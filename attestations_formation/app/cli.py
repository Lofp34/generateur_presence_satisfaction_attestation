from __future__ import annotations

import argparse
from pathlib import Path

import zipfile

from app.config import load_attestation_layout, load_convention_config
from app.extract_convention import extract_convention_data, extract_form_fields, extract_text
from app.generate_attestation import generate_attestation
from app.utils import map_to_attestation_fields, sanitize_filename


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate attestation from a convention PDF.")
    parser.add_argument("pdf", help="Path to the convention PDF")
    parser.add_argument("--output", default="certificats_output/attestation.pdf", help="Output PDF path")
    parser.add_argument("--debug", action="store_true", help="Print extracted text and form fields")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    output_path = Path(args.output)

    if args.debug:
        text = extract_text(str(pdf_path))
        form_fields = extract_form_fields(str(pdf_path))
        print("---- DEBUG TEXT (first 800 chars) ----")
        print(text[:800] if text else "[no text extracted]")
        print("---- DEBUG FORM FIELDS ----")
        if not form_fields:
            print("[no form fields detected]")
        else:
            for name, value in sorted(form_fields.items()):
                print(f"{name} = {value}")
        return

    convention_config = load_convention_config()
    extracted_fields, participants = extract_convention_data(str(pdf_path), convention_config)
    layout = load_attestation_layout()

    files: list[Path] = []
    beneficiaries = participants or [extracted_fields.get("beneficiary_name", "beneficiaire")]
    for beneficiary in beneficiaries:
        fields = dict(extracted_fields)
        fields["beneficiary_name"] = beneficiary
        attestation_fields = map_to_attestation_fields(fields)
        safe_name = sanitize_filename(beneficiary)
        output_file = output_path.with_name(f"{output_path.stem}_{safe_name}.pdf")
        generate_attestation(attestation_fields, layout, output_file)
        files.append(output_file)

    if len(files) == 1:
        print(f"Attestation generated at {files[0]}")
        return

    zip_path = output_path.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for pdf in files:
            archive.write(pdf, arcname=pdf.name)
    print(f"{len(files)} attestations generated, zip saved at {zip_path}")


if __name__ == "__main__":
    main()
