# Team Contributions — Mini Compiler

> **Team Members:**  M1 = Shambhavi Jha · M2 = Venkata Shreya · M3 = Yuvaraj Nayak · M4 = Krishna Nagpal

---

## Section 1 — Cross-Contribution Matrix

| Question | Shambhavi Jha (M1) | Venkata Shreya (M2) | Yuvaraj Nayak (M3) | Krishna Nagpal (M4) |
| :--- | :--- | :--- | :--- | :--- |
| **Q1 – Lexical Analysis** | `tokenize` loop, keyword resolution, EOF/LexicalError emission | `_peek`, `_advance`, `_skip_ws`, `WHITESPACE_PATTERN`, source normalization | `TokenType`, `KEYWORDS`, `Token`, `LexicalError` in `tokens.py` | `TOKEN_SPECS`, `LEXICAL_SPEC`, `_err_class`, regex compile; CLI token table in `compiler.py` |
| **Q2 – Grammar & Syntax** | `parse`, `parse_decl`, `parse_stmt`, `parse_assign`, `parse_if`, `parse_while`, `parse_print`, `parse_block` | `parse_expr`, `parse_term`, `parse_factor`, `parse_bool_*`, `parse_rel_expr`, `current`, `advance` | AST dataclasses: `Program`, `Assign`, `IfStmt`, `WhileStmt`, `BinOp`, `RelExpr`, `BoolOr`, `Var`, etc. | `ast_dump`, `_label`, `_children`, `_tree_lines`; CFG strings, derivation text, `run_syntax_analysis` |
| **Q3 – Syntax Error Detection** | `expect`, `_syntax_error_type`, `SyntaxErrorReport` append in `expect` | Error branches in `parse_stmt`, `parse_assign`, `parse_if`, `parse_while`, `parse_print`, `parse_block`, `parse_factor` | `SyntaxErrorReport` dataclass; `_errors` display; `main` phase-gate logic | `run_syntax_analysis` error enumeration; menu-1 error path |
| **Compre Q1 – Parsers** | LL(1) predictive algorithm, ε-reduction, stack trace in `ll1_parser.py` | SLR(1) Shift-Reduce engine, Action/Goto transitions in `slr_parser.py` | FIRST/FOLLOW sets, LL(1) + SLR(1) parsing tables, augmented grammar | CLI integration (Options 4–5), system-wide integration testing |
| **Compre Q2 – Symbol Table** | Symbol table integration into LL(1) flow | Symbol table integration into SLR(1) flow | Memory offset logic (int=4B, float=8B), type-size tracking | `SymbolTable`, `Scope` classes; nested scope management; CLI Option 8 |
| **Compre Q3 – Semantic Analysis** | Use-of-undeclared-variable detection | Multiple-declaration-in-scope detection | Type-mismatch detection (assignment & expressions) | Invalid boolean condition detection; `run_semantic_analysis`; CLI Option — |
| **Compre Q4 – Intermediate Code (TAC)** | `TACGenerator` AST traversal for arithmetic expressions & temporaries | Boolean expression TAC & conditional branching labels | Loop control flow (`WhileStmt`) TAC generation | CLI Option 9 integration; TAC display formatting |
| **Compre Q5 – Optimization & Target Code** | Constant Folding optimization pass in `target_code.py` | `TargetCodeGenerator` pseudo-assembly emission (`MOV`, `ADD`, `CMP`, `JE`) | Jump-label management & optimization correctness verification | CLI Option 10 integration; Optimized TAC + Target Code display |

---

## Section 2 — Per-Question Detailed Contributions

---

### Question 1: Lexical Specification and Tokenization

#### M1 — Shambhavi Jha

| Item | Details |
| :--- | :--- |
| **Function** | Core tokenization loop and token emission |
| **Tasks** | Implemented the main `tokenize()` loop: iterates compiled patterns in priority order, resolves identifiers to keywords via `KEYWORDS.get`, emits `Token` objects, appends `EOF` at end, collects `LexicalError` when no pattern matches |
| **Files** | `modules/lexer.py` |
| **Classes/Functions** | `Lexer.tokenize` (match loop, keyword branch, `errors.append`, EOF emission) |
| **Dataset** | All valid token types in the evaluation program |

