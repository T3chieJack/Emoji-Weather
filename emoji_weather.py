import os, sys, requests

WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")
LOCATION = os.getenv("LOCATION", "Hatfield")   # default = Hatfield
if not WEBHOOK:
    print("Missing DISCORD_WEBHOOK_URL", file=sys.stderr); sys.exit(1)

# wttr.in emoji weather (docs: https://wttr.in/:help)
FORMAT = "%l: %c %t (feels %f) %w"
URL = f"https://wttr.in/{LOCATION}?format={FORMAT}"

def fetch_line():
    r = requests.get(URL, timeout=15, headers={"User-Agent": "discord-emoji-weather/1.0"})
    r.raise_for_status()
    return r.text.strip()

def post_discord(line):
    payload = {
        "username": "Emoji Weather",
        "embeds": [{
            "title": f"🌦️ Weather — {LOCATION}",
            "description": line
        }]
    }
    resp = requests.post(WEBHOOK, json=payload, timeout=15)
    if resp.status_code not in (200, 204):
        print(f"Discord post failed: {resp.status_code} {resp.text}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    try:
        post_discord(fetch_line())
    except Exception as e:
        # Fallback if API fails
        requests.post(WEBHOOK, json={"content": f"🌦️ Weather unavailable for {LOCATION}: {e}"}, timeout=10)
        sys.exit(1)
