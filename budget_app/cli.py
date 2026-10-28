
import argparse

from .repository import TransactionRepository, CategoryStore
from .service import TransactionService, CategoryService


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


    category_parser = subparsers.add_parser(
        "category",
        help="카테고리 관리"
    )

    category_subparsers = category_parser.add_subparsers(
        dest="category_command",
        required=True
    )

    category_subparsers.add_parser(
        "add",
        help="카테고리 추가"
    )

    category_subparsers.add_parser(
        "list",
        help="카테고리 목록 조회"
    )

    category_subparsers.add_parser(
        "remove",
        help="카테고리 삭제"
    )


    args = parser.parse_args()

    repository = TransactionRepository()
    category_store = CategoryStore()
    service = TransactionService(repository, category_store)
    category_service = CategoryService(category_store, repository)

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


    elif args.command == "category":
        try:
            if args.category_command == "add":
                name = input("카테고리명: ")
                category_service.add_category(name)
                print(f"[저장 완료] category={name.strip()}")

            elif args.category_command == "list":
                categories = category_service.list_categories()

                if not categories:
                    print("등록된 카테고리가 없습니다.")
                else:
                    for category in categories:
                        print(f"- {category}")

            elif args.category_command == "remove":
                name = input("삭제할 카테고리명: ")
                category_service.remove_category(name)
                print(f"[삭제 완료] category={name.strip()}")

        except ValueError as error:
            print(f"[오류] {error}")
            raise SystemExit(1)
