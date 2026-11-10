# Demo inputs

These files can be pasted into the website or analyzed directly from the
repository root:

```powershell
python -m backend.lexer examples/valid_units.sml
python -m backend.lexer examples/valid_control_flow.sml
python -m backend.lexer examples/valid_comments.sml --comments
python -m backend.lexer examples/invalid_lexical_errors.sml
```

The three `valid_*.sml` files should finish with exit status `0`. The invalid
file intentionally demonstrates several independent lexer errors and should
finish with exit status `1`.

Run the automated example check with:

```powershell
python -m unittest backend.test_examples
```