#### M2 — Venkata Shreya

| Item | Details |
| :--- | :--- |
| **Function** | Cursor, line/column tracking and whitespace handling |
| **Tasks** | Implemented source normalization in `__init__`, `_peek` for lookahead, `_advance` with newline line-count, `_skip_ws` for spaces/tabs/newlines, `WHITESPACE_PATTERN` |
| **Files** | `modules/lexer.py` |
| **Classes/Functions** | `Lexer.__init__`, `_peek`, `_advance`, `_skip_ws`, `WHITESPACE_PATTERN` |
| **Dataset** | Whitespace and newline sequences across test programs |

#### M3 — Yuvaraj Nayak

| Item | Details |
| :--- | :--- |
| **Function** | Token type definitions and structured payloads |
| **Tasks** | Defined `TokenType` enum (keywords, literals, operators, delimiters, EOF); built `KEYWORDS` map; implemented `Token` and `LexicalError` dataclasses consumed by lexer and compiler driver |
| **Files** | `modules/tokens.py` |
| **Classes/Functions** | `TokenType`, `KEYWORDS`, `Token`, `LexicalError` |
| **Dataset** | Full token vocabulary of the language specification |

#### M4 — Krishna Nagpal

| Item | Details |
| :--- | :--- |
| **Function** | Regex pattern spec, error classification, CLI token display |
| **Tasks** | Authored `TOKEN_SPECS` (float before int, multi-char ops before single-char), `LEXICAL_SPEC` summary, `_err_class` for illegal characters; compiled regexes; implemented `compiler.py` token table (`_tokens`, `_heading`) for Option 2 |
| **Files** | `modules/lexer.py`, `compiler.py` |
| **Classes/Functions** | `TOKEN_SPECS`, `LEXICAL_SPEC`, `_err_class`, `_specs` compile; `compiler._tokens`, `compiler._heading` |
| **Dataset** | Regex patterns for all 30+ token classes |

---

### Question 2: Grammar Design and Syntactic Validation

#### M1 — Shambhavi Jha

| Item | Details |
| :--- | :--- |
| **Function** | Recursive descent for program structure and statements |
| **Tasks** | Implemented `parse`, `parse_decl`, `parse_stmt`, `parse_assign`, `parse_if`, `parse_while`, `parse_print`, `parse_block` — building correct AST nodes for all statement-level constructs |
| **Files** | `modules/parser.py` |
| **Classes/Functions** | `Parser.parse`, `parse_decl`, `parse_stmt`, `parse_assign`, `parse_if`, `parse_while`, `parse_print`, `parse_block` |
| **Dataset** | Declaration, assignment, if-else, while, print constructs in evaluation program |

#### M2 — Venkata Shreya

| Item | Details |
| :--- | :--- |
| **Function** | Expression and boolean/relational parsing |
| **Tasks** | Implemented `parse_expr`, `parse_term`, `parse_factor`, `parse_bool_expr`, `parse_bool_term`, `parse_bool_factor`, `parse_rel_expr`; cursor helpers `current` and `advance` |
| **Files** | `modules/parser.py` |
| **Classes/Functions** | `parse_expr`, `parse_term`, `parse_factor`, `parse_bool_expr`, `parse_bool_term`, `parse_bool_factor`, `parse_rel_expr`, `current`, `advance` |
| **Dataset** | Arithmetic and boolean sub-expressions in evaluation program |

#### M3 — Yuvaraj Nayak

| Item | Details |
| :--- | :--- |
| **Function** | Abstract Syntax Tree node definitions |
| **Tasks** | Defined all AST `@dataclass` nodes: `Program`, `Decl`, `Assign`, `IfStmt`, `WhileStmt`, `PrintStmt`, `Block`, `BoolOr`, `BoolAnd`, `BoolNot`, `RelExpr`, `BinOp`, `UnaryMinus`, `IntLit`, `FloatLit`, `Var` |
| **Files** | `modules/parser.py` |
| **Classes/Functions** | All AST dataclass definitions |
| **Dataset** | Full AST schema for the mini-compiler language |

