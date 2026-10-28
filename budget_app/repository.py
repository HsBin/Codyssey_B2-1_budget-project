
import json
import uuid
import os
import tempfile
import shutil

from dataclasses import asdict
from pathlib import Path
from typing import Iterator

from .models import Transaction


class TransactionRepository:
    def __init__(self, data_dir: str = "./data") -> None:
        self.data_dir = Path(data_dir)
        self.file_path = self.data_dir / "transactions.jsonl"

        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.file_path.touch(exist_ok=True)

    def add(self, transaction: Transaction) -> None:
        with self.file_path.open("a", encoding="utf-8") as file:
            json.dump(
                asdict(transaction),
                file,
                ensure_ascii=False
            )
            file.write("\n")


    def add_many(self, transactions: list[Transaction]) -> None:
        if not transactions:
            return

        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w+b",
                dir=self.data_dir,
                delete=False
            ) as temp_file:
                temp_path = Path(temp_file.name)

                # 기존 JSONL 데이터를 임시 파일로 복사
                with self.file_path.open("rb") as source:
                    shutil.copyfileobj(source, temp_file)

                # 기존 파일의 마지막 줄에 개행이 없으면 추가
                if temp_file.tell() > 0:
                    temp_file.seek(-1, os.SEEK_END)
                    last_byte = temp_file.read(1) if temp_file.readable() else None
                    temp_file.seek(0, os.SEEK_END)

                    if last_byte != b"\n":
                        temp_file.write(b"\n")

                # 신규 거래를 임시 파일에 기록
                for transaction in transactions:
                    line = json.dumps(
                        asdict(transaction),
                        ensure_ascii=False
                    )
                    temp_file.write((line + "\n").encode("utf-8"))

                temp_file.flush()
                os.fsync(temp_file.fileno())

            # 모든 기록이 성공한 경우에만 원본 교체
            os.replace(temp_path, self.file_path)

        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)


    def get_all(self) -> Iterator[Transaction]:
        with self.file_path.open("r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    data = json.loads(line)
                    yield Transaction(**data)


    def generate_id(self) -> str:
        return f"TX-{uuid.uuid4().hex}"


    def get_by_id(self, transaction_id: str) -> Transaction | None:
        for transaction in self.get_all():
            if transaction.id == transaction_id:
                return transaction

        return None


    def update(self, updated_transaction: Transaction) -> bool:
        temp_path = None
        found = False

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.data_dir,
                delete=False
            ) as temp_file:
                temp_path = Path(temp_file.name)

                for transaction in self.get_all():
                    if transaction.id == updated_transaction.id:
                        transaction = updated_transaction
                        found = True

                    json.dump(
                        asdict(transaction),
                        temp_file,
                        ensure_ascii=False
                    )
                    temp_file.write("\n")

            if found:
                os.replace(temp_path, self.file_path)

            return found

        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)


    def delete(self, transaction_id: str) -> bool:
        temp_path = None
        found = False

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.data_dir,
                delete=False
            ) as temp_file:
                temp_path = Path(temp_file.name)

                for transaction in self.get_all():
                    if transaction.id == transaction_id:
                        found = True
                        continue

                    json.dump(
                        asdict(transaction),
                        temp_file,
                        ensure_ascii=False
                    )
                    temp_file.write("\n")

            if found:
                os.replace(temp_path, self.file_path)

            return found

        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)



class CategoryStore:
    def __init__(self, data_dir: str = "./data") -> None:
        self.data_dir = Path(data_dir)
        self.file_path = self.data_dir / "categories.jsonl"

        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.file_path.touch(exist_ok=True)

    def get_all(self) -> list[str]:
        categories = []

        with self.file_path.open("r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    data = json.loads(line)
                    categories.append(data["name"])

        return categories

    def add(self, name: str) -> None:
        with self.file_path.open("a", encoding="utf-8") as file:
            json.dump(
                {"name": name},
                file,
                ensure_ascii=False
            )
            file.write("\n")


    def remove(self, name: str) -> None:
        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.data_dir,
                delete=False
            ) as temp_file:
                temp_path = Path(temp_file.name)

                for category in self.get_all():
                    if category != name:
                        json.dump(
                            {"name": category},
                            temp_file,
                            ensure_ascii=False
                        )
                        temp_file.write("\n")

            os.replace(temp_path, self.file_path)

        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)


class BudgetRepository:
    def __init__(self, data_dir: str = "./data") -> None:
        self.data_dir = Path(data_dir)
        self.file_path = self.data_dir / "budgets.jsonl"

        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.file_path.touch(exist_ok=True)

    def get_all(self) -> list[dict]:
        budgets = []

        with self.file_path.open("r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    budgets.append(json.loads(line))

        return budgets

    def set_budget(
        self,
        month: str,
        category: str,
        amount: int
    ) -> None:
        budgets = self.get_all()

        updated = False

        for budget in budgets:
            if (
                budget["month"] == month
                and budget["category"] == category
            ):
                budget["amount"] = amount
                updated = True
                break

        if not updated:
            budgets.append({
                "month": month,
                "category": category,
                "amount": amount
            })

        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.data_dir,
                delete=False
            ) as temp_file:
                temp_path = Path(temp_file.name)

                for budget in budgets:
                    json.dump(
                        budget,
                        temp_file,
                        ensure_ascii=False
                    )
                    temp_file.write("\n")

            os.replace(temp_path, self.file_path)

        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
