import heapq
from itertools import count

from datetime import datetime

from .models import Transaction
from .repository import TransactionRepository, CategoryStore
from dataclasses import replace

class TransactionService:
    def __init__(
        self,
        repository: TransactionRepository,
        category_store: CategoryStore
    ) -> None:
        self.repository = repository
        self.category_store = category_store

    def add_transaction(
        self,
        date: str,
        type: str,
        category: str,
        amount: int,
        memo: str = "",
        tags: list[str] | None = None
    ) -> Transaction:

        # 날짜 검증
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d")
            if parsed_date.strftime("%Y-%m-%d") != date:
                raise ValueError
        except ValueError:
            raise ValueError(
                "날짜 형식이 올바르지 않습니다. 예: 2026-10-28"
            )

        # 거래 타입 검증
        if type not in ("income", "expense"):
            raise ValueError(
                "거래 타입은 income 또는 expense여야 합니다."
            )

        # 금액 검증
        if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
            raise ValueError("금액은 0보다 큰 정수여야 합니다.")

        # 카테고리 기본 검증
        category = category.strip()

        if not category:
            raise ValueError("카테고리는 비워둘 수 없습니다.")

        if category not in self.category_store.get_all():
            raise ValueError(
                "등록되지 않은 카테고리입니다. category add로 먼저 등록하세요."
            )

        transaction = Transaction(
            id=self.repository.generate_id(),
            type=type,
            date=date,
            amount=amount,
            category=category.strip(),
            memo=memo,
            tags=tags if tags is not None else []
        )

        self.repository.add(transaction)

        return transaction


    def list_transactions(self, limit: int = 10) -> list[Transaction]:
        if limit <= 0:
            raise ValueError("조회 개수는 1 이상이어야 합니다.")

        sequence = count()

        latest = heapq.nlargest(
            limit,
            (
                (transaction.date, next(sequence), transaction)
                for transaction in self.repository.get_all()
            ),
            key=lambda item: (item[0], item[1])
        )

        return [item[2] for item in latest]

    def update_transaction(
        self,
        transaction_id: str,
        date: str,
        transaction_type: str,
        category: str,
        amount: int,
        memo: str,
        tags: list[str]
    ) -> Transaction:
        existing = self.repository.get_by_id(transaction_id)

        if existing is None:
            raise ValueError("해당 ID의 거래가 존재하지 않습니다.")

        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d")
            if parsed_date.strftime("%Y-%m-%d") != date:
                raise ValueError
        except ValueError:
            raise ValueError("날짜 형식이 올바르지 않습니다. 예: 2026-10-28")

        if transaction_type not in ("income", "expense"):
            raise ValueError("거래 타입은 income 또는 expense여야 합니다.")

        if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
            raise ValueError("금액은 0보다 큰 정수여야 합니다.")

        category = category.strip()

        if category not in self.category_store.get_all():
            raise ValueError("등록되지 않은 카테고리입니다.")

        updated = replace(
            existing,
            date=date,
            type=transaction_type,
            category=category,
            amount=amount,
            memo=memo,
            tags=tags
        )

        if not self.repository.update(updated):
            raise ValueError("거래 수정에 실패했습니다.")

        return updated

    def delete_transaction(self, transaction_id: str) -> None:
        if not self.repository.delete(transaction_id):
            raise ValueError("해당 ID의 거래가 존재하지 않습니다.")

    def search_transactions(
        self,
        category: str | None = None,
        transaction_type: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        min_amount: int | None = None,
        max_amount: int | None = None,
        keyword: str | None = None
    ) -> list[Transaction]:

        def validate_date(value: str) -> None:
            try:
                parsed = datetime.strptime(value, "%Y-%m-%d")
                if parsed.strftime("%Y-%m-%d") != value:
                    raise ValueError
            except ValueError:
                raise ValueError(
                    f"날짜 형식이 올바르지 않습니다: {value}"
                )

        if date_from is not None:
            validate_date(date_from)

        if date_to is not None:
            validate_date(date_to)

        if date_from and date_to and date_from > date_to:
            raise ValueError("시작 날짜는 종료 날짜보다 늦을 수 없습니다.")

        if transaction_type is not None:
            if transaction_type not in ("income", "expense"):
                raise ValueError("타입은 income 또는 expense여야 합니다.")

        if min_amount is not None and min_amount < 0:
            raise ValueError("최소 금액은 0 이상이어야 합니다.")

        if max_amount is not None and max_amount < 0:
            raise ValueError("최대 금액은 0 이상이어야 합니다.")

        if (
            min_amount is not None
            and max_amount is not None
            and min_amount > max_amount
        ):
            raise ValueError("최소 금액은 최대 금액보다 클 수 없습니다.")

        results = []

        for transaction in self.repository.get_all():
            if category is not None and transaction.category != category:
                continue

            if transaction_type is not None and transaction.type != transaction_type:
                continue

            if date_from is not None and transaction.date < date_from:
                continue

            if date_to is not None and transaction.date > date_to:
                continue

            if min_amount is not None and transaction.amount < min_amount:
                continue

            if max_amount is not None and transaction.amount > max_amount:
                continue

            if keyword is not None:
                if keyword.lower() not in transaction.memo.lower():
                    continue

            results.append(transaction)

        return results


class CategoryService:
    def __init__(
        self,
        category_store: CategoryStore,
        transaction_repository: TransactionRepository
    ) -> None:
        self.category_store = category_store
        self.transaction_repository = transaction_repository

    def add_category(self, name: str) -> None:
        name = name.strip()

        if not name:
            raise ValueError("카테고리 이름은 비워둘 수 없습니다.")

        if name in self.category_store.get_all():
            raise ValueError("이미 등록된 카테고리입니다.")

        self.category_store.add(name)

    def list_categories(self) -> list[str]:
        return self.category_store.get_all()

    def remove_category(self, name: str) -> None:
        name = name.strip()

        if name not in self.category_store.get_all():
            raise ValueError("존재하지 않는 카테고리입니다.")

        for transaction in self.transaction_repository.get_all():
            if transaction.category == name:
                raise ValueError(
                    "사용 중인 카테고리는 삭제할 수 없습니다."
                )

        self.category_store.remove(name)
