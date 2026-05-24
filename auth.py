"""
Session cookie management.
Logs in once and saves the cookie to disk so subsequent runs don't need to
re-authenticate. Call ensure_session() before any API request.
"""
import os
import requests
from config import SERVER_URL, USERNAME, PASSWORD, COOKIE_FILE

_session: requests.Session | None = None


def _load_cookie(session: requests.Session) -> bool:
    """Try to load a saved cookie from disk. Return True if found."""
    if not os.path.exists(COOKIE_FILE):
        return False
    with open(COOKIE_FILE) as f:
        cookie = f.read().strip()
    if not cookie:
        return False
    session.cookies.set("session", cookie, domain=SERVER_URL.split("//")[1].split(":")[0])
    return True


def _save_cookie(session: requests.Session) -> None:
    cookie = session.cookies.get("session")
    if cookie:
        with open(COOKIE_FILE, "w") as f:
            f.write(cookie)


def _login(session: requests.Session) -> bool:
    """POST /api/auth/login and save the resulting cookie."""
    if not USERNAME or not PASSWORD:
        raise RuntimeError("NYOMNYOM_USER and NYOMNYOM_PASS must be set in environment")
    resp = session.post(
        f"{SERVER_URL}/api/auth/login",
        json={"username": USERNAME, "password": PASSWORD},
        timeout=10,
    )
    if resp.status_code == 200:
        _save_cookie(session)
        return True
    print(f"[auth] login failed: {resp.status_code} {resp.text}")
    return False


def ensure_session() -> requests.Session:
    """Return a requests.Session with a valid auth cookie, logging in if needed."""
    global _session
    if _session is None:
        _session = requests.Session()
        if not _load_cookie(_session):
            _login(_session)
    return _session


def invalidate() -> None:
    """Clear in-memory session and saved cookie — forces re-login on next call."""
    global _session
    _session = None
    if os.path.exists(COOKIE_FILE):
        os.remove(COOKIE_FILE)
