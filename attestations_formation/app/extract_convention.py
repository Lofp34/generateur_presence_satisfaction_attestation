from __future__ import annotations

import re
from datetime import datetime
from typing import Iterable

import pdfplumber
from pypdf import PdfReader


def extract_text(pdf_path: str) -> str:
    chunks: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            chunks.append(text)
    return "\n".join(chunks)


def normalize_lines(text: str) -> list[str]:
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    return [line for line in lines if line]


def find_after_label(lines: list[str], labels: Iterable[str]) -> str | None:
    lowered_labels = [label.lower() for label in labels]
    for index, line in enumerate(lines):
        lower_line = line.lower()
        for label in lowered_labels:
            if label in lower_line:
                split = re.split(r":|-", line, maxsplit=1)
                if len(split) == 2 and split[1].strip():
                    return split[1].strip()
                if index + 1 < len(lines):
                    return lines[index + 1].strip()
    return None


def extract_form_fields(pdf_path: str) -> dict[str, str]:
    reader = PdfReader(pdf_path)
    raw_fields = reader.get_fields() or {}
    fields: dict[str, str] = {}
    for name, meta in raw_fields.items():
        value = meta.get("/V") or meta.get("/DV")
        if value is None:
            continue
        fields[name] = str(value)
    return fields


def find_from_form_fields(form_fields: dict[str, str], labels: Iterable[str], patterns: Iterable[str]) -> str | None:
    lowered_labels = [label.lower() for label in labels]
    for name, value in form_fields.items():
        name_lower = name.lower()
        if any(label in name_lower for label in lowered_labels) and value.strip():
            return value.strip()
    for name, value in form_fields.items():
        for pattern in patterns:
            if re.search(pattern, name, flags=re.IGNORECASE):
                if value.strip():
                    return value.strip()
    return None


def extract_fields(text: str, config: dict, form_fields: dict[str, str] | None = None) -> dict[str, str | None]:
    lines = normalize_lines(text)
    fields: dict[str, str | None] = {}
    for field_id, spec in config.get("fields", {}).items():
        value = None
        for pattern in spec.get("patterns", []):
            match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.groupdict().get("value") or match.group(1)
                break
        if not value and spec.get("labels"):
            value = find_after_label(lines, spec["labels"])
        if not value and form_fields is not None:
            value = find_from_form_fields(
                form_fields,
                spec.get("labels", []),
                spec.get("patterns", []),
            )
        if value:
            cleaned = value.strip()
            cleaned = re.sub(r"\s+en\s+qualit[eé]\s+de.*$", "", cleaned, flags=re.IGNORECASE)
            cleaned = cleaned.strip(" .;:")
            fields[field_id] = cleaned
        else:
            fields[field_id] = None
    return fields


def extract_convention_fields(pdf_path: str, config: dict) -> dict[str, str]:
    text = extract_text(pdf_path)
    form_fields = extract_form_fields(pdf_path)
    if not text.strip() and not form_fields:
        raise ValueError("Aucun texte ou champ de formulaire detecte dans le PDF.")
    fields = extract_fields(text, config, form_fields)
    missing = [field for field in config.get("required", []) if not fields.get(field)]
    if missing:
        fixed_fields = extract_fixed_fields(text)
        fields.update({key: value for key, value in fixed_fields.items() if value})
        missing = [field for field in config.get("required", []) if not fields.get(field)]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")
    return {key: value for key, value in fields.items() if value}


def extract_convention_data(pdf_path: str, config: dict) -> tuple[dict[str, str], list[str]]:
    text = extract_text(pdf_path)
    form_fields = extract_form_fields(pdf_path)
    if not text.strip() and not form_fields:
        raise ValueError("Aucun texte ou champ de formulaire detecte dans le PDF.")
    fields = extract_fields(text, config, form_fields)
    fixed_fields = extract_fixed_fields(text)
    participants = extract_participants(text)
    client_contact = extract_client_contact(text)
    for key, value in fixed_fields.items():
        if value:
            fields[key] = value
    if participants:
        fields["beneficiary_name"] = participants[0]
    if not participants and client_contact:
        fields["beneficiary_name"] = client_contact
    missing = [field for field in config.get("required", []) if not fields.get(field)]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")
    return {key: value for key, value in fields.items() if value}, participants


