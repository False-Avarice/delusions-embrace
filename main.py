#!/usr/bin/env python3
import argparse
import sys
import time

from game_engine import GameEngine


def type_text(text):
    for character in text:
        sys.stdout.write(character)
        sys.stdout.flush()
        time.sleep(0.016)
    print()
    time.sleep(0.18)


def get_choice(options):
    for index, option in enumerate(options, 1):
        print(f" {index}. {option}")

    while True:
        choice = input("\n> ").strip()
        try:
            index = int(choice) - 1
        except ValueError:
            index = -1
        if 0 <= index < len(options):
            return index
        print("Enter the number of a choice.")


def main(instant=False):
    engine = GameEngine()
    state = engine.get_initial_state()
    scene = engine.process_step(state)
    write = print if instant else type_text

    while True:
        if scene["title"]:
            print(f"\n{scene['title'].upper()}\n")
        for paragraph in scene["text"]:
            write(paragraph)
            print()

        if state["current_step"] == "restart":
            return

        scene = engine.process_step(state, get_choice(scene["choices"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--instant", action="store_true", help="Show each passage without typing delays.")
    try:
        main(instant=parser.parse_args().instant)
    except (EOFError, KeyboardInterrupt):
        print("\nGame exited.")
