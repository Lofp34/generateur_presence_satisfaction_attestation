import pytest
from pathlib import Path
import json

@pytest.fixture
def sample_config():
    """Returns a simplified version of convention_patterns.json"""
    return {
        "required": ["provider_name", "beneficiary_name", "date_start", "date_end", "duration", "action_title"],
        "fields": {
            "provider_name": {
                "labels": ["Entre", "Prestataire :"],
                "patterns": [r"Entre\s+(?P<value>.+?)\s+Ci-après"]
            },
            "beneficiary_name": {
                "labels": ["Client :", "Stagiaire :"],
                "patterns": [r"Client\s*:\s*(?P<value>.+)"]
            }
        }
    }

@pytest.fixture
def sample_settings(sample_config, tmp_path):
    """
    Mock settings object.
    We need to mock convention_config and attestation_layout.
    """
    from app.config import Settings
    
    # Mock files
    settings = Settings(_env_file=None)
    # Monkeypatch properties
    Settings.convention_config = property(lambda self: sample_config)
    
    layout = {
        "template_pdf": "template.pdf",
        "image_width": 1000,
        "image_height": 1000,
        "fields": [
             {"field_id": "beneficiary_name", "bbox": [10, 10, 100, 20], "font_size": 12},
             {"field_id": "checkbox_action_training", "type": "checkbox", "bbox": [200, 200, 220, 220]}
        ]
    }
    Settings.attestation_layout = property(lambda self: layout)
    
    return settings

@pytest.fixture
def sample_attestation_fields():
    return {
        "signatory_name": "Jean Dupont",
        "provider_name": "Formation Plus",
        "beneficiary_name": "Martin Durand",
        "company_name": "Société Exemple",
        "action_title": "Formation Python",
        "checkbox_action_training": "X",
        "date_start": "01/01/2024",
        "date_end": "05/01/2024",
        "duration": "35",
        "location": "Paris",
        "signature_date": "06/01/2024",
    }
