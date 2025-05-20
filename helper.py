# just dummy functions right now, fill this file with actual fetches later

def get_recent_alerts(limit: int = 5) -> list[dict]:
    """Return recent alerts as simple dicts (mock)."""
    # TODO: replace with an actual 'alerts' object grabbed from supabase
    return [
        dict(
            title="Impossible Travel Detected",
            body="Login from London, UK (2 h after Tokyo login)",
            icon="bi bi-exclamation-triangle-fill",
            ts="2 hours ago",
        ),
        dict(
            title="Multiple Failed Login Attempts",
            body="15 failed attempts from IP 192.168.1.1",
            icon="bi bi-shield-lock-fill",
            ts="4 hours ago",
        ),
    ][:limit]

