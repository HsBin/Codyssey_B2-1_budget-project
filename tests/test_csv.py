
import csv
import tempfile
import unittest
from pathlib import Path

from budget_app.repository import TransactionRepository, CategoryStore
from budget_app.service import TransactionService
from budget_app.exporter import export_transactions_csv
from budget_app.importer import import_transactions_csv
from unittest.mock import patch

class TestCSV(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)

        self.repository = TransactionRepository(
            str(self.base_path / "source")
        )
        self.category_store = CategoryStore(
            str(self.base_path / "source")
        )

        self.category_store.add("food")

        self.service = TransactionService(
            self.repository,
            self.category_store
        )

        self.csv_path = self.base_path / "transactions.csv"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_export_csv(self):
        self.service.add_transaction(
            date="2026-10-28",
            type="expense",
            category="food",
            amount=15000,
            memo="점심",
            tags=["meal"]
        )

        count = export_transactions_csv(
            self.repository,
            str(self.csv_path)
        )

        self.assertEqual(count, 1)
        self.assertTrue(self.csv_path.exists())

        with self.csv_path.open(
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:
            rows = list(csv.DictReader(file))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["amount"], "15000")
        self.assertEqual(rows[0]["memo"], "점심")
        self.assertEqual(rows[0]["tags"], "meal")

    def test_import_csv_and_skip_duplicates(self):
        original = self.service.add_transaction(
            date="2026-10-28",
            type="expense",
            category="food",
            amount=8500,
            memo="커피",
            tags=["cafe", "drink"]
        )

        export_transactions_csv(
            self.repository,
            str(self.csv_path)
        )

        target_repository = TransactionRepository(
            str(self.base_path / "target")
        )
        target_categories = CategoryStore(
            str(self.base_path / "target")
        )
        target_categories.add("food")

        first = import_transactions_csv(
            target_repository,
            target_categories,
            str(self.csv_path)
        )

        self.assertEqual(first["imported"], 1)
        self.assertEqual(first["skipped"], 0)

        imported = list(target_repository.get_all())

        self.assertEqual(len(imported), 1)
        self.assertEqual(imported[0].id, original.id)
        self.assertEqual(imported[0].tags, ["cafe", "drink"])

        second = import_transactions_csv(
            target_repository,
            target_categories,
            str(self.csv_path)
        )

        self.assertEqual(second["imported"], 0)
        self.assertEqual(second["skipped"], 1)
        self.assertEqual(
            len(list(target_repository.get_all())),
            1
        )

    def test_import_missing_file(self):
        with self.assertRaises(ValueError):
            import_transactions_csv(
                self.repository,
                self.category_store,
                str(self.base_path / "missing.csv")
            )

    def test_import_rollback_on_replace_failure(self):
        # 기존 데이터 저장
        original_content = self.repository.file_path.read_bytes()

        # 임포트할 CSV 파일 생성
        csv_path = Path(self.temp_dir.name) / "rollback_test.csv"

        with csv_path.open(
            "w",
            encoding="utf-8-sig",
            newline=""
        ) as file:
            writer = csv.writer(file)
            writer.writerow([
                "id", "type", "date", "amount",
                "category", "memo", "tags"
            ])
            category = next(iter(self.category_store.get_all()))
            writer.writerow([
                "TX-rollback-test",
                "expense",
                "2026-10-29",
                "5000",
                category,
                "롤백 테스트",
                ""
            ])

        # 최종 파일 교체 단계에서 오류 발생시키기
        with patch(
            "budget_app.repository.os.replace",
            side_effect=OSError("파일 교체 실패")
        ):
            with self.assertRaises(OSError):
                import_transactions_csv(
                    self.repository,
                    self.category_store,
                    str(csv_path)
                )

        # 원본 파일이 변경되지 않았는지 확인
        self.assertEqual(
            self.repository.file_path.read_bytes(),
            original_content
        )

        # 신규 거래가 저장되지 않았는지 확인
        self.assertIsNone(
            self.repository.get_by_id("TX-rollback-test")
        )