def extract_fixed_fields(text: str) -> dict[str, str | None]:
    fields: dict[str, str | None] = {}
    normalized = text.replace("\r\n", "\n")
    header = normalized.split("Article 1", 1)[0]

    provider_match = re.findall(r"Ci-apr[eè]s d[ée]sign[ée] [«\"]([^»\"]+)[»\"]", header, flags=re.IGNORECASE)
    if provider_match:
        fields["provider_name"] = provider_match[0].strip()

    company_match = re.search(r"Et\s*:\s*([^,\n]+)", header, flags=re.IGNORECASE)
    if company_match:
        fields["company_name"] = company_match.group(1).strip()

    signatory_match = re.search(r"Pour\s+le\s+Prestataire\s*:\s*(?:Nom\s*:\s*)?([^\n]+)", normalized, flags=re.IGNORECASE)
    if signatory_match:
        fields["signatory_name"] = signatory_match.group(1).strip()

    action_match = re.search(r"formation\s+intitul[ée]e\s*:\s*([^\n]+)", normalized, flags=re.IGNORECASE)
    if action_match:
        fields["action_title"] = action_match.group(1).strip()

    duration_match = re.search(r"Dur[eé]e\s+de\s+la\s+formation\s*:\s*([^\n\.]+)", normalized, flags=re.IGNORECASE)
    if duration_match:
        duration = duration_match.group(1).strip()
        duration = re.split(r"\s+soit\s+", duration, flags=re.IGNORECASE)[0].strip()
        duration = re.sub(r"\s+de\s+formation\s+par\s+personne.*$", "", duration, flags=re.IGNORECASE).strip()
        hours_match = re.search(r"(\d+[.,]?\d*)", duration)
        if hours_match:
            fields["duration"] = hours_match.group(1).replace(",", ".")
        else:
            fields["duration"] = duration

    dates_match = re.search(
        r"Dates?\s+de\s+formation\s*:\s*(\d{2}/\d{2}/\d{4})\s+au\s+(\d{2}/\d{2}/\d{4})",
        normalized,
        flags=re.IGNORECASE,
    )
    if dates_match:
        fields["date_start"] = dates_match.group(1)
        fields["date_end"] = dates_match.group(2)

    location_match = re.search(r"Lieu\s+de\s+la\s+formation\s*:\s*([^\n\.]+)", normalized, flags=re.IGNORECASE)
    if location_match:
        fields["location"] = location_match.group(1).strip()

    signature_match = re.search(
        r"Fait\s+en\s+\d+\s+exemplaires?,\s+à\s+([^,\n]+),\s+le\s+(\d{4}-\d{2}-\d{2})",
        normalized,
        flags=re.IGNORECASE,
    )
    if signature_match:
        fields["location"] = signature_match.group(1).strip()
        fields["signature_date"] = format_date(signature_match.group(2))

    return fields


def extract_participants(text: str) -> list[str]:
    normalized = text.replace("\r\n", "\n")
    match = re.search(r"Article\s+3\s+[–-]\s+Participants(.*?)(Article\s+4|$)", normalized, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return []
    block = match.group(1)
    names: list[str] = []
    for line in block.splitlines():
        if "•" not in line and "Participants" not in line:
            continue
        if "•" in line:
            line = line.split("•", 1)[1]
        line = line.strip(" .;:")
        if not line:
            continue
        parts = re.split(r",|;|\\s+et\\s+", line, flags=re.IGNORECASE)
        for part in parts:
            candidate = part.strip()
            if candidate and len(candidate.split()) >= 2:
                names.append(candidate)
    filtered = [name for name in names if len(name) <= 60]
    return filtered


def extract_client_contact(text: str) -> str | None:
    normalized = text.replace("\r\n", "\n")
    match = re.search(r"Pour\s+le\s+Client\s*:\s*(?:Nom\s*:\s*)?([^\n]+)", normalized, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None
    return names


def format_date(value: str) -> str:
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt).strftime("%d/%m/%Y")
        except ValueError:
            continue
    return value
