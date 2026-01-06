import cgi
import io
import json
import sys
import tempfile
import zipfile
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "generateur_questionnaire"))
sys.path.insert(0, str(ROOT / "attestations_formation"))

from generateur_feuilles import create_presence_sheet  # noqa: E402
from questionnaire_core import QuestionnaireData, render_questionnaire, split_full_name  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.generate_attestation import generate_attestation  # noqa: E402
from app.utils import map_to_attestation_fields, sanitize_filename  # noqa: E402


def _extract_lines(value: str) -> list[str]:
    tokens = [item.strip() for item in value.replace(",", "\n").splitlines()]
    return [token for token in tokens if token]


def _parse_date(raw_value: str) -> datetime | None:
    if not raw_value:
        return None
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw_value.strip(), fmt)
        except ValueError:
            continue
    return None


def _normalize_dates(raw_dates: list[str]) -> list[str]:
    normalized = []
    for raw in raw_dates:
        parsed = _parse_date(raw)
        if parsed:
            normalized.append(parsed.strftime("%d/%m/%Y"))
        else:
            normalized.append(raw.strip())
    return normalized


def _select_date_bounds(dates_list: list[str]) -> tuple[str, str]:
    first = ""
    last = ""
    for value in dates_list:
        parsed = _parse_date(value)
        if parsed:
            formatted = parsed.strftime("%d/%m/%Y")
            if not first:
                first = formatted
            last = formatted
        else:
            if not first:
                first = value
            last = value
    return first, last


def _send_text(handler: BaseHTTPRequestHandler, status: int, message: str) -> None:
    handler.send_response(status)
    handler.send_header("Content-Type", "text/plain; charset=utf-8")
    handler.end_headers()
    handler.wfile.write(message.encode("utf-8"))


class handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        _send_text(self, 200, "OK")

    def do_POST(self) -> None:
        content_type = self.headers.get("Content-Type")
        if not content_type:
            _send_text(self, 400, "Missing Content-Type header.")
            return

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": content_type},
        )

        if "data" not in form:
            _send_text(self, 400, "Missing data payload.")
            return

        try:
            payload = json.loads(form["data"].value)
        except json.JSONDecodeError:
            _send_text(self, 400, "Invalid JSON payload.")
            return

        company = (payload.get("company") or "").strip()
        training = (payload.get("training") or "").strip()
        duration = (payload.get("duration") or "").strip()
        location = (payload.get("location") or "").strip()
        dates_raw = payload.get("dates") or ""
        participants_raw = payload.get("participants") or ""
        provider = (payload.get("provider") or "Laurent-Serre-Developpement").strip()
        signatory = (payload.get("signatory") or "Laurent Serre").strip()

        participants = _extract_lines(participants_raw)
        if not all([company, training, duration, location, dates_raw, participants]):
            _send_text(self, 400, "Missing required fields.")
            return

        dates_list = _normalize_dates(_extract_lines(dates_raw))
        questionnaire_start, questionnaire_end = _select_date_bounds(dates_list)
        attestation_start = questionnaire_start or (dates_list[0] if dates_list else "")
        attestation_end = questionnaire_end or (dates_list[-1] if dates_list else "")

        logo_file = form["logo"] if "logo" in form else None
        settings = get_settings()
        attestation_layout = settings.attestation_layout

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            presence_output_dir = tmp_path / "feuilles_presence"
            questionnaire_output_dir = tmp_path / "questionnaires_satisfaction"
            attestation_output_dir = tmp_path / "attestations_formation"
            presence_output_dir.mkdir(parents=True, exist_ok=True)
            questionnaire_output_dir.mkdir(parents=True, exist_ok=True)
            attestation_output_dir.mkdir(parents=True, exist_ok=True)

            logo_path = None
            if logo_file is not None and getattr(logo_file, "file", None):
                logo_path = str(tmp_path / logo_file.filename)
                with open(logo_path, "wb") as handle:
                    handle.write(logo_file.file.read())

            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
                for participant in participants:
                    create_presence_sheet(
                        company,
                        participant,
                        duration,
                        location,
                        training,
                        dates=dates_list if dates_list else None,
                        output_dir=presence_output_dir,
                    )

                    first_name, last_name = split_full_name(participant)
                    data = QuestionnaireData(
                        participant_last_name=last_name,
                        participant_first_name=first_name,
                        company=company,
                        training_program=training,
                        training_center=location,
                        start_date=questionnaire_start,
                        end_date=questionnaire_end,
                        logo_path=logo_path,
                    )
                    questionnaire_path = render_questionnaire(data, questionnaire_output_dir)

                    attestation_fields = map_to_attestation_fields(
                        {
                            "signatory_name": signatory,
                            "provider_name": provider,
                            "beneficiary_name": participant,
                            "company_name": company,
                            "action_title": training,
                            "date_start": attestation_start,
                            "date_end": attestation_end,
                            "duration": duration,
                            "location": location,
                        }
                    )
                    attestation_name = f"attestation_{sanitize_filename(participant)}.pdf"
                    attestation_path = attestation_output_dir / attestation_name
                    generate_attestation(attestation_fields, attestation_layout, attestation_path)

                    presence_file = (
                        presence_output_dir / f"Feuille_de_presence_{participant.replace(' ', '_')}.pdf"
                    )
                    if presence_file.exists():
                        archive.write(
                            presence_file, arcname=f"feuilles_presence/{presence_file.name}"
                        )
                    if questionnaire_path.exists():
                        archive.write(
                            questionnaire_path,
                            arcname=f"questionnaires_satisfaction/{questionnaire_path.name}",
                        )
                    if attestation_path.exists():
                        archive.write(
                            attestation_path,
                            arcname=f"attestations_formation/{attestation_path.name}",
                        )

            zip_bytes = zip_buffer.getvalue()

        self.send_response(200)
        self.send_header("Content-Type", "application/zip")
        self.send_header(
            "Content-Disposition", 'attachment; filename="documents_formation.zip"'
        )
        self.send_header("Content-Length", str(len(zip_bytes)))
        self.end_headers()
        self.wfile.write(zip_bytes)
