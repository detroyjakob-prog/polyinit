from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="{{package_name}}",
        description="Command line interface for {{project_name}}.",
    )
    parser.add_argument(
        "--name",
        default="World",
        help="Name to greet (default: %(default)s).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    print(f"Hello {args.name} from {{project_name}}!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
