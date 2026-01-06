from __future__ import annotations

import io
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas


def _map_bbox_to_pdf(bbox: list[int], image_width: int, image_height: int, page_width: float, page_height: float, y_offset: int = 0) -> tuple[float, float]:
    left, top, right, bottom = bbox
    x = left / image_width * page_width
    y_center = (top + bottom) / 2 + y_offset
    y = page_height - (y_center / image_height * page_height)
    return x, y


def _draw_text(c: canvas.Canvas, text: str, x: float, y: float, font_size: int) -> None:
    c.setFont("Helvetica", font_size)
    c.drawString(x, y, text)


def _draw_checkbox(c: canvas.Canvas, x: float, y: float, font_size: int) -> None:
    c.setFont("Helvetica", font_size)
    c.drawString(x, y, "X")


def generate_attestation_bytes(fields: dict[str, str], layout: dict) -> bytes:
    template_path = Path(layout["template_pdf"])
    # Template path resolution is now handled by config settings
    reader = PdfReader(str(template_path))
    writer = PdfWriter()

    image_width = layout["image_width"]
    image_height = layout["image_height"]

    for page_index, page in enumerate(reader.pages):
        packet = io.BytesIO()
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)
        c = canvas.Canvas(packet, pagesize=(page_width, page_height))

        for entry in layout["fields"]:
            field_id = entry["field_id"]
            value = fields.get(field_id)
            if entry.get("type") == "checkbox":
                value = "X" if value else ""
            if not value:
                continue
            x, y = _map_bbox_to_pdf(
                entry["bbox"],
                image_width,
                image_height,
                page_width,
                page_height,
                entry.get("y_offset", 0),
            )
            if entry.get("type") == "checkbox":
                _draw_checkbox(c, x, y, entry.get("font_size", 12))
            else:
                _draw_text(c, str(value), x, y, entry.get("font_size", 12))

        c.save()
        packet.seek(0)
        overlay = PdfReader(packet)
        page.merge_page(overlay.pages[0])
        writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def generate_attestation(fields: dict[str, str], layout: dict, output_path: Path) -> None:
    data = generate_attestation_bytes(fields, layout)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(data)
