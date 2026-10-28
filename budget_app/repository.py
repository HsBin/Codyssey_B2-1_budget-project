
import json
import uuid
import os
import tempfile

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

    def get_all(self) -> Iterator[Transaction]:
        with self.file_path.open("r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    data = json.loads(line)
                    yield Transaction(**data)


    def generate_id(self) -> str:
        return f"TX-{uuid.uuid4().hex}"


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
