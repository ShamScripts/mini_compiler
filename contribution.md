# Contributions

---

#### Member 1: Shambhavi Jha (M1)

- Developed the LL(1) Table-Driven Parser module (`ll1_parser.py`).
- Implemented the stack-based predictive parsing algorithm.
- Created the comprehensive LL(1) mapping for the mini-compiler grammar, ensuring correct handling of left-recursion and operator precedence.
- Designed the detailed stack trace visualization to demonstrate non-trivial input parsing.

#### Member 2: Venkata Shreya (M2)

- Developed the SLR(1) Shift-Reduce Parser module (`slr_parser.py`).
- Implemented the core state-stack management for Shift and Reduce operations.
- Defined the formal grammar rules and Action/Goto transitions for high-fidelity parsing of the evaluation program.
- Integrated the trace logging for shift-reduce steps.

#### Member 3: Yuvaraj Nayak (M3)

- Formalized the Context-Free Grammar (CFG) for the mini-compiler project.
- Calculated the FIRST and FOLLOW sets for symbols (documented in grammar development notes).
- Engineered the Parsing Tables for both LL(1) and SLR(1) architectures.
- Assisted in debugging the parser integration and ensuring success on the evaluation program.

#### Member 4: Krishna Nagpal (M4)

- Designed and implemented the Nested-Scope Symbol Table (`symbol_table.py`).
- Implemented memory offset logic (4 bytes for `int`, 8 bytes for `float`) and type tracking.
- Created the CLI evaluation driver in `compiler.py` with multi-choice testing menu.
- Managed project structure, README documentation, and final system verification for the Compre Evaluation.

## Quick summary

| Question | Shambhavi Jha (M1) | Venkata Shreya (M2) | Yuvaraj Nayak (M3) | Krishna Nagpal (M4) |
| :--- | :--- | :--- | :--- | :--- |
| **Q1** | Lexer `tokenize` loop, token/EOF emission, keyword branch | `Lexer` navigation: `_peek`, `_advance`, `_skip_ws`, `WHITESPACE_PATTERN` | `tokens.py`: `TokenType`, `KEYWORDS`, `Token`, `LexicalError` | `TOKEN_SPECS`, `LEXICAL_SPEC`, `_err_class`, regex compile; `compiler.py` token table |
| **Q2** | `Parser`: program + statements (`parse` … `parse_block`) | `Parser`: expressions + booleans (`parse_expr` … `parse_factor`, `current`/`advance`) | AST dataclasses (`Program`, `Stmt`, `Expr`, …) | `ast_dump` + tree helpers; `syntax_analyzer` CFG + derivations + `run_syntax_analysis` shell |
| **Q3** | `expect`, `_syntax_error_type`, core error recording in `expect` | Syntax error branches in `parse_stmt`, `parse_assign`, `parse_if`, `parse_while`, `parse_print`, `parse_block`, `parse_factor` | `SyntaxErrorReport` in `tokens.py`; `compiler.py` `_errors` syntax section | `run_syntax_analysis` error listing; menu 1 path with syntax output |
| **Compre Q1** | LL(1) Parser algorithm & Stack Trace visualization | SLR(1) Parser algorithm & Shift-Reduce logic | Grammar Engineering, FIRST/FOLLOW & Parsing Tables | CLI Driver integration (Menu 5-6) |
| **Compre Q2** | Symbol table integration into LL(1) | Symbol table integration into SLR(1) | Memory offset logic and type size tracking | `SymbolTable` class & nested scope management (Menu 7) |

---

## Question 1: Lexical Specification and Tokenization

### M1 (Shambhavi Jha) — Tokenization loop and emission

| Item | Details |
| :--- | :--- |
| **Function** | Main lexical scan and token stream construction |
| **Tasks** | Implemented the core `tokenize()` loop: skip whitespace, try each compiled pattern in priority order, emit `Token` with correct `TokenType` (including keyword resolution for `ID` matches), append `EOF`, collect `LexicalError` entries when no pattern matches. |
| **Files** | `modules/lexer.py` |
| **Classes/Functions** | `Lexer.tokenize` (matching loop, `KEYWORDS.get` branch, `errors.append`, final `EOF`) |

### M2 (Venkata Shreya) — Position and input helpers

| Item | Details |
| :--- | :--- |
| **Function** | Cursor, line/column, and whitespace handling |
| **Tasks** | Implemented source normalization in `__init__`, `_peek`, `_advance` with newline handling, `_skip_ws` for spaces/tabs/newlines, and `WHITESPACE_PATTERN` so the tokenizer advances correctly through the source. |
| **Files** | `modules/lexer.py` |
| **Classes/Functions** | `Lexer.__init__`, `_peek`, `_advance`, `_skip_ws`, `WHITESPACE_PATTERN` |

### M3 (Yuvaraj Nayak) — Token model and keyword map

