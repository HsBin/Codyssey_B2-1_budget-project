import heapq
from itertools import count

from datetime import datetime

from .models import Transaction
from .repository import TransactionRepository


class TransactionService:
    def __init__(self, repository: TransactionRepository) -> None:
        self.repository = repository

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
        if not category.strip():
            raise ValueError(
                "카테고리는 비워둘 수 없습니다."
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
