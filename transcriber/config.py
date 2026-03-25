from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class AppSettings:
    language: str = "ru"
    theme: str = "dark"
    primary_api_key: str = ""
    use_multiple_keys: bool = False
    extra_api_keys: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AppConfig:
    upload_folder: Path
    result_folder: Path
    settings_path: Path
    words_per_line: int = 100
    poll_interval_seconds: int = 1
    transcription_timeout_seconds: int = 86400


def _normalize_settings(raw: dict, fallback_api_key: str) -> AppSettings:
    language = str(raw.get("language", "ru")).lower()
    if language not in {"ru", "en"}:
        language = "ru"

    theme = str(raw.get("theme", "dark")).lower()
    if theme not in {"dark", "light", "system"}:
        theme = "dark"

    primary_api_key = str(raw.get("primary_api_key", "")).strip()
    if not primary_api_key:
        primary_api_key = fallback_api_key

    use_multiple_keys = bool(raw.get("use_multiple_keys", False))
    raw_keys = raw.get("extra_api_keys", [])
    extra_api_keys: list[str] = []
    if isinstance(raw_keys, list):
        for item in raw_keys:
            key = str(item).strip()
            if key and key not in extra_api_keys:
                extra_api_keys.append(key)

    return AppSettings(
        language=language,
        theme=theme,
        primary_api_key=primary_api_key,
        use_multiple_keys=use_multiple_keys,
        extra_api_keys=extra_api_keys,
    )


def _read_env_api_key(base_dir: Path) -> str:
    api_key = os.getenv("ASSEMBLYAI_API_KEY", "").strip()
    if api_key:
        return api_key

    env_file = base_dir / ".env"
    if not env_file.exists():
        return ""

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() == "ASSEMBLYAI_API_KEY":
            return value.strip().strip("\"'")
    return ""


def load_config() -> tuple[AppConfig, AppSettings]:
    base_dir = Path(__file__).resolve().parents[1]
    upload_folder = base_dir / "uploads"
    result_folder = base_dir / "results"
    settings_path = base_dir / "app_settings.json"

    upload_folder.mkdir(parents=True, exist_ok=True)
    result_folder.mkdir(parents=True, exist_ok=True)

    fallback_api_key = _read_env_api_key(base_dir)
    settings = AppSettings(primary_api_key=fallback_api_key)

    if settings_path.exists():
        try:
            raw = json.loads(settings_path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                settings = _normalize_settings(raw, fallback_api_key=fallback_api_key)
        except (json.JSONDecodeError, OSError):
            settings = AppSettings(primary_api_key=fallback_api_key)

    config = AppConfig(
        upload_folder=upload_folder,
        result_folder=result_folder,
        settings_path=settings_path,
    )
    return config, settings


def save_settings(path: Path, settings: AppSettings) -> None:
    payload = asdict(settings)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
