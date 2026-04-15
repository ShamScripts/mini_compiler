# Module Documentation: `modules/parser.py`

## 1. Module Overview

This module implements:
- AST node definitions
- AST pretty-printer
- recursive-descent parser for syntax analysis

Pipeline position:
- consumes lexer token stream
- produces AST + syntax errors

---

## 2. Imports

- `from dataclasses import dataclass`  
  Used for compact AST node classes.
- `from typing import List, Optional`  
  Type annotations for AST containers and optional nodes.
- `from .tokens import TokenType, Token, SyntaxErrorReport`  
  Uses token enums and structured syntax-error reporting.

---

## 3. AST Classes

Main AST model:
- program/unit level:
  - `Program`, `Decl`, `FuncDecl`, `Param`
- statements:
  - `Assign`, `IfStmt`, `WhileStmt`, `PrintStmt`, `Block`
- boolean expression nodes:
  - `BoolOr`, `BoolAnd`, `BoolNot`, `RelExpr`
- arithmetic expression nodes:
  - `BinOp`, `UnaryMinus`, `Var`, `IntLit`, `FloatLit`

These classes represent parsed syntax in structured form for later phases.

---

## 4. Parse-Tree Utilities

## `_label(node)`
Maps AST node -> display label text.

## `_children(node)`
Returns child nodes for tree traversal.

## `_tree_lines(node, prefix, is_last)`
Recursive helper building ASCII tree lines.

## `ast_dump(node)`
Entry point to render AST tree as string.

---

## 5. `Parser` Class

## Core state
- `self.tokens`: input token list
- `self.i`: cursor index
- `self.errors`: list of `SyntaxErrorReport`

## Cursor helpers
- `current()`: returns current token (or last token as safety)
- `advance()`: increments index safely

## Error helper
- `_syntax_error_type(tt)`: maps expected token type to friendly error category
- `expect(tt)`: checks current token, consumes on success, appends error on mismatch

---

## 6. Parsing Flow (Recursive Descent)

## `parse()`
Top-level parse:
- loops until EOF
- repeatedly parses units (`parse_unit`)
- returns `Program(units=...)`

## `parse_unit()`
Parses either:
- declaration/function declaration (when starts with `INT/FLOAT`)
- or statement (`parse_stmt`)

## `parse_stmt()`
Dispatches by starting token:
- identifier -> assignment
- `if` -> if statement
- `while` -> while statement
- `print` -> print statement
- `{` -> block

## Specific statement parsers
- `parse_assign()`
- `parse_if()`
- `parse_while()`
- `parse_print()`
- `parse_block()`

---

## 7. Expression and Boolean Parsing

## Arithmetic precedence

Order implemented:
1. `parse_expr` handles `+ -`
2. `parse_term` handles `* / %`
3. `parse_factor` handles identifiers/literals/parenthesized/unary minus

This enforces correct precedence and left-associative chaining.

## Boolean/relational flow
- `parse_bool_expr`: handles `||`
- `parse_bool_term`: handles `&&`
- `parse_bool_factor`: handles `!` and parenthesized bool expression
- `parse_rel_expr`: parses `Expr RelOp Expr`

This ensures conditions are parsed in boolean structure, not as arbitrary arithmetic expressions.

---

## 8. Error Handling

Errors are accumulated in `self.errors` as `SyntaxErrorReport`:
- expected token
- found token
- line/column
- categorized message (missing semicolon, missing brace, etc.)

Parser does not stop at first mismatch in all cases; it continues where possible based on current logic.

---

## 9. Parser Variants in Project

This file is recursive-descent parser.  
Project also includes:
- `modules/ll1_parser.py` (table-driven LL(1))
- `modules/slr_parser.py` (shift-reduce SLR(1))

These are alternative parser demonstrations for evaluation artifacts and traces.

---

## 10. Data Structures Used

- token list + index cursor
- error list
- AST object graph (tree)

No explicit stack here (recursive call stack is used).

---

## 11. Examples

## Valid
```c
int a;
a = -5 + 3 * 2;
if (a < 10) { print(a); } else { print(a); }
```
Expected:
- syntax success
- AST contains `Decl`, `Assign`, `IfStmt`, nested expression nodes

## Invalid
```c
int a
a = 5;
```
Expected:
- syntax error: missing semicolon after declaration

---

## 12. Strengths and Limitations

### Strengths
- clear recursive-descent structure
- explicit precedence handling
- structured AST output
- readable and location-aware syntax errors

### Limitations
- grammar accepted by recursive parser must be kept aligned manually with grammar artifact modules
- no advanced recovery strategy for multiple heavy syntax faults
