
import csv
from pathlib import Path

from .repository import TransactionRepository


def export_transactions_csv(
    repository: TransactionRepository,
    output_path: str
) -> int:
    path = Path(output_path)

    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "id",
        "type",
        "date",
        "amount",
        "category",
        "memo",
        "tags"
    ]

    count = 0

    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for transaction in repository.get_all():
            writer.writerow({
                "id": transaction.id,
                "type": transaction.type,
                "date": transaction.date,
                "amount": transaction.amount,
                "category": transaction.category,
                "memo": transaction.memo,
                "tags": ",".join(transaction.tags)
            })

            count += 1

    return count
