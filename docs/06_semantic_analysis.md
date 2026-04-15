# Module Documentation: `modules/semantic_analyzer.py`

## 1. Module Overview

This module performs semantic checks on top of a successfully parsed AST and an already-built symbol table.

It validates:
- undeclared variable usage (via symbol lookup path; diagnostics sourced from symbol-table phase)
- duplicate declaration handling (sourced from symbol-table phase)
- type mismatch in assignment
- type mismatch in expressions
- invalid boolean conditions
- modulus operator integer-only constraint
- logical operator boolean-operand correctness

---

## 2. Role in Compiler Pipeline

Pipeline order in `compiler.py`:

```text
Source -> Lexer -> Parser -> SymbolTable -> SemanticAnalyzer
```

Semantic analyzer input:
- AST from `modules/parser.py`
- symbol table built by `modules/symbol_table.py`

Semantic analyzer output:
- list of semantic error messages (`ERROR: ...`)

---

## 3. Design Approach

The module uses:
- visitor-style traversal (`_visit_unit`, `_visit_stmt`, `_visit_expr`, `_visit_bool_expr`)
- existing symbol table scopes (no duplicate rebuilding when symbol table is provided)

Key idea:
- symbol table is the source of scope/binding truth
- semantic analyzer focuses on type/rule validation

---

## 4. Semantic Checks (with examples)

## A) Undeclared variables
Example:
```c
x = 5;
```
Symbol-table phase reports undeclared usage. Semantic analyzer avoids duplicate reporting.

## B) Multiple declarations in same scope
Example:
```c
int a;
float a;
```
Handled by symbol-table insertion logic; surfaced in semantic error summary without duplication.

## C) Assignment type mismatch
Example:
```c
int a;
a = 5.7;
```
Error:
`ERROR: Type mismatch in assignment to 'a' (expected int, got float)`

## D) Expression type mismatch
Example:
```c
int a;
float b;
a = b + 2.5;
```
Expression evaluates to `float`; assignment to `int` is flagged.

## E) Invalid boolean condition
Example:
```c
int a;
if (a + 5) { print(a); }
```
Condition is numeric, not boolean.
Error:
`ERROR: Invalid condition in if statement (expected boolean expression)`

## F) Modulus operator restriction
Example:
```c
float f;
int x;
x = f % 2;
```
Error:
`ERROR: Modulus operator requires integer operands`

## G) Logical operators require booleans
Example:
```c
if ((a + 5) && (b < 3)) { ... }
```
Left operand is not boolean.
Error:
`ERROR: Logical operators require boolean operands`

---

## 5. Error Handling Strategy

- Errors are appended to `self.errors` with consistent format:
  - `ERROR: <message>`
- Analyzer does not throw on first semantic issue; it continues traversal where possible.
- Binding errors (undeclared/duplicate declaration) are not duplicated if already emitted by symbol-table phase.

---

## 6. Integration with `compiler.py`

In `main()`:

1. Build symbol table from AST.
2. Extract symbol-table errors from history.
3. Run semantic analyzer with the same symbol table.
4. Combine:
   - symbol-table errors
   - semantic analyzer errors

This gives a clean consolidated semantic report to the user.

---

## 7. Limitations

- Types are currently limited to `int`/`float`/`bool`-style inferred categories.
- No function call argument checking (language currently has no call-expression support).
- Error objects are plain strings, not structured semantic-report dataclasses.

---

## 8. Sample Input / Output

Input:
```c
int a;
a = 5.7;
```

Output:
```text
ERROR: Type mismatch in assignment to 'a' (expected int, got float)
```

Input:
```c
int a;
if (a + 5) {
    print(a);
}
```

Output:
```text
ERROR: Invalid condition in if statement (expected boolean expression)
```
