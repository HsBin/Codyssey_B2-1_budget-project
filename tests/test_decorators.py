
import io
import unittest

from contextlib import redirect_stdout
from budget_app.decorators import measure_time, log_execution, handle_errors

class TestMeasureTime(unittest.TestCase):

    def test_return_value(self):
        @measure_time
        def add(a, b):
            return a + b

        with redirect_stdout(io.StringIO()):
            result = add(10, 20)

        self.assertEqual(result, 30)

    def test_output_message(self):
        @measure_time
        def sample():
            return "완료"

        output = io.StringIO()

        with redirect_stdout(output):
            sample()

        self.assertIn("[실행 시간] sample:", output.getvalue())

    def test_preserve_function_name(self):
        @measure_time
        def sample_function():
            return True

        self.assertEqual(sample_function.__name__, "sample_function")


class TestLoggingDecorators(unittest.TestCase):

    def test_log_execution(self):
        @log_execution
        def sample():
            return "완료"

        with self.assertLogs(
            "budget_app.decorators",
            level="INFO"
        ) as logs:
            result = sample()

        self.assertEqual(result, "완료")
        self.assertIn("sample 실행 시작", logs.output[0])
        self.assertIn("sample 실행 완료", logs.output[1])

    def test_handle_errors(self):
        @handle_errors
        def failing_function():
            raise ValueError("테스트 오류")

        with self.assertLogs(
            "budget_app.decorators",
            level="ERROR"
        ) as logs:
            with self.assertRaises(ValueError):
                failing_function()

        self.assertIn(
            "failing_function 실행 중 오류 발생",
            logs.output[0]
        )

    def test_handle_errors_success(self):
        @handle_errors
        def add(a, b):
            return a + b

        self.assertEqual(add(10, 20), 30)
