import io
import tempfile
import zipfile
from pathlib import Path

import streamlit as st

from questionnaire_core import QuestionnaireData, render_questionnaire, split_full_name


DEFAULT_OUTPUT_DIR = Path("generateur_questionnaire/questionnaires_satisfaction")


def _extract_participants(raw_value: str) -> list[str]:
    tokens = [item.strip() for item in raw_value.replace(",", "\n").splitlines()]
    return [token for token in tokens if token]


def _collect_missing(
    company: str,
    training_program: str,
    training_center: str,
    start_date: str,
    end_date: str,
    participants: list[str],
) -> list[str]:
    missing = []
    if not company:
        missing.append("Société")
    if not training_program:
        missing.append("Parcours de formation")
    if not training_center:
        missing.append("Centre d'entraînement")
    if not start_date:
        missing.append("Date de début")
    if not end_date:
        missing.append("Date de fin")
    if not participants:
        missing.append("Participants")
    return missing


def _build_zip_buffer(paths: list[Path]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in paths:
            archive.write(file_path, arcname=file_path.name)
    buffer.seek(0)
    return buffer.read()


st.set_page_config(page_title="Questionnaires de satisfaction", page_icon="✅")
st.title("Générateur de questionnaires de satisfaction")
st.caption("Entrez les informations de la formation et récupérez un PDF par participant.")


with st.form("questionnaire_form"):
    company = st.text_input("Société cliente")
    training_program = st.text_input("Parcours de formation")
    training_center = st.text_input("Centre d'entraînement")

    col_dates = st.columns(2)
    with col_dates[0]:
        start_date = st.text_input("Date de début")
    with col_dates[1]:
        end_date = st.text_input("Date de fin")

    participants_raw = st.text_area(
        "Participants (un nom par ligne ou séparé par des virgules)",
        placeholder="Alice Dupont\nBob Martin\nCharlie Durand",
        height=140,
    )

    logo_file = st.file_uploader(
        "Logo (optionnel)",
        type=["png", "jpg", "jpeg"],
        help="Le logo sera affiché dans l'en-tête de chaque questionnaire.",
    )

    submitted = st.form_submit_button("Générer les questionnaires")


if submitted:
    participants = _extract_participants(participants_raw)
    missing = _collect_missing(
        company, training_program, training_center, start_date, end_date, participants
    )

    if missing:
        st.error("Champs manquants : " + ", ".join(missing))
    else:
        generated_paths = []
        DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmpdir:
            logo_path = None
            if logo_file:
                tmp_file = Path(tmpdir) / logo_file.name
                tmp_file.write_bytes(logo_file.getvalue())
                logo_path = str(tmp_file)

            with st.spinner("Génération des PDF en cours..."):
                for participant in participants:
                    first_name, last_name = split_full_name(participant)
                    data = QuestionnaireData(
                        participant_last_name=last_name,
                        participant_first_name=first_name,
                        company=company,
                        training_program=training_program,
                        training_center=training_center,
                        start_date=start_date,
                        end_date=end_date,
                        logo_path=logo_path,
                    )
                    pdf_path = render_questionnaire(data, DEFAULT_OUTPUT_DIR)
                    generated_paths.append(pdf_path)

        if generated_paths:
            zip_bytes = _build_zip_buffer(generated_paths)
            st.success(f"{len(generated_paths)} questionnaire(s) généré(s).")
            st.download_button(
                label="Télécharger le ZIP",
                data=zip_bytes,
                file_name="questionnaires_satisfaction.zip",
                mime="application/zip",
            )
        else:
            st.warning("Aucun questionnaire n'a été généré.")
