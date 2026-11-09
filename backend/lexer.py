#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any, List, Optional, Tuple

CAP = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
SM = set("abcdefghijklmnopqrstuvwxyz")
ALPHA = CAP | SM
DIGITS = set("0123456789")
SYMBOLS = set('.+-*/%^<>=!&|(){}[];:,"_')
WHITESPACE = set(" \t\r\n")
CHARACTER = ALPHA | DIGITS | SYMBOLS | WHITESPACE
IDENT_REST = ALPHA | DIGITS | {"_"}

KEYWORDS = {
    "let", "const", "fn", "return", "if", "else", "for", "while",
    "break", "continue", "print", "input", "assert", "as",
}
PRIMITIVE_TYPES = {"int", "float", "bool", "text"}
BOOLEAN_LITERALS = {"true", "false"}
NAMED_DIMENSIONS = {"Length", "Mass", "Time", "Force"}
NOISE_WORDS = {"to", "then", "do"}

WORD_CLASSES = {}
for _w in KEYWORDS:
    WORD_CLASSES[_w] = "KEYWORD"
for _w in PRIMITIVE_TYPES:
    WORD_CLASSES[_w] = "PRIMITIVE_TYPE"
for _w in BOOLEAN_LITERALS:
    WORD_CLASSES[_w] = "BOOLEAN_LITERAL"
for _w in NAMED_DIMENSIONS:
    WORD_CLASSES[_w] = "NAMED_DIMENSION"
for _w in NOISE_WORDS:
    WORD_CLASSES[_w] = "NOISE_WORD"

TWO_CHAR_OPERATORS = {
    "+=": "ASSIGNMENT_OPERATOR", "-=": "ASSIGNMENT_OPERATOR",
    "*=": "ASSIGNMENT_OPERATOR", "/=": "ASSIGNMENT_OPERATOR",
    "==": "RELATIONAL_OPERATOR", "!=": "RELATIONAL_OPERATOR",
    "<=": "RELATIONAL_OPERATOR", ">=": "RELATIONAL_OPERATOR",
    "&&": "LOGICAL_OPERATOR", "||": "LOGICAL_OPERATOR",
    "++": "UPDATE_OPERATOR", "--": "UPDATE_OPERATOR",
}
ONE_CHAR_OPERATORS = {
    "=": "ASSIGNMENT_OPERATOR",
    "+": "ARITHMETIC_OPERATOR", "-": "ARITHMETIC_OPERATOR",
    "*": "ARITHMETIC_OPERATOR", "/": "ARITHMETIC_OPERATOR",
    "%": "ARITHMETIC_OPERATOR", "^": "ARITHMETIC_OPERATOR",
    "<": "RELATIONAL_OPERATOR", ">": "RELATIONAL_OPERATOR",
    "!": "LOGICAL_OPERATOR",
}
OPERATOR_START = set("+-*/%^<>=!&|")

DELIMITERS = {
    ";": "SEMICOLON", "(": "LPAREN", ")": "RPAREN",
    "{": "LBRACE", "}": "RBRACE", "[": "LBRACKET", "]": "RBRACKET",
    ",": "COMMA", ":": "COLON",
}

MAX_UNIT_TEXT = 128
MAX_UNIT_FACTORS = 8
MAX_WRITTEN_EXPONENT = 16


class _UnitError(Exception):
    pass


def _unit_tokens(text: str) -> List[Tuple[str, str]]:
    toks: List[Tuple[str, str]] = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c in (" ", "\t"):
            i += 1
        elif c in ALPHA:
            j = i + 1
            while j < n and text[j] in IDENT_REST:
                j += 1
            toks.append(("id", text[i:j]))
            i = j
        elif c in DIGITS:
            j = i + 1
            while j < n and text[j] in DIGITS:
                j += 1
            toks.append(("num", text[i:j]))
            i = j
        elif c in "^*/()-":
            toks.append((c, c))
            i += 1
        else:
            raise _UnitError("invalid character %r" % c)
    return toks


def _describe(tok: Tuple[Optional[str], Optional[str]]) -> str:
    kind, val = tok
    if kind is None:
        return "end of the unit expression"
    if kind == "id":
        return "unit symbol '%s'" % val
    if kind == "num":
        return "number '%s'" % val
    return "'%s'" % val


