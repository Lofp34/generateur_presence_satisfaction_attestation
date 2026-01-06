import io
import os
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

import streamlit as st

from generateur_feuilles import create_presence_sheet

sys.path.append(str(Path(__file__).parent / "generateur_questionnaire"))
from questionnaire_core import QuestionnaireData, render_questionnaire, split_full_name  # noqa: E402

attestation_root = Path(__file__).parent / "attestations_formation"
ATTESTATION_AVAILABLE = False
ATTESTATION_ERROR: str | None = None
if attestation_root.exists():
    sys.path.insert(0, str(attestation_root))
    try:
        from app.config import get_settings  # noqa: E402
        from app.generate_attestation import generate_attestation  # noqa: E402
        from app.utils import map_to_attestation_fields, sanitize_filename  # noqa: E402
        ATTESTATION_AVAILABLE = True
    except ModuleNotFoundError as exc:
        try:
            import importlib

            sys.path.insert(0, str(attestation_root / "app"))
            config_module = importlib.import_module("config")
            generator_module = importlib.import_module("generate_attestation")
            utils_module = importlib.import_module("utils")

            get_settings = config_module.get_settings
            generate_attestation = generator_module.generate_attestation
            map_to_attestation_fields = utils_module.map_to_attestation_fields
            sanitize_filename = utils_module.sanitize_filename
            ATTESTATION_AVAILABLE = True
        except Exception as fallback_exc:
            ATTESTATION_ERROR = f"{exc} | fallback: {fallback_exc}"
            ATTESTATION_AVAILABLE = False