#### M4 — Krishna Nagpal

| Item | Details |
| :--- | :--- |
| **Function** | AST pretty-printer and CFG/derivation driver |
| **Tasks** | Implemented `ast_dump`, `_label`, `_children`, `_tree_lines`; CFG production strings (`_CFG_INTRO`, `_CFG_PROD`), `print_cfg`, left/right derivation constants, `_print_grammar_and_tree`, `_section`, `run_syntax_analysis` |
| **Files** | `modules/parser.py`, `modules/syntax_analyzer.py` |
| **Classes/Functions** | `ast_dump`, `_label`, `_children`, `_tree_lines`, `print_cfg`, `run_syntax_analysis`, CFG/derivation constants |
| **Dataset** | CFG productions, left/right derivation steps for evaluation program |

---

### Question 3: Syntax Error Detection

#### M1 — Shambhavi Jha

| Item | Details |
| :--- | :--- |
| **Function** | Central token expectation and error type labelling |
| **Tasks** | Implemented `expect` (appends `SyntaxErrorReport` on mismatch), `_syntax_error_type` (human-readable labels for `SEMICOLON`, `RPAREN`, `RBRACE`, etc.) |
| **Files** | `modules/parser.py` |
| **Classes/Functions** | `Parser.expect`, `Parser._syntax_error_type` |
| **Dataset** | Intentional syntax error test programs |

#### M2 — Venkata Shreya

| Item | Details |
| :--- | :--- |
| **Function** | Local parse-path error detection |
| **Tasks** | Added `SyntaxErrorReport` appends in `parse_stmt` (unexpected start), `parse_assign`, `parse_if`, `parse_while`, `parse_print`, `parse_block`, and `parse_factor` (invalid expression) |
| **Files** | `modules/parser.py` |
| **Classes/Functions** | Error branches in `parse_stmt`, `parse_assign`, `parse_if`, `parse_while`, `parse_print`, `parse_block`, `parse_factor` |
| **Dataset** | Malformed statement and expression test cases |

#### M3 — Yuvaraj Nayak

| Item | Details |
| :--- | :--- |
| **Function** | Structured error type and CLI error panel |
| **Tasks** | Defined `SyntaxErrorReport` dataclass; implemented `compiler.py` `_errors` to display lexical and syntax errors in a framed layout; phase-gated `main` so syntax runs only after clean lex |
| **Files** | `modules/tokens.py`, `compiler.py` |
| **Classes/Functions** | `SyntaxErrorReport`; `_errors`, `main` phase-gate |
| **Dataset** | Error report formatting for ≥2 intentional error programs |

#### M4 — Krishna Nagpal

| Item | Details |
| :--- | :--- |
| **Function** | Syntax-analysis driver with error listing |
| **Tasks** | Implemented `run_syntax_analysis` to instantiate `Parser`, call `parse`, enumerate `parser.errors` with numbered messages, and suppress grammar/tree print when errors exist |
| **Files** | `modules/syntax_analyzer.py` |
| **Classes/Functions** | `run_syntax_analysis` |
| **Dataset** | Error enumeration and display for evaluation program |

---

### Compre Q1: Parser Implementation (LL(1) + SLR(1))

#### M1 — Shambhavi Jha

| Item | Details |
| :--- | :--- |
| **Function** | LL(1) predictive table-driven parser |
| **Tasks** | Implemented `LL1Parser` with stack-based predictive algorithm, ε-production handling, and non-trivial stack trace logging for the evaluation program |
| **Files** | `modules/ll1_parser.py` |
| **Classes/Functions** | `LL1Parser`, parsing algorithm, stack trace methods |
| **Dataset** | LL(1) parsing table, evaluation program token stream |

#### M2 — Venkata Shreya

| Item | Details |
| :--- | :--- |
| **Function** | SLR(1) Shift-Reduce parser |
| **Tasks** | Authored `SLRParser` with state-stack management, Shift/Reduce operations, full Action and Goto transitions covering declarations, assignments, and nested control flow |
| **Files** | `modules/slr_parser.py` |
| **Classes/Functions** | `SLRParser`, Action/Goto tables, shift/reduce methods |
| **Dataset** | SLR(1) item sets, evaluation program token stream |

