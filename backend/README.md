# SML lexical analyzer

`lexer.py` implements the lexical analyzer defined by the SML programming
language proposal for COSC-303. It requires Python 3.8 or newer and uses only
the Python standard library.

## Command-line usage

Run these commands from the repository root:

```powershell
python -m backend.lexer examples/valid_operators.sml
python -m backend.lexer -c "let x = 5m;"
python -m backend.lexer examples/valid_comments.sml --comments
python -m backend.lexer examples/valid_units.sml --json
Get-Content examples/valid_units.sml | python -m backend.lexer
```

The process exits with status `0` when no lexical errors are found and `1`
when the input contains lexical errors.

## Token categories

The lexer produces the following categories:

- `KEYWORD`, `PRIMITIVE_TYPE`, `NAMED_DIMENSION`, `BOOLEAN_LITERAL`,
  `NOISE_WORD`, and `IDENTIFIER`
- `INTEGER_LITERAL`, `DECIMAL_LITERAL`, `STRING_LITERAL`, and
  `QUANTITY_LITERAL`
- `ASSIGN`, `PLUS_ASSIGN`, `MINUS_ASSIGN`, `MULTIPLY_ASSIGN`, and
  `DIVIDE_ASSIGN`
- `PLUS`, `MINUS`, `MULTIPLY`, `DIVIDE`, `MODULO`, and `POWER`
- `EQUAL`, `NOT_EQUAL`, `LESS_THAN`, `GREATER_THAN`,
  `LESS_THAN_OR_EQUAL`, and `GREATER_THAN_OR_EQUAL`
- `LOGICAL_AND`, `LOGICAL_OR`, `LOGICAL_NOT`, `INCREMENT`, and `DECREMENT`
- `SEMICOLON`, `LPAREN`, `RPAREN`, `LBRACE`, `RBRACE`, `LBRACKET`,
  `RBRACKET`, `COMMA`, and `COLON`
- `COMMENT` when `--comments` is enabled
- `ERROR` for invalid input

Each `Token` stores its category, original lexeme, one-based line and column,
and an optional value. A value may be a parsed number, string contents,
quantity parts, or an error message. Internally, a lexer mark is the tuple
`(absolute position, line, column)` where a lexeme begins.

## Lexical rules

- The lexer uses maximal munch, so the longest valid lexeme wins. For example,
  `+=` is one operator rather than `+` followed by `=`.
- Each operator symbol has a distinct token type. `PLUS` and `MINUS` identify
  the symbols themselves; deciding whether they are unary or binary belongs to
  a future parser.
- Quantity units must be attached to the magnitude. `100m`, `9.58s`, and
  `9.8[m/s^2]` are quantity literals. `100 m` and `9.8 [m/s^2]` become
  separate tokens and are rejected later by the parser.
- The lexer validates the shape and limits of bracketed unit expressions, but
  it does not decide whether a unit identifier is registered. Unit resolution
  happens after parsing.
- Leading `+` and `-` characters are operators, not part of numeric literals.
- Whitespace and comments are discarded unless `--comments` is supplied.
- Identifiers cannot begin with an underscore.
- Numeric literals reject leading zeroes, leading decimal points, and trailing
  decimal points.
- String escape sequences are not supported.
- A lone `&` or `|` is invalid; logical operators are `&&` and `||`.

## Unit-expression grammar

```text
UnitPower       = UnitSymbol [ "^" SignedInteger ]
UnitProduct     = UnitPower { "*" UnitPower }
UnitDenominator = UnitPower | "(" UnitProduct ")"
UnitExpression  = UnitProduct [ "/" UnitDenominator ]
```

The text inside one unit annotation is limited to 128 ASCII characters, eight
written unit-factor occurrences, and exponents from `-16` through `16`.

## Implementation map

The source is organized in this order:

1. Character sets and identifier characters
2. Keywords, primitive types, dimensions, literals, and noise words
3. Operators and delimiters
4. Unit-expression tokenization, parsing, and validation
5. The immutable `Token` data class
6. The stateful `SMLLexer`
7. Table, report, JSON, and command-line output

Within `SMLLexer`, scanning proceeds through low-level cursor helpers, the main
dispatch loop, comments, words, numbers and quantities, strings, and operators.
Number scanning reads the integer portion, an optional fractional portion, and
then an optional attached simple or compound unit. Block comments consume their
opening `/*` before searching for the closing `*/`; strings similarly consume
their opening quote before collecting their contents.

The full language specification is in
`docs/SML_Programming_Language_Proposal.md`.
