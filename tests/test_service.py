
import tempfile
import unittest

from budget_app.repository import (
    TransactionRepository,
    CategoryStore,
    BudgetRepository
)
from budget_app.service import TransactionService, BudgetService


class TestTransactionService(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        self.repository = TransactionRepository(
            self.temp_dir.name
        )

        self.category_store = CategoryStore(
            self.temp_dir.name
        )

        self.category_store.add("food")

        self.service = TransactionService(
            self.repository,
            self.category_store
        )

    def tearDown(self):
        self.temp_dir.cleanup()


    def test_update_transaction(self):
        transaction = self.service.add_transaction(
            date="2026-10-28",
            type="expense",
            category="food",
            amount=10000,
            memo="점심"
        )

        updated = self.service.update_transaction(
            transaction_id=transaction.id,
            date="2026-10-29",
            transaction_type="expense",
            category="food",
            amount=15000,
            memo="저녁",
            tags=["dinner"]
        )

        self.assertEqual(updated.amount, 15000)
        self.assertEqual(updated.memo, "저녁")

        saved = self.repository.get_by_id(transaction.id)
        self.assertEqual(saved.amount, 15000)
        self.assertEqual(saved.tags, ["dinner"])

    def test_delete_transaction(self):
        transaction = self.service.add_transaction(
            date="2026-10-28",
            type="expense",
            category="food",
            amount=10000
        )

        self.service.delete_transaction(transaction.id)

        self.assertIsNone(
            self.repository.get_by_id(transaction.id)
        )

    def test_search_transactions(self):
        self.service.add_transaction(
            date="2026-10-28",
            type="expense",
            category="food",
            amount=15000,
            memo="점심"
        )

        self.service.add_transaction(
            date="2026-10-29",
            type="expense",
            category="food",
            amount=8000,
            memo="커피"
        )

        results = self.service.search_transactions(
            category="food",
            min_amount=10000
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].memo, "점심")


    def test_add_transaction_success(self):
        transaction = self.service.add_transaction(
            date="2026-10-28",
            type="expense",
            category="food",
            amount=15000,
            memo="점심",
            tags=["meal"]
        )

        self.assertEqual(transaction.amount, 15000)
        self.assertEqual(transaction.category, "food")

        transactions = list(self.repository.get_all())
        self.assertEqual(len(transactions), 1)

    def test_add_transaction_invalid_amount(self):
        with self.assertRaises(ValueError):
            self.service.add_transaction(
                date="2026-10-28",
                type="expense",
                category="food",
                amount=-1000
            )

    def test_add_transaction_invalid_category(self):
        with self.assertRaises(ValueError):
            self.service.add_transaction(
                date="2026-10-28",
                type="expense",
                category="unknown",
                amount=1000
            )

    def test_add_transaction_invalid_date(self):
        with self.assertRaises(ValueError):
            self.service.add_transaction(
                date="2026-13-28",
                type="expense",
                category="food",
                amount=1000
            )

    def test_monthly_summary(self):
        self.service.add_transaction(
            date="2026-10-28",
            type="expense",
            category="food",
            amount=15000
        )

        self.service.add_transaction(
            date="2026-10-29",
            type="income",
            category="food",
            amount=50000
        )

        summary = self.service.get_monthly_summary("2026-10")

        self.assertEqual(summary["income"], 50000)
        self.assertEqual(summary["expense"], 15000)
        self.assertEqual(summary["balance"], 35000)
        self.assertEqual(
            summary["category_expenses"]["food"],
            15000
        )


class TestBudgetService(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        self.repository = TransactionRepository(
            self.temp_dir.name
        )
        self.category_store = CategoryStore(
            self.temp_dir.name
        )
        self.budget_repository = BudgetRepository(
            self.temp_dir.name
        )

        self.category_store.add("food")

        self.transaction_service = TransactionService(
            self.repository,
            self.category_store
        )

        self.budget_service = BudgetService(
            self.budget_repository,
            self.category_store,
            self.repository
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_budget_status(self):
        self.budget_service.set_budget(
            "2026-10",
            "food",
            30000
        )

        self.transaction_service.add_transaction(
            date="2026-10-28",
            type="expense",
            category="food",
            amount=35500
        )

        results = self.budget_service.get_budget_status("2026-10")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["budget"], 30000)
        self.assertEqual(results[0]["spent"], 35500)
        self.assertEqual(results[0]["remaining"], -5500)
        self.assertAlmostEqual(
            results[0]["usage_rate"],
            118.33333333333333
        )

    def test_budget_invalid_amount(self):
        with self.assertRaises(ValueError):
            self.budget_service.set_budget(
                "2026-10",
                "food",
                -10000
            )


if __name__ == "__main__":
    unittest.main()
