from __future__ import annotations

import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, HTTPError, SSLError
from urllib3.util.retry import Retry


StatusCallback = Callable[[str], None]
KeyInfoCallback = Callable[[int, int], None]


@dataclass
class TranscriptResult:
    text: str
    language_code: str


class ApiKeySelector:
    def __init__(self, api_keys: list[str], use_multiple_keys: bool) -> None:
        sanitized = [key.strip() for key in api_keys if key and key.strip()]
        unique_keys: list[str] = []
        for key in sanitized:
            if key not in unique_keys:
                unique_keys.append(key)
        self._api_keys = unique_keys
        self._use_multiple_keys = use_multiple_keys
        self._last_key: str | None = None

    def has_keys(self) -> bool:
        return bool(self._api_keys)

    def all_keys(self) -> list[str]:
        return list(self._api_keys)

    def total(self) -> int:
        return len(self._api_keys)

    def index_of(self, key: str) -> int:
        return self._api_keys.index(key) + 1

    def pick(self, exclude: set[str] | None = None) -> str:
        if not self._api_keys:
            raise RuntimeError("РќРµ Р·Р°РґР°РЅ API РєР»СЋС‡ AssemblyAI")

        excluded = exclude or set()
        allowed = [key for key in self._api_keys if key not in excluded]
        if not allowed:
            allowed = self._api_keys

        if not self._use_multiple_keys or len(allowed) == 1:
            key = allowed[0]
            self._last_key = key
            return key

        candidates = [key for key in allowed if key != self._last_key]
        if not candidates:
            candidates = allowed

        key = random.choice(candidates)
        self._last_key = key
        return key


