import io
import os
import zipfile

import streamlit as st

from generateur_feuilles import create_presence_sheet


st.set_page_config(page_title="Générateur de feuilles de présence", page_icon="📄")
st.title("Générateur de feuilles de présence")
st.caption("Créez des feuilles de présence PDF par académicien et téléchargez-les en ZIP.")


with st.form("presence_form"):
    societe = st.text_input("Société cliente")
    academiciens_str = st.text_input("Académiciens (séparés par des virgules)")
    duree = st.text_input("Durée de la formation")
    lieu = st.text_input("Lieu de formation")
    formation = st.text_input("Nom de la formation")

    submitted = st.form_submit_button("Générer les feuilles")


if submitted:
    academiciens = [a.strip() for a in academiciens_str.split(',') if a.strip()]

    # Validation minimale
    missing = []
    if not societe:
        missing.append("Société")
    if not academiciens:
        missing.append("Académiciens")
    if not duree:
        missing.append("Durée")
    if not lieu:
        missing.append("Lieu")
    if not formation:
        missing.append("Formation")

    if missing:
        st.error("Champs manquants: " + ", ".join(missing))
    else:
        with st.spinner("Génération des feuilles en cours..."):
            output_dir = "feuilles_présence"
            os.makedirs(output_dir, exist_ok=True)

            for nom in academiciens:
                create_presence_sheet(societe, nom, duree, lieu, formation)

            # Préparer le ZIP en mémoire
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for nom in academiciens:
                    file_name = f"Feuille_de_presence_{nom.replace(' ', '_')}.pdf"
                    path = os.path.join(output_dir, file_name)
                    if os.path.exists(path):
                        zf.write(path, arcname=file_name)
            zip_buffer.seek(0)

        st.success("Génération terminée !")
        st.download_button(
            label="Télécharger le ZIP",
            data=zip_buffer,
            file_name="feuilles_presence.zip",
            mime="application/zip"
        )


