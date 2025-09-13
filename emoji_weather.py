# emoji_weather_hatfield.py
# Posts Hatfield weather to a Discord webhook using wttr.in (emoji output).
# - Uses precise coords for lookup to avoid ambiguity
# - Always displays "Hatfield" as the title
# - Metric units

import os
import sys
import requests
from urllib.parse import quote_plus

WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")
# Exact point in Hatfield, Hertfordshire (tilde tells wttr.in it's a coordinate)
LOCATION = os.getenv("LOCATION", "~51.7635,-0.2259")
# What to show in the embed title
DISPLAY_NAME = os.getenv("DISPLAY_NAME", "Hatfield")

if not WEBHOOK:
    print("Missing DISCORD_WEBHOOK_URL", file=sys.stderr)
    sys.exit(1)

# wttr.in emoji format (see https://wttr.in/:help)
FORMAT = "%l: %c %t (feels %f) %w"

HEADERS = {
    "User-Agent": "emoji-weather/2.1 (+github-actions)",
    "Accept-Language": "en-GB,en;q=0.9",
    "Cache-Control": "no-cache",
}

def fetch_line(location: str) -> str:
    # Build URL with proper encoding via params
    base = f"https://wttr.in/{quote_plus(location)}"
    params = {"format": FORMAT, "m": ""}  # m => metric
    r = requests.get(base, params=params, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.text.strip()

def post_discord(title_loc: str, line: str):
    payload = {
        "username": "Emoji Weather",
        "embeds": [{
            "title": f"🌦️ Weather — {title_loc}",
            "description": line
        }]
    }
    resp = requests.post(WEBHOOK, json=payload, timeout=20)
    if resp.status_code not in (200, 204):
        print(f"Discord post failed: {resp.status_code} {resp.text}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    try:
        line = fetch_line(LOCATION)
        # If wttr.in still returns an "Unknown location" hint for some reason, show it verbatim.
        post_discord(DISPLAY_NAME, line)
    except Exception as e:
        # Fallback message so you still get a notification
        try:
            requests.post(
                WEBHOOK,
                json={"content": f"🌦️ Weather unavailable for {DISPLAY_NAME}: {e}"},
                timeout=10
            )
        finally:
            sys.exit(1)
