# Mini Compiler - Formal Lexical Specification

## 1) Scope

This lexical specification defines tokenization rules for the prescribed core language used in `evaluation_program.txt`.

Supported language constructs:
- data types: `int`, `float`
- control constructs: `if`, `else`, `while`
- output construct: `print`
- identifiers, integer and float literals
- arithmetic, relational, and boolean operators
- delimiters for statements, expressions, and blocks

## 2) Token Classes and Regular Expressions

| Token Class | Token Name(s) | Regular Expression / Lexeme Pattern |
|---|---|---|
| Keyword | `INT` | `int` |
| Keyword | `FLOAT` | `float` |
| Keyword | `IF` | `if` |
| Keyword | `ELSE` | `else` |
| Keyword | `WHILE` | `while` |
| Keyword | `PRINT` | `print` |
| Identifier | `IDENTIFIER` | `[A-Za-z_][A-Za-z0-9_]*` |
| Integer literal | `INT_LITERAL` | `\d+` |
| Float literal | `FLOAT_LITERAL` | `\d+\.\d+` |
| Assignment operator | `ASSIGN` | `=` |
| Arithmetic operator | `PLUS` | `\+` |
| Arithmetic operator | `MINUS` | `-` |
| Arithmetic operator | `MUL` | `\*` |
| Arithmetic operator | `DIV` | `/` |
| Arithmetic operator | `MOD` | `%` |
| Relational operator | `LT` | `<` |
| Relational operator | `GT` | `>` |
| Relational operator | `LE` | `<=` |
| Relational operator | `GE` | `>=` |
| Relational operator | `EQ` | `==` |
| Relational operator | `NE` | `!=` |
| Boolean operator | `AND` | `&&` |
| Boolean operator | `OR` | `\|\|` |
| Boolean operator | `NOT` | `!` |
| Delimiter | `SEMICOLON` | `;` |
| Delimiter | `LBRACE` | `\{` |
| Delimiter | `RBRACE` | `\}` |
| Delimiter | `LPAREN` | `\(` |
| Delimiter | `RPAREN` | `\)` |
| End marker | `EOF` | end of file sentinel |

## 3) Whitespace Handling

- Ignored separators: spaces, tabs, and newlines.
- Whitespace contributes to line and column tracking for error reporting.

## 4) Matching Priority (Deterministic Scan Order)

The lexer scans left-to-right and applies ordered matching to avoid ambiguity:
1. `FLOAT_LITERAL` before `INT_LITERAL`
2. multi-character operators before single-character operators:
   - `<=`, `>=`, `==`, `!=`, `&&`, `||`
3. identifiers are keyword-resolved post-match (`int` -> `INT`, etc.)

## 5) Lexical Error Specification

On a non-matching character, lexer emits a `LexicalError` with:
- error type
- expected token description
- found character
- line and column

Error categories:
- malformed float
- unsupported/invalid operator
- illegal character (not in language)

## 6) Implementation Reference

Primary implementation files:
- `modules/lexer.py`
- `modules/tokens.py`

This specification is aligned with the lexer used by the parser pipeline in `compiler.py`.