#### M3 — Yuvaraj Nayak

| Item | Details |
| :--- | :--- |
| **Function** | Formal grammar analysis and parsing tables |
| **Tasks** | Computed FIRST and FOLLOW sets for all non-terminals; constructed LL(1) and SLR(1) parsing tables; resolved shift/reduce conflicts; documented augmented grammar |
| **Files** | `modules/grammar_utils.py` |
| **Classes/Functions** | FIRST/FOLLOW computation, table construction logic |
| **Dataset** | Complete grammar non-terminal/terminal sets |

#### M4 — Krishna Nagpal

| Item | Details |
| :--- | :--- |
| **Function** | CLI integration and integration testing |
| **Tasks** | Wired LL(1) (Option 4) and SLR(1) (Option 5) into `compiler.py` menu; performed end-to-end integration testing on the evaluation program |
| **Files** | `compiler.py` |
| **Classes/Functions** | Menu Options 4–5 handlers |
| **Dataset** | Evaluation program, integration test suite |

---

### Compre Q2: Symbol Table and Scope Handling

#### M1 — Shambhavi Jha

| Item | Details |
| :--- | :--- |
| **Function** | Symbol table integration into LL(1) |
| **Tasks** | Connected symbol table insertion/lookup calls into the LL(1) parsing flow |
| **Files** | `modules/ll1_parser.py`, `modules/symbol_table.py` |
| **Classes/Functions** | LL1Parser symbol table hook points |
| **Dataset** | Variable declarations in evaluation program |

#### M2 — Venkata Shreya

| Item | Details |
| :--- | :--- |
| **Function** | Symbol table integration into SLR(1) |
| **Tasks** | Connected symbol table insertion/lookup calls into the SLR(1) parsing flow |
| **Files** | `modules/slr_parser.py`, `modules/symbol_table.py` |
| **Classes/Functions** | SLRParser symbol table hook points |
| **Dataset** | Variable declarations in evaluation program |

#### M3 — Yuvaraj Nayak

| Item | Details |
| :--- | :--- |
| **Function** | Memory layout and type-size logic |
| **Tasks** | Implemented memory offset calculation (int = 4 bytes, float = 8 bytes), type tracking per symbol, offset incrementing across declarations |
| **Files** | `modules/symbol_table.py` |
| **Classes/Functions** | `SymbolTable` offset logic, type-size constants |
| **Dataset** | Mixed int/float variable declarations |

#### M4 — Krishna Nagpal

| Item | Details |
| :--- | :--- |
| **Function** | Core symbol table implementation and CLI |
| **Tasks** | Designed `SymbolTable` and `Scope` classes; implemented `insert`, `lookup`, `push_scope`, `pop_scope`; added CLI Option 8 with nested-scope trace display |
| **Files** | `modules/symbol_table.py`, `compiler.py` |
| **Classes/Functions** | `SymbolTable`, `Scope`, `insert`, `lookup`, `push_scope`, `pop_scope`; Option 8 handler |
| **Dataset** | Nested block scope programs |

---

### Compre Q3: Semantic Analysis

#### M1 — Shambhavi Jha

| Item | Details |
| :--- | :--- |
| **Function** | Undeclared variable detection |
| **Tasks** | Implemented checks for use of variables before declaration; reports variable name, line, and scope context |
| **Files** | `modules/semantic_analyzer.py` |
| **Classes/Functions** | Undeclared-use detection pass |
| **Dataset** | Programs with undeclared variable references |

#### M2 — Venkata Shreya

| Item | Details |
| :--- | :--- |
| **Function** | Duplicate declaration detection |
| **Tasks** | Implemented checks for multiple declarations of the same name in the same scope; generates descriptive error messages |
| **Files** | `modules/semantic_analyzer.py` |
| **Classes/Functions** | Duplicate-declaration detection pass |
| **Dataset** | Programs with re-declared variables in same scope |

#### M3 — Yuvaraj Nayak