| Item | Details |
| :--- | :--- |
| **Function** | Token types and structured token/error payloads |
| **Tasks** | Defined `TokenType` for keywords, literals, operators, delimiters, `EOF`; built `KEYWORDS` map; implemented `Token` and `LexicalError` dataclasses used by the lexer and driver. |
| **Files** | `modules/tokens.py` |
| **Classes/Functions** | `TokenType`, `KEYWORDS`, `Token`, `LexicalError` |

### M4 (Krishna Nagpal) — Regex spec, patterns, driver display

| Item | Details |
| :--- | :--- |
| **Function** | Pattern ordering, error classification, CLI token table |
| **Tasks** | Authored `TOKEN_SPECS` (float before int, multi-char operators before single-char), `LEXICAL_SPEC` summary, `_err_class` for bad characters; compiled regexes in `Lexer.__init__`; implemented `compiler.py` token stream table (`_tokens`, `_heading`) for menu option 2. |
| **Files** | `modules/lexer.py`, `compiler.py` |
| **Classes/Functions** | `TOKEN_SPECS`, `LEXICAL_SPEC`, `_err_class`, `_specs` compile; `compiler._tokens`, `compiler._heading` |

---

## Question 2: Grammar Design and Syntactic Validation

### M1 (Shambhavi Jha) — Program and statement parsing

| Item | Details |
| :--- | :--- |
| **Function** | Recursive descent for declarations and statements |
| **Tasks** | Implemented `parse`, `parse_decl`, `parse_stmt`, `parse_assign`, `parse_if`, `parse_while`, `parse_print`, `parse_block` so the grammar’s top-level and statement structure is recognized and AST nodes are built. |
| **Files** | `modules/parser.py` |
| **Classes/Functions** | `Parser.parse`, `parse_decl`, `parse_stmt`, `parse_assign`, `parse_if`, `parse_while`, `parse_print`, `parse_block` |

### M2 (Venkata Shreya) — Expression and boolean parsing

| Item | Details |
| :--- | :--- |
| **Function** | Precedence and boolean/relational layer |
| **Tasks** | Implemented `parse_expr`, `parse_term`, `parse_factor`, `parse_bool_expr`, `parse_bool_term`, `parse_bool_factor`, `parse_rel_expr`; token cursor `current` and `advance` for ordered consumption. |
| **Files** | `modules/parser.py` |
| **Classes/Functions** | `parse_expr`, `parse_term`, `parse_factor`, `parse_bool_expr`, `parse_bool_term`, `parse_bool_factor`, `parse_rel_expr`, `current`, `advance` |

### M3 (Yuvaraj Nayak) — AST data model

| Item | Details |
| :--- | :--- |
| **Function** | Abstract syntax tree node types |
| **Tasks** | Defined dataclasses for `Program`, declarations, statements, boolean and arithmetic expressions (`Assign`, `IfStmt`, `WhileStmt`, `PrintStmt`, `Block`, `BoolOr`, `BoolAnd`, `BoolNot`, `RelExpr`, `BinOp`, literals, `Var`, etc.). |
| **Files** | `modules/parser.py` |
| **Classes/Functions** | AST `@dataclass` definitions from `Program` through `UnaryMinus` |

### M4 (Krishna Nagpal) — Tree printing and syntax-analyzer driver

| Item | Details |
| :--- | :--- |
| **Function** | AST pretty-print and CFG/derivation presentation |
| **Tasks** | Implemented `ast_dump`, `_label`, `_children`, `_tree_lines`; CFG strings (`_CFG_INTRO`, `_CFG_PROD`), `print_cfg`, left/right derivation text (`_LEFT`, `_RIGHT`), `_print_grammar_and_tree`, `_section`, and `run_syntax_analysis` orchestration for phase-2 output. |
| **Files** | `modules/parser.py`, `modules/syntax_analyzer.py` |
| **Classes/Functions** | `ast_dump`, `_label`, `_children`, `_tree_lines`; `print_cfg`, `_print_grammar_and_tree`, `run_syntax_analysis`, CFG/derivation constants |

---

## Question 3: Syntax Error Detection

### M1 (Shambhavi Jha) — Central expectation and error typing

| Item | Details |
| :--- | :--- |
| **Function** | Missing-token messages and `expect` |
| **Tasks** | Implemented `expect`, `_syntax_error_type` (human-readable error labels for `SEMICOLON`, `RPAREN`, `RBRACE`, etc.), and append of `SyntaxErrorReport` when the current token does not match the expected type. |
| **Files** | `modules/parser.py` |
| **Classes/Functions** | `Parser.expect`, `Parser._syntax_error_type` |

### M2 (Venkata Shreya) — Local parse-path error reporting

