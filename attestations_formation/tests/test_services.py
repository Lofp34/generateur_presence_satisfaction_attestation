import pytest
from unittest.mock import MagicMock, patch
import io
from app.services import AttestationService

@patch("app.services.extract_convention_data")
@patch("app.services.generate_attestation_bytes")
def test_process_pdf_single_beneficiary(mock_generate, mock_extract, sample_settings, sample_attestation_fields):
    # Setup service
    service = AttestationService(sample_settings)
    
    # Mock extraction
    extracted = {
        "provider_name": "Provider",
        "beneficiary_name": "John Doe",
        "date_start": "01/01/2024",
        "date_end": "05/01/2024",
        "duration": "35",
        "action_title": "Python Basics"
    }
    mock_extract.return_value = (extracted, [])
    
    # Mock generating bytes
    mock_generate.return_value = b"%PDF-1.4..."

    # Call
    file_stream, filename, media_type = service.process_pdf(b"fake pdf content")
    
    assert filename == "attestation_John_Doe.pdf"
    assert media_type == "application/pdf"
    assert file_stream.getvalue() == b"%PDF-1.4..."

@patch("app.services.extract_convention_data")
@patch("app.services.generate_attestation_bytes")
def test_process_pdf_multiple_participants(mock_generate, mock_extract, sample_settings):
    service = AttestationService(sample_settings)
    
    extracted = {
        "provider_name": "Provider",
        "date_start": "01/01/2024",
        "date_end": "05/01/2024",
        "duration": "35",
        "action_title": "Python Basics"
    }
    participants = ["Alice", "Bob"]
    mock_extract.return_value = (extracted, participants)
    
    mock_generate.return_value = b"%PDF..."
    
    file_stream, filename, media_type = service.process_pdf(b"content")
    
    assert filename == "attestations.zip"
    assert media_type == "application/zip"
