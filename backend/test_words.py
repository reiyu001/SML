import unittest

from backend.lexer import tokenize


FIXED_WORDS = [
    ("let", "LET"),
    ("const", "CONST"),
    ("fn", "FN"),
    ("return", "RETURN"),
    ("if", "IF"),
    ("else", "ELSE"),
    ("for", "FOR"),
    ("while", "WHILE"),
    ("break", "BREAK"),
    ("continue", "CONTINUE"),
    ("print", "PRINT"),
    ("input", "INPUT"),
    ("assert", "ASSERT"),
    ("as", "AS"),
    ("int", "TYPE_INT"),
    ("float", "TYPE_FLOAT"),
    ("bool", "TYPE_BOOL"),
    ("text", "TYPE_TEXT"),
    ("true", "TRUE"),
    ("false", "FALSE"),
    ("Length", "DIMENSION_LENGTH"),
    ("Mass", "DIMENSION_MASS"),
    ("Time", "DIMENSION_TIME"),
    ("Force", "DIMENSION_FORCE"),
    ("to", "TO"),
    ("then", "THEN"),
    ("do", "DO"),
]


class FixedWordTokenTests(unittest.TestCase):
    def test_every_fixed_word_has_a_distinct_token_type(self) -> None:
        source = " ".join(lexeme for lexeme, _ in FIXED_WORDS)
        actual = [(token.lexeme, token.type) for token in tokenize(source)]
        self.assertEqual(actual, FIXED_WORDS)

    def test_similar_user_defined_names_remain_identifiers(self) -> None:
        source = "letter integer truthful length mass timing forceful todo"
        tokens = tokenize(source)
        self.assertTrue(tokens)
        self.assertTrue(all(token.type == "IDENTIFIER" for token in tokens))

    def test_fixed_words_remain_case_sensitive(self) -> None:
        source = "Let TRUE length"
        tokens = tokenize(source)
        self.assertTrue(all(token.type == "IDENTIFIER" for token in tokens))


if __name__ == "__main__":
    unittest.main()
