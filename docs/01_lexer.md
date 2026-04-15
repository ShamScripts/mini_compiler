# Module Documentation: `modules/lexer.py`

## 1. Module Overview

The lexer scans source text and converts it to a sequence of tokens consumed by the parser.

- Pipeline position: **first stage**
- Input: source code string
- Output:
  - `list[Token]`
  - `list[LexicalError]`

---

## 2. Imports

- `import re`  
  Used for regex-based token matching.
- `from .tokens import TokenType, Token, LexicalError, KEYWORDS`  
  Uses shared token enums/data classes and keyword map.

---

## 3. Constants and Helpers

## `VALID_DESC`
Message used in lexical error diagnostics to indicate expected valid token categories.

## `LEXICAL_SPEC`
Human-readable lexical specification summary:
- keywords
- identifier regex
- integer/float regex
- operators
- delimiters

## `_err_class(ch: str) -> tuple[str, str]`
Classifies invalid character into an error category:
- malformed float hint
- illegal character
- invalid/unsupported operator

Returns `(error_type, expected_description)`.

---

## 4. `Lexer` Class

## Purpose
Implements scanner logic with positional tracking (`line`, `column`).

## Class attributes

### `TOKEN_SPECS`
Ordered token definitions. Order matters:
- float before int
- multi-character operators before single-character operators

### `WHITESPACE_PATTERN`
Regex for spaces/tabs.

## `__init__(source: str)`
- normalizes newlines (`\r\n`, `\r` -> `\n`)
- initializes cursor fields:
  - `pos`
  - `line`
  - `column`
- precompiles regex specs

## `_peek() -> str`
Returns current character or empty string at EOF.

## `_advance(text: str) -> None`
Moves cursor over matched text while updating:
- line count on `\n`
- column count for non-newline characters

## `_skip_ws() -> None`
Consumes whitespace and newlines between tokens.

## `tokenize() -> tuple[list[Token], list[LexicalError]]`
Main scanning loop:
1. skip whitespace
2. attempt regex match using ordered specs
3. if matched:
   - create `Token`
   - convert ID lexeme to keyword token if present in `KEYWORDS`
4. if no match:
   - create `LexicalError`
   - advance by one character
5. append `EOF` token at end

---

## 5. Token Categories (Implemented)

- Keywords: `int`, `float`, `if`, `else`, `while`, `print`
- Identifier: `[A-Za-z_][A-Za-z0-9_]*`
- Integer literal: `\d+`
- Float literal: `\d+\.\d+`
- Operators:
  - arithmetic: `+ - * / %`
  - assignment: `=`
  - relational: `< > <= >= == !=`
  - boolean: `&& || !`
- Delimiters: `; { } ( )`

---

## 6. Tokenization Strategy

- **Left-to-right scanning**
- **Longest-valid by ordering**, not by global backtracking
- **Prefix matching** from current cursor
- **Maximal valid unit per token class order**

Important case (`2value`):
- tokenized as `INT_LITERAL("2")` + `IDENTIFIER("value")`
- rejected later by parser as syntax error in declaration context

This is explicitly documented in code comments.

---

## 7. Data Structures Used

- `list` for token stream
- `list` for lexical errors
- compiled regex list for token matching
- dictionary (`KEYWORDS`) for ID -> keyword remapping

---

## 8. Examples

## Valid
```c
int x;
x = 10;
```
Expected:
- no lexical errors
- tokens include `INT IDENTIFIER SEMICOLON IDENTIFIER ASSIGN INT_LITERAL SEMICOLON EOF`

## Invalid
```c
int a;
a = 5 @ 3;
```
Expected:
- lexical error on `@` with location

---

## 9. Error Handling

Detected and reported:
- illegal characters
- unsupported operator characters
- malformed float-style punctuation context

Each `LexicalError` includes:
- error type
- expected text
- offending character
- line/column

---

## 10. Strengths and Limitations

### Strengths
- clean, deterministic regex scanner
- precise line/column tracking
- robust token ordering for ambiguous operators
- explicit lexical error list (does not crash on first bad character)

### Limitations
- no comment syntax handling
- no string/char literals (not required by this language)
- `2value` treated as syntax-phase invalid, not lexical-phase invalid token