class _UnitParser:
    def __init__(self, toks: List[Tuple[str, str]]):
        self.toks = toks
        self.i = 0
        self.factors = 0

    def peek(self) -> Tuple[Optional[str], Optional[str]]:
        return self.toks[self.i] if self.i < len(self.toks) else (None, None)

    def parse(self) -> None:
        self.product()
        if self.peek()[0] == "/":
            self.i += 1
            self.denominator()
        kind, val = self.peek()
        if kind is not None:
            self.leftover(kind)
        if self.factors > MAX_UNIT_FACTORS:
            raise _UnitError("more than %d unit-factor occurrences" % MAX_UNIT_FACTORS)

    def leftover(self, kind: str) -> None:
        if kind == "/":
            raise _UnitError("repeated division is invalid (only one top-level '/' is allowed)")
        if kind == "id":
            raise _UnitError("implicit multiplication is invalid; write '*' between units")
        if kind == "num":
            raise _UnitError("numeric scale factors are not allowed inside unit expressions")
        if kind == ")":
            raise _UnitError("unbalanced ')'")
        raise _UnitError("unexpected %s" % _describe(self.peek()))

    def product(self) -> None:
        self.power()
        while self.peek()[0] == "*":
            self.i += 1
            self.power()

    def power(self) -> None:
        kind, _ = self.peek()
        if kind == "num":
            raise _UnitError("numeric scale factors are not allowed inside unit expressions")
        if kind == "(":
            raise _UnitError("parentheses are only allowed around a denominator "
                             "(a grouped unit expression cannot be raised to a power)")
        if kind != "id":
            raise _UnitError("expected a unit symbol but found %s" % _describe(self.peek()))
        self.i += 1
        self.factors += 1
        if self.peek()[0] == "^":
            self.i += 1
            negative = False
            if self.peek()[0] == "-":
                negative = True
                self.i += 1
            kind, val = self.peek()
            if kind != "num":
                raise _UnitError("expected an integer exponent after '^'")
            self.i += 1
            exponent = -int(val) if negative else int(val)
            if not -MAX_WRITTEN_EXPONENT <= exponent <= MAX_WRITTEN_EXPONENT:
                raise _UnitError("written exponent %d is outside -%d..%d"
                                 % (exponent, MAX_WRITTEN_EXPONENT, MAX_WRITTEN_EXPONENT))

    def denominator(self) -> None:
        if self.peek()[0] == "(":
            self.i += 1
            self.product()
            if self.peek()[0] == "/":
                raise _UnitError("nested division is invalid")
            if self.peek()[0] != ")":
                raise _UnitError("expected ')' to close the denominator group")
            self.i += 1
            if self.peek()[0] == "^":
                raise _UnitError("a grouped unit expression cannot be raised to a power")
        else:
            self.power()


def validate_unit_expression(text: str) -> Optional[str]:
    if len(text) > MAX_UNIT_TEXT:
        return "unit annotation is longer than %d characters" % MAX_UNIT_TEXT
    try:
        toks = _unit_tokens(text)
        if not toks:
            return "the unit expression is empty"
        _UnitParser(toks).parse()
    except _UnitError as exc:
        return str(exc)
    return None


@dataclass(frozen=True)
class Token:
    type: str
    lexeme: str
    line: int
    column: int
    value: Any = None


Mark = Tuple[int, int, int]


