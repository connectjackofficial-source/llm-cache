"""llm-cache CLI."""
import argparse

from .cache import LLMCache


def main():
    ap = argparse.ArgumentParser(prog="llm-cache")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("stats", help="show cache stats")
    sub.add_parser("clear", help="delete all entries")
    args = ap.parse_args()
    c = LLMCache()
    if args.cmd == "stats":
        print(c.stats())
    elif args.cmd == "clear":
        print({"cleared": c.clear()})


if __name__ == "__main__":
    main()
