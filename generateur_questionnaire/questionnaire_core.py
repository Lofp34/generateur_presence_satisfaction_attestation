import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)


RATING_OPTIONS = ("++", "+", "-", "--")


@dataclass
class QuestionnaireData:
    participant_last_name: str
    participant_first_name: str
    company: str
    training_program: str
    training_center: str
    start_date: str
    end_date: str
    logo_path: str | None = None


def render_questionnaire(data: QuestionnaireData, output_dir: str | Path) -> Path:
    """Generate a satisfaction questionnaire PDF matching the provided sample."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filename = _build_filename(
        data.participant_last_name or data.participant_first_name or "participant",
        data.training_program or "formation",
    )
    pdf_path = output_path / f"Questionnaire_{filename}.pdf"

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    section_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Heading3"],
        fontSize=12,
        leading=15,
        spaceAfter=4,
    )
    body_style = styles["Normal"]

    story = []
    if data.logo_path:
        story.extend(_build_logo_flow(data.logo_path))

    story.append(Paragraph("Questionnaire de satisfaction", title_style))
    story.append(Spacer(1, 0.5 * cm))
    story.append(_build_information_table(data))
    story.append(Spacer(1, 0.4 * cm))

    # Section 1
    story.append(Paragraph("1ère partie : l’organisation de la formation", section_style))
    story.append(Paragraph("Votre avis sur le déroulement de la formation ?", subtitle_style))
    story.append(_rating_table(["Accueil", "Respect des horaires", "Durée", "Logistique, prestations techniques"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Avez-vous des commentaires à faire sur ces points ?", body_style))
    story.append(_text_area(3 * cm))
    story.append(Spacer(1, 0.5 * cm))

    # Section 2
    story.append(Paragraph("2ème partie : le formateur", section_style))
    story.append(Paragraph("Chez le formateur, comment évaluez-vous ?", subtitle_style))
    story.append(_rating_table(["La maîtrise du contenu", "La qualité de l’écoute", "La clarté du message"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Avez-vous des commentaires à faire sur ces points ?", body_style))
    story.append(_text_area(3 * cm))
    story.append(Spacer(1, 0.5 * cm))

    # Section 3
    story.append(Paragraph("3ème partie : l’animation", section_style))
    story.append(Paragraph("Votre avis sur l’animation de la formation ?", subtitle_style))
    story.append(_rating_table(["Les supports", "Les échanges", "La méthode pédagogique", "La durée et le rythme"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Avez-vous des commentaires à faire sur ces points ?", body_style))
    story.append(_text_area(3 * cm))
    story.append(Spacer(1, 0.5 * cm))

    # Section 4
    story.append(Paragraph("4ème partie : les objectifs de la formation", section_style))
    story.append(Paragraph("Selon vous, quels étaient les objectifs de la formation ?", body_style))
    story.append(_text_area(3.5 * cm))
    story.append(Spacer(1, 0.3 * cm))
    story.append(_rating_table(["Adhériez-vous à cet objectif ?", "Vous semble-t-il atteint ?"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Avez-vous des commentaires à faire sur ces points ?", body_style))
    story.append(_text_area(3 * cm))
    story.append(Spacer(1, 0.5 * cm))

    # Conclusion
    story.append(Paragraph("Conclusion", section_style))
    story.append(Paragraph("La formation a-t-elle répondu à vos attentes ?", body_style))
    story.append(_checkbox_list(["Tout à fait", "En grande partie", "A peu près", "Pas du tout"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Note de la formation (sur 10)", body_style))
    story.append(_text_area(1.5 * cm))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Vos suggestions sont les bienvenues :", body_style))
    story.append(_text_area(3.5 * cm))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("Merci d’avoir répondu à ce questionnaire !", body_style))

    doc.build(story)
    return pdf_path


def split_full_name(full_name: str) -> tuple[str, str]:
    """Split a full name into first name and last name."""
    tokens = [tok for tok in full_name.strip().split() if tok]
    if not tokens:
        return "", ""
    if len(tokens) == 1:
        return "", tokens[0]
    first = " ".join(tokens[:-1])
    last = tokens[-1]
    return first, last


def _build_information_table(data: QuestionnaireData) -> Table:
    nom_value = data.participant_last_name.upper() if data.participant_last_name else ""
    prenom_value = data.participant_first_name
    table_data = [
        ["Nom :", nom_value],
        ["Prénom :", prenom_value],
        ["Société :", data.company],
        ["Parcours de formation :", data.training_program],
        ["Centre d’entraînement :", data.training_center],
        ["Date de début :", data.start_date],
        ["Date de fin :", data.end_date],
    ]
    table = Table(table_data, colWidths=[4.5 * cm, 11 * cm])
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def _rating_table(items: Sequence[str]) -> Table:
    data = [[""] + list(RATING_OPTIONS)]
    for label in items:
        data.append([label] + [""] * len(RATING_OPTIONS))
    col_widths = [7.0 * cm] + [2.5 * cm for _ in RATING_OPTIONS]
    row_heights = [0.9 * cm] + [1.1 * cm for _ in items]
    table = Table(data, colWidths=col_widths, rowHeights=row_heights)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (1, 0), (-1, 0), colors.HexColor("#EFEFEF")),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (0, -1), "Helvetica"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ]
        )
    )
    return table


def _checkbox_list(options: Iterable[str]) -> Table:
    styles = getSampleStyleSheet()
    rows = [[Paragraph(f"[ ] {opt}", styles["Normal"])] for opt in options]
    table = Table(rows, colWidths=[15 * cm])
    table.setStyle(
        TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def _text_area(height: float) -> Table:
    table = Table([[""]], colWidths=[15 * cm], rowHeights=[height])
    table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.black)]))
    return table


def _build_logo_flow(logo_path: str):
    flow = []
    path = Path(logo_path)
    if not path.exists():
        return flow
    try:
        img = Image(str(path))
        max_width = 4 * cm
        max_height = 4 * cm
        ratio = min(max_width / img.drawWidth, max_height / img.drawHeight)
        img.drawWidth *= ratio
        img.drawHeight *= ratio
        flow.append(img)
        flow.append(Spacer(1, 0.3 * cm))
    except Exception:
        pass
    return flow


def _build_filename(participant: str, training_program: str) -> str:
    base = f"{participant}_{training_program}"
    normalized = unicodedata.normalize("NFKD", base).encode("ascii", "ignore").decode("ascii")
    normalized = normalized.lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")
    return normalized or "questionnaire"
