from app.schemas import ConventionData
import pytest
from pydantic import ValidationError

def test_convention_data_valid():
    data = {
        "provider_name": "Provider",
        "beneficiary_name": "Beneficiary",
        "date_start": "01/01/2024",
        "date_end": "05/01/2024",
        "duration": "35",
        "action_title": "Training"
    }
    model = ConventionData(**data)
    assert model.provider_name == "Provider"

def test_convention_data_invalid_date():
    data = {
        "provider_name": "Provider",
        "beneficiary_name": "Beneficiary",
        "date_start": "2024-01-01", # Invalid format
        "date_end": "05/01/2024",
        "duration": "35",
        "action_title": "Training"
    }
    with pytest.raises(ValidationError) as exc:
        ConventionData(**data)
    assert "Date format must be DD/MM/YYYY" in str(exc.value)

def test_convention_data_missing_field():
    data = {
        "provider_name": "Provider",
        # Missing beneficiary_name
        "date_start": "01/01/2024",
        "date_end": "05/01/2024",
        "duration": "35",
        "action_title": "Training"
    }
    with pytest.raises(ValidationError):
        ConventionData(**data)