class AssemblyAIClient:
    def __init__(
        self,
        api_keys: list[str],
        use_multiple_keys: bool = False,
        poll_interval_seconds: int = 1,
        polling_timeout_seconds: int = 86400,
        key_info_callback: KeyInfoCallback | None = None,
    ) -> None:
        self._selector = ApiKeySelector(api_keys, use_multiple_keys)
        self._poll_interval_seconds = poll_interval_seconds
        self._polling_timeout_seconds = polling_timeout_seconds
        self._session = self._build_session()
        self._job_key: str | None = None
        self._key_info_callback = key_info_callback

    @staticmethod
    def _build_session() -> requests.Session:
        session = requests.Session()
        retry = Retry(
            total=5,
            connect=5,
            read=5,
            backoff_factor=1.2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=8, pool_maxsize=8)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def has_keys(self) -> bool:
        return self._selector.has_keys()

    def _headers_for_key(self, key: str) -> dict[str, str]:
        return {"authorization": key}

    def _emit_key_info(self, key: str) -> None:
        if self._key_info_callback is None:
            return
        try:
            self._key_info_callback(self._selector.index_of(key), self._selector.total())
        except Exception:
            pass

    @staticmethod
    def _is_auth_error(exc: Exception) -> bool:
        if not isinstance(exc, HTTPError) or exc.response is None:
            return False
        return exc.response.status_code in {401, 403}

    def _pick_job_key(self, exclude: set[str] | None = None) -> str:
        if self._job_key and (exclude is None or self._job_key not in exclude):
            self._emit_key_info(self._job_key)
            return self._job_key
        self._job_key = self._selector.pick(exclude=exclude)
        self._emit_key_info(self._job_key)
        return self._job_key

    def upload_file(self, file_path: Path) -> str:
        attempted_keys: set[str] = set()
        last_error: Exception | None = None

        for _ in range(max(1, len(self._selector.all_keys()))):
            key = self._pick_job_key(exclude=attempted_keys)
            attempted_keys.add(key)

            for attempt in range(3):
                response = None
                try:
                    with file_path.open("rb") as file_obj:
                        response = self._session.post(
                            "https://api.assemblyai.com/v2/upload",
                            headers=self._headers_for_key(key),
                            data=file_obj,
                            timeout=(30, 300),
                        )
                    response.raise_for_status()
                    data = response.json()
                    upload_url = data.get("upload_url")
                    if not upload_url:
                        raise RuntimeError(data.get("error", f"РћС€РёР±РєР° Р·Р°РіСЂСѓР·РєРё: {data}"))
                    return str(upload_url)
                except (SSLError, ConnectionError) as exc:
                    last_error = exc
                    if attempt == 2:
                        break
                    self._session = self._build_session()
                    time.sleep(1.0 + attempt)
                except HTTPError as exc:
                    last_error = exc
                    if self._is_auth_error(exc):
                        self._job_key = None
                        break
                    raise

        if self._is_auth_error(last_error or Exception()):
            raise RuntimeError("Р”РѕСЃС‚СѓРї Р·Р°РїСЂРµС‰РµРЅ (401/403). РџСЂРѕРІРµСЂСЊС‚Рµ API РєР»СЋС‡, Р»РёРјРёС‚С‹ Рё Р±РёР»Р»РёРЅРі AssemblyAI.")
        if last_error is not None:
            raise last_error
        raise RuntimeError("РќРµ СѓРґР°Р»РѕСЃСЊ Р·Р°РіСЂСѓР·РёС‚СЊ С„Р°Р№Р»")

    def request_transcription(self, audio_url: str) -> str:
        payload = {
            "audio_url": audio_url,
            "speech_models": ["universal-3-pro", "universal-2"],
            "language_detection": True,
        }

        attempted_keys: set[str] = set()
        last_error: Exception | None = None

        for _ in range(max(1, len(self._selector.all_keys()))):
            key = self._pick_job_key(exclude=attempted_keys)
            attempted_keys.add(key)
            try:
                response = self._session.post(
                    "https://api.assemblyai.com/v2/transcript",
                    json=payload,
                    headers=self._headers_for_key(key),
                    timeout=(30, 120),
                )
                response.raise_for_status()
                data = response.json()
                transcript_id = data.get("id")
                if not transcript_id:
                    raise RuntimeError(data.get("error", f"РћС€РёР±РєР° СЃРѕР·РґР°РЅРёСЏ С‚СЂР°РЅСЃРєСЂРёРїС†РёРё: {data}"))
                return str(transcript_id)
            except HTTPError as exc:
                last_error = exc
                if self._is_auth_error(exc):
                    self._job_key = None
                    continue
                if exc.response is not None:
                    try:
                        error_payload = exc.response.json()
                        error_text = (
                            error_payload.get("error")
                            or error_payload.get("message")
                            or str(error_payload)
                        )
                    except Exception:
                        error_text = exc.response.text or str(exc)
                    raise RuntimeError(f"РћС€РёР±РєР° Р·Р°РїСЂРѕСЃР° С‚СЂР°РЅСЃРєСЂРёРїС†РёРё: {error_text}") from exc
                raise

        if self._is_auth_error(last_error or Exception()):
            raise RuntimeError("Р”РѕСЃС‚СѓРї Р·Р°РїСЂРµС‰РµРЅ (401/403). РџСЂРѕРІРµСЂСЊС‚Рµ API РєР»СЋС‡, Р»РёРјРёС‚С‹ Рё Р±РёР»Р»РёРЅРі AssemblyAI.")
        if last_error is not None:
            raise last_error
        raise RuntimeError("РќРµ СѓРґР°Р»РѕСЃСЊ СЃРѕР·РґР°С‚СЊ Р·Р°РґР°С‡Сѓ С‚СЂР°РЅСЃРєСЂРёРїС†РёРё")

    def wait_for_result(self, transcript_id: str, set_status: StatusCallback) -> TranscriptResult:
        transcript_url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
        started_at = time.monotonic()

        key = self._pick_job_key()
        try:
            while True:
                if time.monotonic() - started_at > self._polling_timeout_seconds:
                    raise RuntimeError("РџСЂРµРІС‹С€РµРЅРѕ РІСЂРµРјСЏ РѕР¶РёРґР°РЅРёСЏ СЂР°СЃС€РёС„СЂРѕРІРєРё")

                response = self._session.get(
                    transcript_url,
                    headers=self._headers_for_key(key),
                    timeout=(30, 120),
                )
                response.raise_for_status()
                data = response.json()
                status = str(data.get("status", ""))

                if status in {"queued", "processing"}:
                    set_status("Р Р°СЃРїРѕР·РЅР°РІР°РЅРёРµ...")
                elif status == "completed":
                    return TranscriptResult(
                        text=str(data.get("text", "")),
                        language_code=str(data.get("language_code", "unknown")),
                    )
                elif status == "error":
                    raise RuntimeError(str(data.get("error", "РћС€РёР±РєР° С‚СЂР°РЅСЃРєСЂРёРїС†РёРё")))
                else:
                    set_status(f"РЎС‚Р°С‚СѓСЃ: {status or 'unknown'}")

                time.sleep(self._poll_interval_seconds)
        finally:
            self._job_key = None