| Item | Details |
| :--- | :--- |
| **Function** | Type mismatch detection |
| **Tasks** | Implemented type-compatibility checking for assignments and binary expressions (int vs float operand mismatches) |
| **Files** | `modules/semantic_analyzer.py` |
| **Classes/Functions** | Type-mismatch checking pass |
| **Dataset** | Programs with mixed-type assignments and expressions |

#### M4 — Krishna Nagpal

| Item | Details |
| :--- | :--- |
| **Function** | Boolean condition validation and semantic driver |
| **Tasks** | Implemented invalid boolean condition detection; authored `run_semantic_analysis` orchestrator; integrated semantic phase into compiler pipeline |
| **Files** | `modules/semantic_analyzer.py`, `compiler.py` |
| **Classes/Functions** | `run_semantic_analysis`, boolean-condition checker |
| **Dataset** | Programs with invalid boolean expressions |

---

### Compre Q4: Intermediate Code Generation (TAC)

#### M1 — Shambhavi Jha

| Item | Details |
| :--- | :--- |
| **Function** | Arithmetic expression TAC with temporaries |
| **Tasks** | Implemented AST traversal for `BinOp` and `UnaryMinus` nodes generating three-address instructions with `t1`, `t2`, … temporaries |
| **Files** | `modules/intermediate_code.py` |
| **Classes/Functions** | `TACGenerator`, arithmetic traversal methods |
| **Dataset** | Arithmetic expression sub-trees in evaluation program |

#### M2 — Venkata Shreya

| Item | Details |
| :--- | :--- |
| **Function** | Boolean expressions and conditional branch TAC |
| **Tasks** | Generated TAC for `BoolOr`, `BoolAnd`, `BoolNot`, `RelExpr` nodes and `IfStmt` with `L1`/`L2` jump labels |
| **Files** | `modules/intermediate_code.py` |
| **Classes/Functions** | Boolean and conditional traversal methods in `TACGenerator` |
| **Dataset** | If-else branches in evaluation program |

#### M3 — Yuvaraj Nayak

| Item | Details |
| :--- | :--- |
| **Function** | Loop control flow TAC |
| **Tasks** | Implemented `WhileStmt` TAC generation with loop-start and loop-exit labels, condition check, and back-edge jump |
| **Files** | `modules/intermediate_code.py` |
| **Classes/Functions** | `WhileStmt` traversal in `TACGenerator` |
| **Dataset** | While loop constructs in evaluation program |

#### M4 — Krishna Nagpal

| Item | Details |
| :--- | :--- |
| **Function** | CLI integration and TAC formatting |
| **Tasks** | Wired `TACGenerator` into CLI Option 9; implemented framed display of generated TAC instructions |
| **Files** | `compiler.py` |
| **Classes/Functions** | Option 9 handler, TAC display formatting |
| **Dataset** | Full evaluation program TAC output |

---

### Compre Q5: Optimization and Target Code Generation

#### M1 — Shambhavi Jha

| Item | Details |
| :--- | :--- |
| **Function** | Constant Folding optimization pass |
| **Tasks** | Implemented Constant Folding in `target_code.py` to pre-evaluate arithmetic TAC instructions where both operands are constants, replacing `t1 = 3 * 4` with `t1 = 12` |
| **Files** | `modules/target_code.py` |
| **Classes/Functions** | Constant folding pass in optimization module |
| **Dataset** | TAC with constant operands |

#### M2 — Venkata Shreya

| Item | Details |
| :--- | :--- |
| **Function** | Pseudo-assembly target code emission |
| **Tasks** | Implemented `TargetCodeGenerator` to map optimized TAC to pseudo-assembly instructions: `MOV`, `ADD`, `SUB`, `MUL`, `DIV`, `CMP`, `JE`, `JNE`, `JMP`, `PUSH`/`CALL`/`ADD ESP` for print |
| **Files** | `modules/target_code.py` |
| **Classes/Functions** | `TargetCodeGenerator`, instruction emission methods |
| **Dataset** | Optimized TAC for evaluation program |

#### M3 — Yuvaraj Nayak

| Item | Details |
| :--- | :--- |
| **Function** | Jump label management and optimization verification |
| **Tasks** | Designed consistent jump-label scheme across TAC and target code; verified semantic equivalence between original and optimized output |
| **Files** | `modules/target_code.py` |
| **Classes/Functions** | Label management helpers |
| **Dataset** | Loop and branch programs requiring correct label alignment |

