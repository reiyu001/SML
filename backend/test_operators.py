import unittest

from backend.lexer import tokenize


OPERATORS = [
    ("=", "ASSIGN"),
    ("+=", "PLUS_ASSIGN"),
    ("-=", "MINUS_ASSIGN"),
    ("*=", "MULTIPLY_ASSIGN"),
    ("/=", "DIVIDE_ASSIGN"),
    ("+", "PLUS"),
    ("-", "MINUS"),
    ("*", "MULTIPLY"),
    ("/", "DIVIDE"),
    ("%", "MODULO"),
    ("^", "POWER"),
    ("==", "EQUAL"),
    ("!=", "NOT_EQUAL"),
    ("<", "LESS_THAN"),
    (">", "GREATER_THAN"),
    ("<=", "LESS_THAN_OR_EQUAL"),
    (">=", "GREATER_THAN_OR_EQUAL"),
    ("&&", "LOGICAL_AND"),
    ("||", "LOGICAL_OR"),
    ("!", "LOGICAL_NOT"),
    ("++", "INCREMENT"),
    ("--", "DECREMENT"),
]


class OperatorTokenTests(unittest.TestCase):
    def test_every_operator_has_a_distinct_token_type(self) -> None:
        for lexeme, expected_type in OPERATORS:
            with self.subTest(lexeme=lexeme):
                tokens = tokenize(lexeme)
                self.assertEqual(len(tokens), 1)
                self.assertEqual(tokens[0].lexeme, lexeme)
                self.assertEqual(tokens[0].type, expected_type)

    def test_maximal_munch_across_all_operators(self) -> None:
        source = " ".join(lexeme for lexeme, _ in OPERATORS)
        actual = [(token.lexeme, token.type) for token in tokenize(source)]
        self.assertEqual(actual, OPERATORS)


if __name__ == "__main__":
    unittest.main()
