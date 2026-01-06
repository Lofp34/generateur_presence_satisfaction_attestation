from __future__ import annotations
import tempfile
from pathlib import Path
import io
import zipfile
from typing import Tuple

from app.config import Settings
from app.schemas import ConventionData
from app.extract_convention import extract_convention_data
from app.generate_attestation import generate_attestation_bytes
from app.utils import map_to_attestation_fields, sanitize_filename

class AttestationService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def process_pdf(self, pdf_content: bytes) -> Tuple[io.BytesIO, str, str]:
        """
        Process the PDF content and return a tuple of (file_stream, filename, media_type).
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_pdf = Path(tmp_dir) / "convention.pdf"
            temp_pdf.write_bytes(pdf_content)

            extracted_fields, participants = extract_convention_data(str(temp_pdf), self.settings.convention_config)
            
            # Validate shared data
            # If we have participants, 'beneficiary_name' is not yet in extracted_fields
            # We temporarily add it to validate the rest of the structure
            validation_data = extracted_fields.copy()
            if participants and "beneficiary_name" not in validation_data:
                validation_data["beneficiary_name"] = participants[0]
            
            # This might raise ValidationError which should be handled by the caller
            ConventionData(**validation_data)

            beneficiaries = participants or [extracted_fields.get("beneficiary_name", "beneficiaire")]
            layout = self.settings.attestation_layout

            if len(beneficiaries) == 1:
                beneficiary = beneficiaries[0]
                fields = dict(extracted_fields)
                fields["beneficiary_name"] = beneficiary
                attestation_fields = map_to_attestation_fields(fields)
                pdf_bytes = generate_attestation_bytes(attestation_fields, layout)
                filename = f"attestation_{sanitize_filename(beneficiary)}.pdf"
                return io.BytesIO(pdf_bytes), filename, "application/pdf"

            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
                for beneficiary in beneficiaries:
                    fields = dict(extracted_fields)
                    fields["beneficiary_name"] = beneficiary
                    attestation_fields = map_to_attestation_fields(fields)
                    pdf_bytes = generate_attestation_bytes(attestation_fields, layout)
                    filename = f"attestation_{sanitize_filename(beneficiary)}.pdf"
                    archive.writestr(filename, pdf_bytes)
            zip_buffer.seek(0)
            return zip_buffer, "attestations.zip", "application/zip"
