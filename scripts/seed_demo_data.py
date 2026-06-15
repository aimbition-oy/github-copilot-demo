#!/usr/bin/env python3
"""
seed_demo_data.py — Populate the Arcade with realistic mock data.

Requires the full compose stack to be running:
    docker compose up -d

Usage:
    python scripts/seed_demo_data.py
    python scripts/seed_demo_data.py --auth-url http://localhost:8001 --backend-url http://localhost:8000

Creates:
    - 15 players with classic NES-gamer usernames
    - 120+ scores spread across all 10 games
    - Realistic score distributions (Tetris scores in millions, Zelda in thousands)
    - A few "legendary" players who dominate certain games
"""

import argparse
import random
import sys
import time
from dataclasses import dataclass

import httpx

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

AUTH_URL = "http://localhost:8001"
BACKEND_URL = "http://localhost:8000"

PLAYERS = [
    ("MarioMaster",   "p@ssw0rd!"),
    ("NintendoKing",  "p@ssw0rd!"),
    ("PixelWizard",   "p@ssw0rd!"),
    ("8BitLegend",    "p@ssw0rd!"),
    ("RetroRacer",    "p@ssw0rd!"),
    ("ZeldaQueen",    "p@ssw0rd!"),
    ("MetroidHunter", "p@ssw0rd!"),
    ("ContraGod",     "p@ssw0rd!"),
    ("TetrisBlock",   "p@ssw0rd!"),
    ("PunchOutPro",   "p@ssw0rd!"),
    ("CastleKnight",  "p@ssw0rd!"),
    ("DuckShooter",   "p@ssw0rd!"),
    ("MegaFan",       "p@ssw0rd!"),
    ("IcarusFlyer",   "p@ssw0rd!"),
    ("NoobPlayer",    "p@ssw0rd!"),
]

# Per-game score ranges — tuned to be realistic for each title
GAME_SCORE_PROFILES = {
    "super-mario-bros":    {"min": 1_000,   "max": 999_999, "legendary": 850_000},
    "the-legend-of-zelda": {"min": 0,       "max": 9_999,   "legendary": 9_500},
    "metroid":             {"min": 10_000,  "max": 999_999, "legendary": 750_000},
    "mega-man-2":          {"min": 50_000,  "max": 999_999, "legendary": 900_000},
    "contra":              {"min": 10_000,  "max": 999_999, "legendary": 800_000},
    "castlevania":         {"min": 10_000,  "max": 999_999, "legendary": 700_000},
    "punch-out":           {"min": 0,       "max": 9_999,   "legendary": 9_800},
    "tetris":              {"min": 100_000, "max": 9_999_999, "legendary": 8_500_000},
    "duck-hunt":           {"min": 10_000,  "max": 999_999, "legendary": 850_000},
    "kid-icarus":          {"min": 10_000,  "max": 999_999, "legendary": 600_000},
}

# How many scores each player submits per game (sparse matrix — not everyone plays everything)
# (player_index, game_slug) -> number of attempts (0 = doesn't play this game)
def _attempts(player_idx: int, game_slug: str) -> int:
    """Return how many score submissions a player makes for a game."""
    rng = random.Random(player_idx * 31 + hash(game_slug) % 97)

    # NoobPlayer (index 14) plays everything badly and rarely
    if player_idx == 14:
        return rng.choice([0, 0, 1, 1, 1])

    # Specialist players: each has 1-2 games they grind hard
    specialists = {
        0: ["super-mario-bros", "duck-hunt"],       # MarioMaster
        1: ["contra", "mega-man-2"],                 # NintendoKing
        5: ["the-legend-of-zelda"],                  # ZeldaQueen
        6: ["metroid"],                              # MetroidHunter
        7: ["contra"],                               # ContraGod
        8: ["tetris"],                               # TetrisBlock
        9: ["punch-out"],                            # PunchOutPro
        10: ["castlevania"],                         # CastleKnight
        11: ["duck-hunt"],                           # DuckShooter
        12: ["mega-man-2"],                          # MegaFan
        13: ["kid-icarus"],                          # IcarusFlyer
    }
    specialty = specialists.get(player_idx, [])
    if game_slug in specialty:
        return rng.randint(4, 8)  # lots of attempts on specialty

    # Everyone plays a random subset of other games casually
    return rng.choice([0, 0, 0, 1, 1, 2])


