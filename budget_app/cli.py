
import argparse

from .repository import TransactionRepository, CategoryStore, BudgetRepository
from .service import TransactionService, CategoryService, BudgetService


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


    update_parser = subparsers.add_parser(
        "update",
        help="거래 내역 수정"
    )
    update_parser.add_argument(
        "--id",
        required=True,
        help="수정할 거래 ID"
    )

    delete_parser = subparsers.add_parser(
        "delete",
        help="거래 내역 삭제"
    )
    delete_parser.add_argument(
        "--id",
        required=True,
        help="삭제할 거래 ID"
    )


    search_parser = subparsers.add_parser(
        "search",
        help="조건에 맞는 거래 내역 검색"
    )

    search_parser.add_argument(
        "--category",
        help="카테고리 필터"
    )

    search_parser.add_argument(
        "--type",
        choices=["income", "expense"],
        help="거래 타입 필터"
    )

    search_parser.add_argument(
        "--from",
        dest="date_from",
        help="검색 시작 날짜 (YYYY-MM-DD)"
    )

    search_parser.add_argument(
        "--to",
        dest="date_to",
        help="검색 종료 날짜 (YYYY-MM-DD)"
    )

    search_parser.add_argument(
        "--min-amount",
        type=int,
        help="최소 금액"
    )

    search_parser.add_argument(
        "--max-amount",
        type=int,
        help="최대 금액"
    )

    search_parser.add_argument(
        "--keyword",
        help="메모 검색어"
    )


    summary_parser = subparsers.add_parser(
        "summary",
        help="월별 수입·지출 통계 조회"
    )

    summary_parser.add_argument(
        "--month",
        required=True,
        help="조회할 월 (YYYY-MM)"
    )


    budget_parser = subparsers.add_parser(
        "budget",
        help="월별 예산 관리"
    )

    budget_subparsers = budget_parser.add_subparsers(
        dest="budget_command",
        required=True
    )

    budget_subparsers.add_parser(
        "set",
        help="월별 카테고리 예산 설정"
    )

    budget_list_parser = budget_subparsers.add_parser(
        "list",
        help="월별 예산 및 사용 현황 조회"
    )

    budget_list_parser.add_argument(
        "--month",
        required=True,
        help="조회할 월 (YYYY-MM)"
    )


    args = parser.parse_args()

    repository = TransactionRepository()
    category_store = CategoryStore()
    service = TransactionService(repository, category_store)
    category_service = CategoryService(category_store, repository)
    budget_repository = BudgetRepository()
    budget_service = BudgetService(budget_repository, category_store, repository)

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


    elif args.command == "update":
        try:
            existing = repository.get_by_id(args.id)

            if existing is None:
                raise ValueError("해당 ID의 거래가 존재하지 않습니다.")

            print(f"수정할 거래: {existing.id}")
            print("기존 값을 유지하려면 Enter를 누르세요.")

            date = input(f"날짜 [{existing.date}]: ").strip()
            transaction_type = input(
                f"타입 [{existing.type}]: "
            ).strip()
            category = input(
                f"카테고리 [{existing.category}]: "
            ).strip()
            amount_input = input(
                f"금액 [{existing.amount}]: "
            ).strip()
            memo = input(
                f"메모 [{existing.memo}]: "
            )
            tags_input = input(
                f"태그 [{','.join(existing.tags)}]: "
            ).strip()

            updated = service.update_transaction(
                transaction_id=existing.id,
                date=date or existing.date,
                transaction_type=transaction_type or existing.type,
                category=category or existing.category,
                amount=int(amount_input) if amount_input else existing.amount,
                memo=memo if memo else existing.memo,
                tags=(
                    [tag.strip() for tag in tags_input.split(",") if tag.strip()]
                    if tags_input else existing.tags
                )
            )

            print(f"[수정 완료] id={updated.id}")

        except ValueError as error:
            print(f"[오류] {error}")
            raise SystemExit(1)


    elif args.command == "delete":
        try:
            existing = repository.get_by_id(args.id)

            if existing is None:
                raise ValueError("해당 ID의 거래가 존재하지 않습니다.")

            print(
                f"삭제할 거래: {existing.date} | "
                f"{existing.category} | {existing.amount}원 | "
                f"{existing.memo}"
            )

            confirm = input("정말 삭제하시겠습니까? (y/N): ").strip().lower()

            if confirm != "y":
                print("삭제가 취소되었습니다.")
                return

            service.delete_transaction(existing.id)
            print(f"[삭제 완료] id={existing.id}")

        except ValueError as error:
            print(f"[오류] {error}")
            raise SystemExit(1)


    elif args.command == "search":
        try:
            transactions = service.search_transactions(
                category=args.category,
                transaction_type=args.type,
                date_from=args.date_from,
                date_to=args.date_to,
                min_amount=args.min_amount,
                max_amount=args.max_amount,
                keyword=args.keyword
            )

            if not transactions:
                print("검색 조건에 맞는 거래 내역이 없습니다.")
                return

            print(f"검색 결과: {len(transactions)}건")

            for transaction in transactions:
                print(
                    f"{transaction.id} | {transaction.date} | "
                    f"{transaction.type} | {transaction.category} | "
                    f"{transaction.amount}원 | {transaction.memo}"
                )

        except ValueError as error:
            print(f"[오류] {error}")
            raise SystemExit(1)


    elif args.command == "summary":
        try:
            summary = service.get_monthly_summary(args.month)

            print(f"\n===== {summary['month']} 월별 통계 =====")
            print(f"총수입: {summary['income']:,}원")
            print(f"총지출: {summary['expense']:,}원")
            print(f"잔액: {summary['balance']:,}원")

            print("\n[카테고리별 지출]")

            if not summary["category_expenses"]:
                print("지출 내역이 없습니다.")
            else:
                for category, amount in sorted(
                    summary["category_expenses"].items(),
                    key=lambda item: item[1],
                    reverse=True
                ):
                    print(f"- {category}: {amount:,}원")

        except ValueError as error:
            print(f"[오류] {error}")
            raise SystemExit(1)


    elif args.command == "budget":
        try:
            if args.budget_command == "set":
                month = input("월(YYYY-MM): ").strip()
                category = input("카테고리: ").strip()
                amount = int(input("예산 금액(양수): "))

                budget_service.set_budget(
                    month=month,
                    category=category,
                    amount=amount
                )

                print(
                    f"[저장 완료] {month} | "
                    f"{category} | {amount:,}원"
                )

            elif args.budget_command == "list":
                results = budget_service.get_budget_status(args.month)

                if not results:
                    print("설정된 예산이 없습니다.")
                    return

                print(f"\n===== {args.month} 예산 현황 =====")

                for item in results:
                    print(f"\n[{item['category']}]")
                    print(f"예산: {item['budget']:,}원")
                    print(f"사용: {item['spent']:,}원")
                    print(f"잔액: {item['remaining']:,}원")
                    print(f"사용률: {item['usage_rate']:.1f}%")

                    if item["remaining"] < 0:
                        print("[경고] 예산을 초과했습니다.")

        except ValueError as error:
            print(f"[오류] {error}")
            raise SystemExit(1)
