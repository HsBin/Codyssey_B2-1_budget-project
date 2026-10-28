
import csv
from datetime import datetime
from pathlib import Path

from .models import Transaction
from .repository import TransactionRepository, CategoryStore


def import_transactions_csv(
    repository: TransactionRepository,
    category_store: CategoryStore,
    input_path: str
) -> dict:
    path = Path(input_path)

    if not path.is_file():
        raise ValueError("CSV 파일을 찾을 수 없습니다.")

    existing_ids = {
        transaction.id
        for transaction in repository.get_all()
    }

    valid_categories = set(category_store.get_all())

    imported_transactions = []
    skipped = 0

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        required_fields = {
            "id", "type", "date", "amount",
            "category", "memo", "tags"
        }

        if not required_fields.issubset(reader.fieldnames or []):
            raise ValueError("CSV 파일에 필요한 열이 없습니다.")

        for row_number, row in enumerate(reader, start=2):
            try:
                transaction_id = row["id"].strip()
                transaction_type = row["type"].strip()
                date = row["date"].strip()
                category = row["category"].strip()
                amount = int(row["amount"])

                if not transaction_id:
                    raise ValueError("거래 ID가 비어 있습니다.")

                if transaction_id in existing_ids:
                    skipped += 1
                    continue

                parsed_date = datetime.strptime(date, "%Y-%m-%d")

                if parsed_date.strftime("%Y-%m-%d") != date:
                    raise ValueError("날짜 형식이 올바르지 않습니다.")

                if transaction_type not in ("income", "expense"):
                    raise ValueError("거래 유형은 income 또는 expense여야 합니다.")

                if category not in valid_categories:
                    raise ValueError("등록되지 않은 카테고리입니다.")

                if amount <= 0:
                    raise ValueError("금액은 0보다 커야 합니다.")

                tags = [
                    tag.strip()
                    for tag in row["tags"].split(",")
                    if tag.strip()
                ]

                transaction = Transaction(
                    id=transaction_id,
                    type=transaction_type,
                    date=date,
                    amount=amount,
                    category=category,
                    memo=row["memo"],
                    tags=tags
                )

                imported_transactions.append(transaction)
                existing_ids.add(transaction_id)

            except (ValueError, TypeError, AttributeError) as error:
                raise ValueError(
                    f"{row_number}행: {error}"
                ) from error

    repository.add_many(imported_transactions)

    return {
        "imported": len(imported_transactions),
        "skipped": skipped
    }
