from app.utils import map_to_attestation_fields, sanitize_filename
from datetime import datetime

def test_sanitize_filename():
    assert sanitize_filename("Jean-Paul S@rtre") == "Jean-Paul_S_rtre"
    assert sanitize_filename("   M@rtin   ") == "M_rtin"
    assert sanitize_filename("") == "beneficiaire"

def test_map_to_attestation_fields():
    input_fields = {
        "signatory_name": "Manager",
        "provider_name": "School",
        "beneficiary_name": "Student",
        "date_end": "31/12/2023"
    }
    mapped = map_to_attestation_fields(input_fields)
    
    assert mapped["signatory_name"] == "Manager"
    assert mapped["checkbox_action_training"] == "X"
    assert mapped["signature_date"] == "31/12/2023"

def test_map_to_attestation_fields_no_date():
    input_fields = {
        "beneficiary_name": "Student"
    }
    mapped = map_to_attestation_fields(input_fields)
    # Should fallback to current date
    assert mapped["signature_date"] == datetime.now().strftime("%d/%m/%Y")