| Item | Details |
| :--- | :--- |
| **Function** | Unexpected-token and invalid-expression handling in parsers |
| **Tasks** | Added syntax error reports in `parse_stmt` (unexpected statement start), `parse_assign`, `parse_if`, `parse_while`, `parse_print`, `parse_block`, and `parse_factor` (invalid expression) so failures surface with line/column without relying only on `expect`. |
| **Files** | `modules/parser.py` |
| **Classes/Functions** | `parse_stmt`, `parse_assign`, `parse_if`, `parse_while`, `parse_print`, `parse_block`, `parse_factor` (branches that append `SyntaxErrorReport`) |

### M3 (Yuvaraj Nayak) — Error type definition and CLI error view

| Item | Details |
| :--- | :--- |
| **Function** | Structured syntax error type and menu error panel |
| **Tasks** | Defined `SyntaxErrorReport` dataclass; implemented `compiler.py` `_errors` to print lexical and syntax errors in a framed layout; wired `main` so syntax phase runs only when there are no lexical errors. |
| **Files** | `modules/tokens.py`, `compiler.py` |
| **Classes/Functions** | `SyntaxErrorReport`; `_errors`, relevant branches in `main` |

### M4 (Krishna Nagpal) — Syntax-analysis entry and error listing

| Item | Details |
| :--- | :--- |
| **Function** | Phase-2 driver when reporting multiple syntax issues |
| **Tasks** | Implemented `run_syntax_analysis` to instantiate `Parser`, call `parse`, enumerate `parser.errors` with numbered messages, and skip full grammar/tree print when errors exist. |
| **Files** | `modules/syntax_analyzer.py` |
| **Classes/Functions** | `run_syntax_analysis` |

### Compre Evaluation: Advanced Parsing and Semantics

### Compre Member 1: Shambhavi Jha (M1)

- **Tasks**: Developed the `LL1Parser` in `modules/ll1_parser.py` using a predictive table-driven approach. Defined the comprehensive parsing table encompassing all terminal/non-terminal mappings for the mini-compiler grammar. Ensured full ε-reduction support and non-trivial stack trace logging.

### Compre Member 2: Venkata Shreya (M2)

- **Tasks**: Authored the `SLRParser` in `modules/slr_parser.py`. Implemented a robust Shift-Reduce engine with a complete set of states and grammar rules. Engineered the Action and Goto transitions specifically covering declarations, assignments, and nested control flow (while/if) for the evaluation program.

### Compre Member 3: Yuvaraj Nayak (M3)

- **Tasks**: Conducted formal grammar analysis, calculating FIRST and FOLLOW sets to resolve Shift/Reduce conflicts in the SLR parser and fill the LL(1) table. Documented the augmented grammar and ensured operator precedence (MUL > PLUS) was correctly reflected in the table entries.

### Compre Member 4: Krishna Nagpal (M4)

- **Tasks**: Designed the `SymbolTable` and `Scope` modules for nested block handling. Expanded `compiler.py` to include a full evaluation suite (Options 4-6) and performed system-wide integration testing to ensure the parsers and symbol table work in concert on the final evaluation code.

---

## File summary

| File | Primary contributors (shared work) |
| :--- | :--- |
| `modules/tokens.py` | M3 (`TokenType`, `Token`, `LexicalError`, `KEYWORDS`); M3 Q3 (`SyntaxErrorReport`) |
| `modules/lexer.py` | M1 (`tokenize` core), M2 (position helpers), M4 (`TOKEN_SPECS`, `LEXICAL_SPEC`, `_err_class`) |
| `modules/parser.py` | M1 (statements), M2 (expressions/booleans), M3 (AST classes), M4 (`ast_dump`); Q3: M1 (`expect`), M2 (local errors) |
| `modules/ll1_parser.py` | M1 (algorithm), M3 (parsing tables) |
| `modules/slr_parser.py` | M2 (algorithm), M3 (parsing tables) |
| `modules/symbol_table.py` | M4 (nested scopes & offsets) |
| `modules/syntax_analyzer.py` | M4 (CFG, derivations, `run_syntax_analysis`, formatting) |
| `compiler.py` | M4 Q1 (`_tokens`); M3 Q3 (`_errors`, `main`); shared menu shell; M4 Compre (Menu 5-7) |

---

## Role pattern

| Member | Q1 | Q2 | Q3 | Compre |
| :--- | :--- | :--- | :--- | :--- |
| M1 | Tokenize loop & emission | Statements parsing | `expect` + error typing | LL(1) & Stack Trace |
| M2 | Position & whitespace helpers | Expression/boolean parsing | Local error branches in parsers | SLR(1) & Shift-Reduce |
| M3 | Token model (`tokens.py`) | AST dataclasses | `SyntaxErrorReport` + `_errors` UI | Grammar & Tables |
| M4 | Regex spec + token table UI | `ast_dump` + syntax_analyzer CFG/driver | `run_syntax_analysis` error listing | Symbol Table & CLI |

---
