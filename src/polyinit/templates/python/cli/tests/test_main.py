from {{package_name}}.main import build_parser, main


def test_main_exists():
    assert callable(main)


def test_build_parser():
    parser = build_parser()
    args = parser.parse_args([])
    assert args.name == "World"


def test_main_prints_greeting(capsys):
    assert main(["--name", "Alice"]) == 0
    captured = capsys.readouterr()
    assert "Hello Alice" in captured.out
