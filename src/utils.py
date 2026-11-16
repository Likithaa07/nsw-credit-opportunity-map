"""Shared helpers: logging, clear errors, input checks and downloads that retry."""
# STEP 1: Imports
from __future__ import annotations

import logging
import sys
from collections.abc import Iterable
from pathlib import Path

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# STEP 2: Logging - one consistent format for every script
def get_logger(name: str) -> logging.Logger:
    """Return a logger. The first call sets up a simple 'time  level  message' format."""
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                            format="%(asctime)s  %(levelname)-7s %(name)s: %(message)s",
                            datefmt="%H:%M:%S")
    return logging.getLogger(name)


log = get_logger("utils")


# STEP 3: Errors that stop the pipeline with a clear message
class PipelineError(Exception):
    """Base class for problems that should stop the pipeline."""


class MissingInputError(PipelineError, FileNotFoundError):
    """An input file is missing."""


class DataValidationError(PipelineError, ValueError):
    """The data failed a check."""


class DownloadError(PipelineError):
    """A data service could not be reached or sent back something unexpected."""


def require_files(*paths: Path, hint: str = "") -> None:
    """Stop with a helpful message if any input file is missing."""
    missing = [str(p) for p in paths if not Path(p).exists()]
    if missing:
        message = "Missing input file(s):\n  " + "\n  ".join(missing)
        raise MissingInputError(message + (f"\n{hint}" if hint else ""))


def require_columns(df: pd.DataFrame, columns: Iterable[str], name: str) -> None:
    """Check that a table has every column the next steps rely on."""
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise DataValidationError(f"{name}: missing column(s) {missing}.")


# STEP 4: A web session that retries when a service blips (timeouts, 429, 5xx errors)
def make_session(retries: int = 5, backoff: float = 2.0) -> requests.Session:
    """Waits 2, 4, 8, 16... seconds between tries."""
    retry = Retry(total=retries, connect=retries, read=retries, status=retries,
                  backoff_factor=backoff, status_forcelist=[429, 500, 502, 503, 504],
                  allowed_methods=["GET"], raise_on_status=False)
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.mount("http://", HTTPAdapter(max_retries=retry))
    return session


SESSION = make_session()


def get(url: str, params: dict | None = None, timeout: int = 300,
        session: requests.Session | None = None) -> requests.Response:
    """GET with retries. Raises DownloadError for an error page instead of treating it as data."""
    session = session or SESSION
    try:
        r = session.get(url, params=params, timeout=timeout)
        r.raise_for_status()
    except requests.RequestException as exc:
        raise DownloadError(f"Request to {url} failed: {exc}") from exc
    return r


def get_json(url: str, params: dict | None = None, timeout: int = 300,
             session: requests.Session | None = None) -> dict:
    """GET JSON. ArcGIS sends errors as '200 OK' with an 'error' key, so check for that too."""
    r = get(url, params, timeout, session)
    try:
        data = r.json()
    except ValueError as exc:
        raise DownloadError(f"{url} did not send back JSON (got: {r.text[:120]!r})") from exc
    if isinstance(data, dict) and "error" in data:
        raise DownloadError(f"{url} returned an error: {data['error']}")
    return data


# STEP 5: Download a file once (skipped if it is already there)
def download(url: str, path: Path, session: requests.Session | None = None) -> Path:
    """Saves to a '.part' file first, so a failed download never leaves a broken file behind."""
    path = Path(path)
    if path.exists() and path.stat().st_size > 0:
        return path
    log.info("Downloading %s", path.name)
    part = path.with_suffix(path.suffix + ".part")
    session = session or SESSION
    try:
        with session.get(url, stream=True, timeout=600) as r:
            r.raise_for_status()
            with open(part, "wb") as f:
                for chunk in r.iter_content(chunk_size=1 << 20):
                    f.write(chunk)
    except requests.RequestException as exc:
        part.unlink(missing_ok=True)
        raise DownloadError(f"Download of {path.name} failed: {exc}") from exc
    if part.stat().st_size == 0:
        part.unlink()
        raise DownloadError(f"Download of {path.name} was empty. The service may be blocking "
                            "scripted downloads; try again later or download it by hand.")
    part.replace(path)
    return path
