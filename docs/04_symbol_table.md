# Module Documentation: `modules/symbol_table.py`

## 1. Module Overview

This module builds and manages the compiler symbol table with nested scopes.

Pipeline position:
- runs after parsing (AST is required)
- produces scoped bindings and scope/binding diagnostics

Main responsibilities:
- symbol insertion and lookup
- nested scope entry/exit
- shadowing behavior
- duplicate declaration detection
- undeclared usage detection during AST traversal
- per-scope offset assignment

---

## 2. Imports

- `from dataclasses import dataclass`  
  Used for `Symbol`.
- `from typing import Dict, List, Optional`  
  Type hints for symbol maps, children, optional references.
- `from . import parser as ast_nodes`  
  Uses parser AST classes (`Decl`, `Assign`, `IfStmt`, etc.) during traversal.

---

## 3. Classes and Functions

## `Symbol` (dataclass)

Fields:
- `name`
- `kind` (`var`, `fun`, `arg`)
- `type`
- `scope_level`
- `offset`

Method:
- `__str__()` for debug display.

---

## `Scope`

Fields:
- `level`
- `name`
- `symbols: Dict[str, Symbol]`
- `parent`
- `children`
- `next_offset`

Methods:
- `insert(symbol) -> bool`  
  Inserts symbol in current scope only (duplicate name in same scope -> fail).
- `lookup(name) -> Optional[Symbol]`  
  Looks up current scope only.

---

## `SymbolTable`

### Constructor
- creates global root scope
- sets `current_scope`
- initializes history log

### Scope operations
- `enter_scope(name)`  
  Creates child scope and moves into it.
- `exit_scope()`  
  Moves to parent scope.

### Symbol operations
- `insert(name, symbol_type, kind="var") -> bool`
  - computes size (`int=4`, `float=8`, non-var=0)
  - uses scope-local `next_offset`
  - logs success/error
- `lookup(name) -> Optional[Symbol]`
  - searches current scope outward via parent chain

### Reporting
- `dump()`  
  Prints linear operation history.
- `print_multi_tables()`  
  Prints all scope tables recursively.

### AST build entry
- `build_from_ast(ast)`  
  Starts traversal and logging.

### AST traversal helpers
- `_visit_program(program)`
- `_visit_unit(unit)`
- `_visit_stmt(stmt)`
- `_visit_block(block, name)`
- `_visit_bool_expr(node)`
- `_visit_expr(node)`
- `_print_scope_tables_recursive(scope)`

---

## 4. Core Logic (Step-by-step)

1. Start with global scope.
2. Traverse AST nodes top-down.
3. On declarations/functions/parameters:
   - insert symbols into current scope.
4. On block/function entry:
   - create and enter child scope.
5. On block/function exit:
   - return to parent scope.
6. On variable usage:
   - resolve by nearest scope lookup.
7. Log each operation and each binding error.

---

## 5. Scope Tree Diagram

```text
Global (level 0)
├── func f (level 1)
│   ├── if-block (level 2)
│   └── while-block (level 2)
└── block (level 1)
    └── block (level 2)
```

Actual tree shape depends on source program structure.

---

## 6. Shadowing Example

```c
int x;
{
    int x;   // shadows outer x
    x = 5;   // resolves inner x
}
x = 1;       // resolves outer x
```

Reason:
- lookup searches from current scope upward.

---

## 7. Duplicate Declaration Example

```c
int a;
float a;   // same scope duplicate
```

Behavior:
- second `insert` fails in current scope map
- history logs:
  - `ERROR: Multiple declaration of 'a' in scope ...`

---

## 8. Offset Example

Scope-local allocation example:

| Declaration | Type  | Offset | Next Offset |
|---|---|---:|---:|
| `int a;`   | int   | 0  | 4  |
| `float b;` | float | 4  | 12 |
| `int c;`   | int   | 12 | 16 |

Offsets reset per scope because each `Scope` has its own `next_offset`.

---

## 9. AST Traversal Explanation

Traversal is structural and node-driven:

- `Decl` -> insert variable
- `FuncDecl` -> insert function; enter function scope; insert param; traverse body
- `Assign` -> lookup left side; traverse right expression
- `IfStmt`/`WhileStmt` -> traverse condition + nested blocks
- `Block` -> enter/visit/exit scope
- expressions -> resolve variable uses recursively

This ensures symbol table state reflects actual parsed program structure.

---

## 10. Error Handling

Detected in this module:
- duplicate declarations in same scope
- undeclared identifier usage in assignments/expressions

All are logged in `history`, then surfaced by driver logic.

---

## 11. Data Structures Used

- scope tree (`Scope` parent/children links)
- per-scope symbol dictionary
- linear history log list
- recursive AST traversal call stack

---

## 12. Strengths and Limitations

### Strengths
- clear scope-tree model
- supports shadowing and nested block lookup
- useful logs for viva/demo
- built from AST (real program structure)

### Limitations
- diagnostics are history-string based (not separate typed error objects)
- function signatures stored as plain strings