class SMLLexer:
    def __init__(self, source: str, keep_comments: bool = False):
        self.src = source
        self.keep_comments = keep_comments
        self.pos = 0
        self.line = 1
        self.col = 1

    def _peek(self, k: int = 0) -> str:
        i = self.pos + k
        return self.src[i] if i < len(self.src) else ""

    def _advance(self, n: int = 1) -> None:
        for _ in range(n):
            if self.pos >= len(self.src):
                return
            if self.src[self.pos] == "\n":
                self.line += 1
                self.col = 1
            else:
                self.col += 1
            self.pos += 1

    def _mark(self) -> Mark:
        return (self.pos, self.line, self.col)

    def _make(self, ttype: str, mark: Mark, value: Any = None) -> Token:
        return Token(ttype, self.src[mark[0]:self.pos], mark[1], mark[2], value)

    def _error(self, mark: Mark, message: str) -> Token:
        return self._make("ERROR", mark, message)

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while self.pos < len(self.src):
            ch = self._peek()
            if ch in WHITESPACE:
                self._advance()
                continue

            mark = self._mark()
            nxt = self._peek(1)

            if ch == "/" and nxt == "/":
                tok = self._line_comment(mark)
            elif ch == "/" and nxt == "*":
                tok = self._block_comment(mark)
            elif ch in ALPHA:
                tok = self._word(mark)
            elif ch in DIGITS:
                tok = self._number(mark)
            elif ch == '"':
                tok = self._string(mark)
            elif ch == "_":
                tok = self._bad_underscore(mark)
            elif ch in DELIMITERS:
                self._advance()
                tok = self._make(DELIMITERS[ch], mark)
            elif ch in OPERATOR_START:
                tok = self._operator(mark)
            else:
                self._advance()
                if ch == ".":
                    msg = ("unexpected '.' (leading-dot numbers are not allowed)"
                           if nxt in DIGITS else "unexpected '.'")
                else:
                    msg = "character %r is not part of the SML character set" % ch
                tok = self._error(mark, msg)

            if tok.type == "COMMENT" and not self.keep_comments:
                continue
            tokens.append(tok)
        return tokens

    def _line_comment(self, mark: Mark) -> Token:
        bad: Optional[str] = None
        while self._peek() not in ("", "\n", "\r"):
            ch = self._peek()
            if ch not in CHARACTER and bad is None:
                bad = "character %r is not part of the SML character set" % ch
            self._advance()
        if bad is not None:
            return self._error(mark, bad)
        return self._make("COMMENT", mark)

    def _block_comment(self, mark: Mark) -> Token:
        bad: Optional[str] = None
        self._advance(2)
        while True:
            if self.pos >= len(self.src):
                return self._error(mark, "unterminated block comment: missing '*/'")
            if self._peek() == "*" and self._peek(1) == "/":
                self._advance(2)
                if bad is not None:
                    return self._error(mark, bad)
                return self._make("COMMENT", mark)
            ch = self._peek()
            if ch not in CHARACTER and bad is None:
                bad = "character %r is not part of the SML character set" % ch
            self._advance()

    def _word(self, mark: Mark) -> Token:
        while self._peek() in IDENT_REST:
            self._advance()
        text = self.src[mark[0]:self.pos]
        return self._make(WORD_CLASSES.get(text, "IDENTIFIER"), mark)

    def _bad_underscore(self, mark: Mark) -> Token:
        while self._peek() in IDENT_REST:
            self._advance()
        return self._error(mark, "an identifier cannot begin with an underscore")

    def _number(self, mark: Mark) -> Token:
        problems: List[str] = []

        while self._peek() in DIGITS:
            self._advance()
        int_text = self.src[mark[0]:self.pos]

        is_decimal = False
        if self._peek() == ".":
            if self._peek(1) in DIGITS:
                self._advance()
                while self._peek() in DIGITS:
                    self._advance()
                is_decimal = True
            else:
                self._advance()
                problems.append("trailing-dot numbers such as '5.' are not allowed")
        number_text = self.src[mark[0]:self.pos]

        if len(int_text) > 1 and int_text[0] == "0":
            problems.append("leading zeros are not allowed")

        kind: Optional[str] = None
        unit_text = ""
        nxt = self._peek()
        if nxt in ALPHA:
            kind = "simple"
            start = self.pos
            while self._peek() in IDENT_REST:
                self._advance()
            unit_text = self.src[start:self.pos]
            if unit_text in WORD_CLASSES:
                problems.append("'%s' is a reserved word and cannot be a unit symbol" % unit_text)
        elif nxt == "[":
            kind = "compound"
            self._advance()
            start = self.pos
            while self._peek() not in ("", "]", "\n", "\r"):
                self._advance()
            unit_text = self.src[start:self.pos]
            if self._peek() != "]":
                problems.append("unterminated compound unit: missing ']'")
            else:
                self._advance()
                err = validate_unit_expression(unit_text)
                if err:
                    problems.append("invalid unit expression: " + err)
            unit_text = unit_text.strip()

        if problems:
            return self._error(mark, "; ".join(problems))

        magnitude = float(number_text) if is_decimal else int(number_text)
        if kind is None:
            return self._make("DECIMAL_LITERAL" if is_decimal else "INTEGER_LITERAL",
                              mark, magnitude)
        return self._make("QUANTITY_LITERAL", mark,
                          {"magnitude": magnitude, "unit": unit_text, "form": kind})

    def _string(self, mark: Mark) -> Token:
        self._advance()
        content_start = self.pos
        bad: Optional[str] = None
        while True:
            ch = self._peek()
            if ch == "" or ch in ("\n", "\r"):
                return self._error(mark, "unterminated string literal: missing closing '\"'")
            if ch == '"':
                content = self.src[content_start:self.pos]
                self._advance()
                if bad is not None:
                    return self._error(mark, bad)
                return self._make("STRING_LITERAL", mark, content)
            if ch not in CHARACTER and bad is None:
                bad = "invalid character %r in string literal" % ch
            elif ch == "\\" and bad is None:
                bad = "invalid character '\\' (escape sequences are not supported)"
            self._advance()

    def _operator(self, mark: Mark) -> Token:
        c = self._peek()
        two = c + self._peek(1)
        if two in TWO_CHAR_OPERATORS:
            self._advance(2)
            return self._make(TWO_CHAR_OPERATORS[two], mark)
        if c in ONE_CHAR_OPERATORS:
            self._advance()
            return self._make(ONE_CHAR_OPERATORS[c], mark)
        self._advance()
        return self._error(mark, "'%s' is not an operator; did you mean '%s%s'?" % (c, c, c))


