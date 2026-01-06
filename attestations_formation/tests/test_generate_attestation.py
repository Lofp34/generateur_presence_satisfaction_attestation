import io
from unittest.mock import MagicMock, patch
from app.generate_attestation import generate_attestation_bytes

@patch("app.generate_attestation.PdfReader")
@patch("app.generate_attestation.PdfWriter")
@patch("app.generate_attestation.canvas.Canvas")
def test_generate_attestation_bytes_structure(mock_canvas, mock_writer, mock_reader, sample_attestation_fields):
    # Mock layout
    layout = {
        "template_pdf": "template.pdf",
        "image_width": 1000,
        "image_height": 1000,
        "fields": [
            {"field_id": "beneficiary_name", "bbox": [10, 10, 100, 20], "font_size": 12},
            {"field_id": "checkbox_action_training", "type": "checkbox", "bbox": [200, 200, 220, 220]}
        ]
    }

    # Setup mocks
    mock_writer_instance = mock_writer.return_value
    mock_output = io.BytesIO(b"%PDF-1.4 mock content")
    
    def write_side_effect(output_stream):
        output_stream.write(b"%PDF-1.4 mock content")
    
    mock_writer_instance.write.side_effect = write_side_effect
    
    # Mock Reader pages
    mock_page = MagicMock()
    mock_page.mediabox.width = 500
    mock_page.mediabox.height = 800
    mock_reader.return_value.pages = [mock_page]

    pdf_bytes = generate_attestation_bytes(sample_attestation_fields, layout)
    
    assert pdf_bytes.startswith(b"%PDF")
    mock_canvas.assert_called()
