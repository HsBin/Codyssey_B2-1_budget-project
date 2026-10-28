
import argparse


def main() -> None:
    parser = argparse.ArgumentParser(
        description="나만의 용돈 기입장 프로그램"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    subparsers.add_parser(
        "add",
        help="거래 내역 추가"
    )

    subparsers.add_parser(
        "list",
        help="거래 내역 조회"
    )

    args = parser.parse_args()

    if args.command == "add":
        print("거래 추가 기능은 아직 구현되지 않았습니다.")

    elif args.command == "list":
        print("거래 목록 기능은 아직 구현되지 않았습니다.")
