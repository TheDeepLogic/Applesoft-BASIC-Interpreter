#!/usr/bin/env python3
"""Manual Applesoft BASIC launcher for interactive play."""

import argparse
import os
import subprocess
import sys


def resolve_game_path(game: str) -> str:
    """Resolve a game name or path to a .bas file."""
    candidate_paths = []

    # If caller already passed a path, check it first.
    candidate_paths.append(game)

    # If caller passed a simple name, also try adding .bas.
    if not game.lower().endswith(".bas"):
        candidate_paths.append(f"{game}.bas")

    # Search in common project locations for bare names.
    base_names = [game]
    if not game.lower().endswith(".bas"):
        base_names.append(f"{game}.bas")

    for name in base_names:
        candidate_paths.append(os.path.join("basic_code", "games", name))
        candidate_paths.append(os.path.join("basic_code", name))

    for path in candidate_paths:
        if os.path.isfile(path):
            return path

    raise FileNotFoundError(f"Could not find BASIC file for '{game}'")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run an Applesoft BASIC file in manual play mode")
    parser.add_argument(
        "game",
        nargs="?",
        default="demo",
        help="Program name or path (example: lemon_drop or basic_code/games/lemon_drop.bas)",
    )
    parser.add_argument("--input-timeout", type=float, default=120.0, help="Seconds per INPUT/GET prompt")
    parser.add_argument("--exec-timeout", type=float, default=3600.0, help="Max total run time in seconds")
    args = parser.parse_args()

    try:
        game_path = resolve_game_path(args.game)
    except FileNotFoundError as exc:
        print(str(exc))
        return 2

    print("=" * 60)
    print("APPLESOFT MANUAL PLAY MODE")
    print("=" * 60)
    print(f"Game: {game_path}")
    print(f"Input timeout: {args.input_timeout}s")
    print(f"Execution timeout: {args.exec_timeout}s")
    print()
    print("Type your game's commands when prompted by the game.")
    print("Close the game window or quit in-game to exit.")
    print("=" * 60)
    print()

    result = subprocess.run(
        [
            sys.executable,
            "applesoft.py",
            game_path,
            "--input-timeout",
            str(args.input_timeout),
            "--exec-timeout",
            str(args.exec_timeout),
        ],
        timeout=max(int(args.exec_timeout) + 100, 120),
    )

    print()
    print("=" * 60)
    print("Game ended.")
    print(f"Exit code: {result.returncode}")
    print("=" * 60)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