def tokenize(source: str, keep_comments: bool = False) -> List[Token]:
    return SMLLexer(source, keep_comments).tokenize()


def _shorten(text: str, limit: int = 48) -> str:
    text = text.replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t")
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _value_text(tok: Token) -> str:
    if tok.type in ("INTEGER_LITERAL", "DECIMAL_LITERAL"):
        return str(tok.value)
    if tok.type == "STRING_LITERAL":
        return _shorten(tok.value, 30)
    if tok.type == "QUANTITY_LITERAL":
        return "%s x [%s]" % (tok.value["magnitude"], tok.value["unit"])
    return ""


def render_table(tokens: List[Token]) -> str:
    headers = ("#", "Line:Col", "Token", "Lexeme", "Value")
    rows = [
        (str(i), "%d:%d" % (t.line, t.column), t.type, _shorten(t.lexeme), _value_text(t))
        for i, t in enumerate(tokens, 1)
    ]
    widths = [max(len(h), *(len(r[c]) for r in rows)) if rows else len(h)
              for c, h in enumerate(headers)]
    line = "+-" + "-+-".join("-" * w for w in widths) + "-+"

    def fmt(cells: Tuple[str, ...]) -> str:
        return "| " + " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(cells)) + " |"

    out = [line, fmt(headers), line]
    out.extend(fmt(r) for r in rows)
    out.append(line)
    return "\n".join(out)


def render_report(tokens: List[Token]) -> str:
    errors = [t for t in tokens if t.type == "ERROR"]
    good = [t for t in tokens if t.type != "ERROR"]
    parts = [render_table(tokens), "", "Token summary:"]
    for ttype, n in sorted(Counter(t.type for t in good).items()):
        parts.append("  %-20s %d" % (ttype, n))
    parts.append("  %-20s %d" % ("TOTAL (valid)", len(good)))
    parts.append("")
    if errors:
        parts.append("Lexical errors (%d):" % len(errors))
        for t in errors:
            parts.append("  line %d, col %d: %s  [lexeme: %s]"
                         % (t.line, t.column, t.value, _shorten(t.lexeme, 40)))
    else:
        parts.append("No lexical errors.")
    return "\n".join(parts)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Lexical analyzer for SML (Standard Measurement Language).")
    ap.add_argument("file", nargs="?", help="path to an SML source file (omit to read stdin)")
    ap.add_argument("-c", "--code", help="analyze this string instead of a file")
    ap.add_argument("--comments", action="store_true", help="include COMMENT tokens in the output")
    ap.add_argument("--json", action="store_true", help="print tokens and errors as JSON")
    args = ap.parse_args(argv)

    if args.code is not None:
        source = args.code
    elif args.file:
        try:
            with open(args.file, encoding="utf-8", newline="") as fh:
                source = fh.read()
        except OSError as exc:
            print("error: cannot read %s: %s" % (args.file, exc), file=sys.stderr)
            return 2
    elif not sys.stdin.isatty():
        source = sys.stdin.read()
    else:
        ap.print_help()
        return 2

    tokens = tokenize(source, keep_comments=args.comments)
    errors = [t for t in tokens if t.type == "ERROR"]

    if args.json:
        print(json.dumps({"tokens": [asdict(t) for t in tokens if t.type != "ERROR"],
                          "errors": [asdict(t) for t in errors]}, indent=2))
    else:
        print(render_report(tokens))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
