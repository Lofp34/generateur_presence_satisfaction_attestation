from unittest.mock import MagicMock, patch
from app.extract_convention import extract_fields, extract_convention_fields

def test_extract_fields_from_text(sample_config):
    text = """
    CONVENTION DE FORMATION
    Entre l'organisme Formation Cool
    Ci-après désigné "Prestataire"
    
    Et :
    Client : Super Client SAS
    """
    
    # Mock finding patterns
    # In extract_fields, it iterates over config fields.
    # provider_name pattern matches "Entre ... Ci-après"
    
    fields = extract_fields(text, sample_config)
    
    assert fields.get("provider_name") == "l'organisme Formation Cool"
    # beneficiary_name labels "Client :" should match "Super Client SAS"
    assert fields.get("beneficiary_name") == "Super Client SAS"

@patch("app.extract_convention.extract_text")
@patch("app.extract_convention.extract_form_fields")
def test_extract_convention_fields_full(mock_form, mock_text, sample_config):
    mock_text.return_value = """
    Convention
    Entre Organisme Test Ci-après
    Client : Stagiaire Test
    formation intitulée : Formation Python
    Dates de formation : 01/01/2024 au 05/01/2024
    Durée de la formation : 35 heures
    """
    mock_form.return_value = {}
    
    fields = extract_convention_fields("dummy.pdf", sample_config)
    
    assert fields["provider_name"] == "Organisme Test"
    assert fields["beneficiary_name"] == "Stagiaire Test"
    assert fields["date_start"] == "01/01/2024"
    assert fields["duration"] == "35"
