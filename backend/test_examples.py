import unittest
from pathlib import Path

from backend.lexer import tokenize


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = REPOSITORY_ROOT / "examples"


class DemoExampleTests(unittest.TestCase):
    def test_valid_examples_have_no_lexical_errors(self) -> None:
        for example in sorted(EXAMPLES.glob("valid_*.sml")):
            with self.subTest(example=example.name):
                source = example.read_text(encoding="utf-8")
                errors = [token for token in tokenize(source) if token.type == "ERROR"]
                self.assertEqual(errors, [])

    def test_invalid_example_demonstrates_multiple_errors(self) -> None:
        source = (EXAMPLES / "invalid_lexical_errors.sml").read_text(
            encoding="utf-8"
        )
        errors = [token for token in tokenize(source) if token.type == "ERROR"]
        self.assertGreaterEqual(len(errors), 7)


if __name__ == "__main__":
    unittest.main()