#### M4 — Krishna Nagpal

| Item | Details |
| :--- | :--- |
| **Function** | CLI integration and output formatting |
| **Tasks** | Wired optimization + target code generation into CLI Option 10; implemented framed display of Optimized TAC followed by Pseudo-Assembly target code |
| **Files** | `compiler.py` |
| **Classes/Functions** | Option 10 handler, display formatting |
| **Dataset** | Full evaluation program optimization and target output |

---

## Section 3 — File Summary

| File | Primary Contribution |
| :--- | :--- |
| `modules/tokens.py` | M3: `TokenType`, `Token`, `LexicalError`, `KEYWORDS`; M3 (Q3): `SyntaxErrorReport` |
| `modules/lexer.py` | M1: `tokenize` core loop; M2: position helpers (`_peek`, `_advance`, `_skip_ws`); M4: `TOKEN_SPECS`, `LEXICAL_SPEC`, `_err_class`, regex compile |
| `modules/parser.py` | M1: statement parsers; M2: expression/boolean parsers; M3: AST dataclasses; M4: `ast_dump`, tree helpers; Q3: M1 `expect`, M2 local error branches |
| `modules/syntax_analyzer.py` | M4: CFG strings, derivation constants, `print_cfg`, `_print_grammar_and_tree`, `run_syntax_analysis` |
| `modules/ll1_parser.py` | M1: LL(1) algorithm & stack trace; M3: parsing table entries |
| `modules/slr_parser.py` | M2: SLR(1) algorithm & Shift-Reduce logic; M3: Action/Goto table entries |
| `modules/grammar_utils.py` | M3: FIRST/FOLLOW computation, table construction |
| `modules/symbol_table.py` | M4: `SymbolTable`, `Scope`, insert/lookup/scope management; M3: memory offset & type-size logic; M1/M2: parser hook integration |
| `modules/semantic_analyzer.py` | M1: undeclared-variable pass; M2: duplicate-declaration pass; M3: type-mismatch pass; M4: boolean-condition pass + `run_semantic_analysis` |
| `modules/intermediate_code.py` | M1: arithmetic expression TAC; M2: boolean/conditional TAC; M3: loop control flow TAC; M4: CLI integration |
| `modules/target_code.py` | M1: Constant Folding pass; M2: `TargetCodeGenerator` pseudo-assembly emission; M3: label management |
| `compiler.py` | M4 (Q1): token table UI; M3 (Q3): `_errors`, `main` phase-gate; shared menu shell; M4 (Compre): Options 4–5, 8–10 handlers |

---

## Section 4 — Role Pattern

| Member | Q1 – Lexical Analysis | Q2 – Grammar & Syntax | Q3 – Error Detection | Compre Q1 – Parsers | Compre Q2 – Symbol Table | Compre Q3 – Semantic | Compre Q4 – TAC | Compre Q5 – Target Code |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **M1 Shambhavi Jha** | Tokenize loop & emission | Statement-level parsing | `expect` + error typing | LL(1) algorithm & stack trace | LL(1) symbol table integration | Undeclared variable detection | Arithmetic expression TAC | Constant Folding pass |
| **M2 Venkata Shreya** | Position & whitespace helpers | Expression & boolean parsing | Local error branches in parsers | SLR(1) algorithm & Shift-Reduce | SLR(1) symbol table integration | Duplicate declaration detection | Boolean/conditional branch TAC | Pseudo-assembly emission |
| **M3 Yuvaraj Nayak** | Token model (`tokens.py`) | AST dataclasses | `SyntaxErrorReport` + error UI | FIRST/FOLLOW & parsing tables | Memory offset & type-size logic | Type mismatch detection | Loop control flow TAC | Jump label management |
| **M4 Krishna Nagpal** | Regex spec + token table UI | `ast_dump` + CFG driver | `run_syntax_analysis` error listing | CLI integration & testing | `SymbolTable`/`Scope` core + CLI | Boolean condition check + driver | CLI Option 9 + display | CLI Option 10 + display |

---
