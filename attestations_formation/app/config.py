from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
import json

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"

class Settings(BaseSettings):
    base_dir: Path = BASE_DIR
    config_dir: Path = CONFIG_DIR
    convention_patterns_file: Path = CONFIG_DIR / "convention_patterns.json"
    attestation_layout_file: Path = CONFIG_DIR / "attestation_layout.json"

    @property
    def convention_config(self) -> dict:
        with self.convention_patterns_file.open("r", encoding="utf-8") as f:
            return json.load(f)

    @property
    def attestation_layout(self) -> dict:
        layout = self._load_json(self.attestation_layout_file)
        # Resolve absolute path for template if necessary
        template_path = Path(layout["template_pdf"])
        if not template_path.is_absolute():
            layout["template_pdf"] = str(self.base_dir / template_path)
        return layout

    def _load_json(self, path: Path) -> dict:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

def get_settings() -> Settings:
    return Settings()
