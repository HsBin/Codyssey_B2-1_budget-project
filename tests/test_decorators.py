
import io
import unittest
from contextlib import redirect_stdout

from budget_app.decorators import measure_time


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
