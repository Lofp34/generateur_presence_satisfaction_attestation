from __future__ import annotations

from datetime import datetime
import re


def map_to_attestation_fields(convention_fields: dict[str, str]) -> dict[str, str]:
    signature_date = convention_fields.get("date_end")
    if not signature_date:
        signature_date = datetime.now().strftime("%d/%m/%Y")

    return {
        "signatory_name": convention_fields.get("signatory_name", ""),
        "provider_name": convention_fields.get("provider_name", ""),
        "beneficiary_name": convention_fields.get("beneficiary_name", ""),
        "company_name": convention_fields.get("company_name", ""),
        "action_title": convention_fields.get("action_title", ""),
        "checkbox_action_training": "X",
        "date_start": convention_fields.get("date_start", ""),
        "date_end": convention_fields.get("date_end", ""),
        "duration": convention_fields.get("duration", ""),
        "location": convention_fields.get("location", ""),
        "signature_date": signature_date,
    }


def sanitize_filename(value: str, fallback: str = "beneficiaire") -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in value.strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    if not cleaned:
        cleaned = fallback
    return cleaned[:60]