def _score(player_idx: int, game_slug: str, attempt: int) -> int:
    """Generate a plausible score. Specialists can hit legendary territory."""
    profile = GAME_SCORE_PROFILES[game_slug]
    rng = random.Random(player_idx * 137 + hash(game_slug) % 53 + attempt * 17)

    specialists = {
        0: ["super-mario-bros", "duck-hunt"],
        1: ["contra", "mega-man-2"],
        5: ["the-legend-of-zelda"],
        6: ["metroid"],
        7: ["contra"],
        8: ["tetris"],
        9: ["punch-out"],
        10: ["castlevania"],
        11: ["duck-hunt"],
        12: ["mega-man-2"],
        13: ["kid-icarus"],
    }
    is_specialist = game_slug in specialists.get(player_idx, [])

    if is_specialist and attempt >= 3:
        # Their best attempts approach legendary territory
        lo = int(profile["legendary"] * 0.85)
        hi = int(profile["legendary"] * 1.0)
        return rng.randint(lo, hi)
    elif is_specialist:
        lo = int((profile["min"] + profile["legendary"]) / 2)
        hi = int(profile["legendary"] * 0.9)
        return rng.randint(lo, hi)
    else:
        # Casual play: lower half of the range
        lo = profile["min"]
        hi = int((profile["min"] + profile["max"]) / 3)
        return rng.randint(lo, hi)


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

@dataclass
class Player:
    username: str
    password: str
    token: str


def wait_for_services(client: httpx.Client, retries: int = 20) -> None:
    print("⏳ Waiting for services to be ready...", end="", flush=True)
    for _ in range(retries):
        try:
            r1 = client.get(f"{AUTH_URL}/health")
            r2 = client.get(f"{BACKEND_URL}/health")
            if r1.status_code == 200 and r2.status_code == 200:
                print(" ready!")
                return
        except httpx.ConnectError:
            pass
        print(".", end="", flush=True)
        time.sleep(2)
    print()
    print("❌ Services not reachable after timeout. Is 'docker compose up' running?")
    sys.exit(1)


def register_player(client: httpx.Client, username: str, password: str) -> Player | None:
    res = client.post(f"{AUTH_URL}/register", json={"username": username, "password": password})
    if res.status_code == 409:
        print(f"  ↩ {username} already exists, logging in...")
    elif res.status_code not in (200, 201):
        print(f"  ✗ Register {username} failed: {res.status_code} {res.text}")
        return None

    login_res = client.post(f"{AUTH_URL}/login", json={"username": username, "password": password})
    if login_res.status_code != 200:
        print(f"  ✗ Login {username} failed: {login_res.status_code}")
        return None

    token = login_res.json()["access_token"]
    return Player(username=username, password=password, token=token)


def submit_score(client: httpx.Client, player: Player, game_slug: str, score: int) -> bool:
    res = client.post(
        f"{BACKEND_URL}/scores",
        json={"game_slug": game_slug, "score": score},
        headers={"Authorization": f"Bearer {player.token}"},
    )
    return res.status_code == 201


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(auth_url: str, backend_url: str) -> None:
    global AUTH_URL, BACKEND_URL
    AUTH_URL = auth_url
    BACKEND_URL = backend_url

    with httpx.Client(timeout=10.0) as client:
        wait_for_services(client)

        # Fetch available game slugs from the API
        games_res = client.get(f"{BACKEND_URL}/games")
        if games_res.status_code != 200:
            print(f"❌ Could not fetch games: {games_res.status_code}")
            sys.exit(1)
        game_slugs = [g["slug"] for g in games_res.json()]
        print(f"🎮 Found {len(game_slugs)} games: {', '.join(game_slugs)}\n")

        # Register / login all players
        print("👤 Registering players...")
        players: list[Player] = []
        for username, password in PLAYERS:
            p = register_player(client, username, password)
            if p:
                print(f"  ✓ {p.username}")
                players.append(p)
        print(f"\n✅ {len(players)} players ready.\n")

        # Submit scores
        print("🏆 Submitting scores...")
        total = 0
        skipped = 0
        for idx, player in enumerate(players):
            player_total = 0
            for slug in game_slugs:
                n = _attempts(idx, slug)
                for attempt in range(n):
                    score = _score(idx, slug, attempt)
                    ok = submit_score(client, player, slug, score)
                    if ok:
                        player_total += 1
                        total += 1
                    else:
                        skipped += 1
            if player_total:
                print(f"  {player.username:18s} → {player_total} scores submitted")

        print(f"\n✅ Done! {total} scores inserted ({skipped} failed).")
        print(f"\n🔌 MCP connection string (postgres):")
        print(f"   postgresql://arcade:arcade@localhost:5432/arcade_db")
        print(f"   postgresql://arcade:arcade@localhost:5432/auth_db")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the Arcade with mock data")
    parser.add_argument("--auth-url",    default="http://localhost:8001")
    parser.add_argument("--backend-url", default="http://localhost:8000")
    args = parser.parse_args()
    main(args.auth_url, args.backend_url)
