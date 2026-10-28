
import argparse

from .repository import TransactionRepository
from .service import TransactionService


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

    list_parser = subparsers.add_parser(
        "list",
        help="거래 내역 조회"
    )

    list_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="조회할 거래 개수 (기본값: 10)"
    )

    args = parser.parse_args()

    repository = TransactionRepository()
    service = TransactionService(repository)

    if args.command == "add":
        try:
            date = input("날짜(YYYY-MM-DD): ")
            transaction_type = input("타입(income/expense): ")
            category = input("카테고리: ")
            amount = int(input("금액(양수): "))
            memo = input("메모(선택): ")
            tags_input = input("태그(쉼표로 구분, 선택): ")

            tags = [
                tag.strip()
                for tag in tags_input.split(",")
                if tag.strip()
            ]

            transaction = service.add_transaction(
                date=date,
                type=transaction_type,
                category=category,
                amount=amount,
                memo=memo,
                tags=tags
            )

            print(f"[저장 완료] id={transaction.id}")

        except ValueError as error:
            print(f"[오류] {error}")
            raise SystemExit(1)


    elif args.command == "list":
        try:
            transactions = service.list_transactions(args.limit)

            if not transactions:
                print("저장된 거래 내역이 없습니다.")
                return

            for transaction in transactions:
                print(
                    f"{transaction.id} | "
                    f"{transaction.date} | "
                    f"{transaction.type} | "
                    f"{transaction.category} | "
                    f"{transaction.amount}원 | "
                    f"{transaction.memo}"
                )

        except ValueError as error:
            print(f"[오류] {error}")
            raise SystemExit(1)