st.set_page_config(page_title="Générateur de documents formation", page_icon="🧾")

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@500;700&family=Work+Sans:wght@300;400;500;600&display=swap');

        :root {
            --ink: #111319;
            --paper: #f6f3ed;
            --accent: #c05b3a;
            --accent-2: #2d5c6b;
            --edge: rgba(17, 19, 25, 0.08);
        }

        html, body, [class*="css"]  {
            font-family: "Work Sans", sans-serif;
            color: var(--ink);
        }

        .stApp {
            background: radial-gradient(circle at top left, #f9efe2 0%, #f6f3ed 45%, #f1f3f1 100%);
        }

        .hero {
            padding: 2.2rem 2.6rem 1.6rem;
            border: 1px solid var(--edge);
            border-radius: 28px;
            background: linear-gradient(140deg, rgba(255,255,255,0.85), rgba(249,232,219,0.75));
            box-shadow: 0 12px 40px rgba(17, 19, 25, 0.12);
            margin-bottom: 1.6rem;
        }

        .hero h1 {
            font-family: "Fraunces", serif;
            font-size: 2.3rem;
            margin-bottom: 0.5rem;
        }

        .hero p {
            font-size: 1.02rem;
            color: #343842;
            margin: 0;
        }

        .section-title {
            font-family: "Fraunces", serif;
            font-size: 1.15rem;
            letter-spacing: 0.02em;
            text-transform: uppercase;
            margin: 0.4rem 0 0.9rem;
        }

        div[data-testid="stForm"] {
            border-radius: 24px;
            border: 1px solid var(--edge);
            padding: 1.6rem 1.8rem;
            background: rgba(255, 255, 255, 0.82);
            box-shadow: 0 10px 24px rgba(17, 19, 25, 0.08);
        }

        .stButton > button {
            background: var(--ink);
            color: #fff;
            border-radius: 999px;
            padding: 0.65rem 1.4rem;
            border: none;
            font-weight: 600;
        }

        .stButton > button:hover {
            background: #1f232c;
            color: #fff;
            border: none;
        }

        label, .stMarkdown, .stCaption, .stTextInput label, .stTextArea label, .stFileUploader label {
            color: var(--ink) !important;
        }

        input, textarea {
            color: var(--ink) !important;
            background-color: #fffdf9 !important;
        }

        input::placeholder, textarea::placeholder {
            color: rgba(17, 19, 25, 0.45) !important;
        }

        .stTextInput, .stTextArea, .stFileUploader {
            background-color: transparent;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>Studio de documents formation</h1>
        <p>Un seul formulaire pour générer vos feuilles de présence et vos questionnaires de satisfaction, réunis dans un ZIP unique.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


def _extract_participants(raw_value: str) -> list[str]:
    tokens = [item.strip() for item in raw_value.replace(",", "\n").splitlines()]
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


def _extract_dates(raw_value: str) -> list[str]:
    tokens = [item.strip() for item in raw_value.replace(",", "\n").splitlines()]
    return [token for token in tokens if token]


def _normalize_dates(raw_dates: list[str]) -> list[str]:
    normalized = []
    for raw in raw_dates:
        parsed = _parse_date(raw)
        if parsed:
            normalized.append(parsed.strftime("%d/%m/%Y"))
        else:
            normalized.append(raw.strip())
    return normalized


def _collect_missing(
    societe: str,
    participants: list[str],
    duree: str,
    lieu: str,
    formation: str,
    dates_raw: str,
) -> list[str]:
    missing = []
    if not societe:
        missing.append("Société")
    if not participants:
        missing.append("Participants")
    if not duree:
        missing.append("Durée")
    if not lieu:
        missing.append("Lieu")
    if not formation:
        missing.append("Formation")
    if not dates_raw:
        missing.append("Dates de formation")
    return missing


def _build_zip_buffer(entries: list[tuple[Path, str]]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path, arcname in entries:
            if file_path.exists():
                archive.write(file_path, arcname=arcname)
    buffer.seek(0)
    return buffer.read()


with st.form("presence_form"):
    st.markdown("<p class='section-title'>Informations formation</p>", unsafe_allow_html=True)
    societe = st.text_input("Société cliente")
    formation = st.text_input("Nom de la formation")

    cols = st.columns(2)
    with cols[0]:
        duree = st.text_input("Durée de la formation")
    with cols[1]:
        lieu = st.text_input("Lieu de formation")

    dates_raw = st.text_area(
        "Dates de formation (un jour par ligne ou séparé par des virgules)",
        placeholder="18/12/2025\n19/12/2025\n20/12/2025",
        height=120,
    )

    st.markdown("<p class='section-title'>Participants</p>", unsafe_allow_html=True)
    participants_raw = st.text_area(
        "Académiciens / Participants (un nom par ligne ou séparé par des virgules)",
        placeholder="Alice Dupont\nBob Martin\nCharlie Durand",
        height=140,
    )

    st.markdown("<p class='section-title'>Attestation de formation</p>", unsafe_allow_html=True)
    provider_name = st.text_input(
        "Organisme de formation",
        value="Laurent-Serre-Développement",
        disabled=not ATTESTATION_AVAILABLE,
    )
    signatory_name = st.text_input(
        "Signataire",
        value="Laurent Serre",
        disabled=not ATTESTATION_AVAILABLE,
    )

    st.markdown("<p class='section-title'>Option visuelle</p>", unsafe_allow_html=True)
    logo_file = st.file_uploader(
        "Logo pour le questionnaire (optionnel)",
        type=["png", "jpg", "jpeg"],
    )

    submitted = st.form_submit_button("Générer le ZIP combiné")


if submitted:
    participants = _extract_participants(participants_raw)
    missing = _collect_missing(
        societe, participants, duree, lieu, formation, dates_raw
    )

    if missing:
        st.error("Champs manquants : " + ", ".join(missing))
    else:
        if not ATTESTATION_AVAILABLE:
            message = (
                "Module d'attestations introuvable. Ajoutez le dossier "
                "`attestations_formation/` avec son sous-dossier `app/` dans le projet."
            )
            if ATTESTATION_ERROR:
                message = f"{message}\n\nDétail technique : {ATTESTATION_ERROR}"
            st.error(message)
            st.stop()
        dates_list = _normalize_dates(_extract_dates(dates_raw))
        if not dates_list:
            st.warning(
                "Les dates n'ont pas été reconnues. Les feuilles de présence seront générées avec 16 lignes vides."
            )

        with st.spinner("Génération des documents en cours..."):
            presence_output_dir = Path("feuilles_présence")
            questionnaire_output_dir = Path("generateur_questionnaire/questionnaires_satisfaction")
            attestation_output_dir = Path("attestations_formation/certificats_output")
            presence_output_dir.mkdir(parents=True, exist_ok=True)
            questionnaire_output_dir.mkdir(parents=True, exist_ok=True)
            attestation_output_dir.mkdir(parents=True, exist_ok=True)

            zip_entries: list[tuple[Path, str]] = []

            settings = get_settings()
            attestation_layout = settings.attestation_layout

            parsed_dates = [d for d in (_parse_date(date) for date in dates_list) if d]
            parsed_dates.sort()
            questionnaire_start = (
                parsed_dates[0].strftime("%d/%m/%Y") if parsed_dates else ""
            )
            questionnaire_end = (
                parsed_dates[-1].strftime("%d/%m/%Y") if parsed_dates else ""
            )
            attestation_start = questionnaire_start or (dates_list[0] if dates_list else "")
            attestation_end = questionnaire_end or (dates_list[-1] if dates_list else "")

            with tempfile.TemporaryDirectory() as tmpdir:
                logo_path = None
                if logo_file:
                    tmp_file = Path(tmpdir) / logo_file.name
                    tmp_file.write_bytes(logo_file.getvalue())
                    logo_path = str(tmp_file)

                for participant in participants:
                    create_presence_sheet(
                        societe,
                        participant,
                        duree,
                        lieu,
                        formation,
                        dates=dates_list if dates_list else None,
                    )

                    first_name, last_name = split_full_name(participant)
                    data = QuestionnaireData(
                        participant_last_name=last_name,
                        participant_first_name=first_name,
                        company=societe,
                        training_program=formation,
                        training_center=lieu,
                        start_date=questionnaire_start,
                        end_date=questionnaire_end,
                        logo_path=logo_path,
                    )
                    questionnaire_path = render_questionnaire(data, questionnaire_output_dir)

                    attestation_fields = map_to_attestation_fields(
                        {
                            "signatory_name": signatory_name,
                            "provider_name": provider_name,
                            "beneficiary_name": participant,
                            "company_name": societe,
                            "action_title": formation,
                            "date_start": attestation_start,
                            "date_end": attestation_end,
                            "duration": duree,
                            "location": lieu,
                        }
                    )
                    attestation_name = f"attestation_{sanitize_filename(participant)}.pdf"
                    attestation_path = attestation_output_dir / attestation_name
                    generate_attestation(attestation_fields, attestation_layout, attestation_path)

                    presence_file = presence_output_dir / f"Feuille_de_presence_{participant.replace(' ', '_')}.pdf"
                    zip_entries.append(
                        (presence_file, f"feuilles_presence/{presence_file.name}")
                    )
                    zip_entries.append(
                        (questionnaire_path, f"questionnaires_satisfaction/{questionnaire_path.name}")
                    )
                    zip_entries.append(
                        (attestation_path, f"attestations_formation/{attestation_path.name}")
                    )

            zip_bytes = _build_zip_buffer(zip_entries)

        st.success("Génération terminée !")
        st.download_button(
            label="Télécharger le ZIP combiné",
            data=zip_bytes,
            file_name="documents_formation.zip",
            mime="application/zip",
        )
