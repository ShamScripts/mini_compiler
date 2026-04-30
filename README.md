# mini_compiler

**Mini Compiler - CS F363 (Python)**

Compiler construction project for CS F363, designed as a step-by-step implementation of core compiler phases.

---

## Goal

The goal was to build the full pipeline step by step:
- **Lexical analysis**
- **Syntax analysis**
- **Semantic analysis + symbol table**
- **Intermediate code (TAC)**
- **Basic optimisation + pseudo assembly**

---

## Implementation Status

| Phase | Status |
|---|---|
| Lexical Analysis | Implemented |
| Syntax Analysis (Recursive Descent + AST) | Implemented |
| LL(1) Parser Evaluation | Implemented |
| SLR(1) Parser Evaluation | Implemented |
| FIRST/FOLLOW + Parsing Tables | Implemented |
| Symbol Table with Nested Scopes | Implemented |
| Semantic Analysis | Implemented |
| TAC Generation | Implemented |
| Optimization | Implemented |
| Target/Pseudo Assembly Generation | Implemented |

---

## Architecture Snapshot

```text
Source Program
   |
   v
Lexer
   |
   v
Token Stream
   |
   v
Parser (AST)
   |
   v
Symbol Table (Scoped Bindings)
   |
   v
Semantic Analyzer
```

Supporting parser-evaluation path:
- LL(1) stack trace
- SLR shift/reduce trace
- FIRST/FOLLOW and table construction materials

---

## Project Structure

### Root
- `compiler.py` - main entry point (menu-driven compiler runner)
- `README.md` - project overview and run/demo guide
- `contribution.md` - team contribution details

### `reports/`
- `lexical_specification.md` - formal lexical specification artifact

### `docs/`
- `00_overall_compiler.md`
- `01_lexer.md`
- `02_parser.md`
- `03_grammar.md`
- `04_symbol_table.md`
- `05_compiler_driver.md`
- `06_semantic_analysis.md`

### `testPrograms/`
- `evaluation_program.txt` - official evaluation program
- `demo.txt` - integrated demo program
- `Q1_Lexical/` ... `Q8_Optimization_TargetCode/` - question-wise categorized tests

### `modules/`
- `tokens.py` - token enums + error/report dataclasses
- `lexer.py` - lexical analyzer (regex-based scanner)
- `parser.py` - recursive-descent parser + AST node model
- `grammar_utils.py` - CFG, FIRST/FOLLOW, LL(1)/SLR table generation
- `ll1_parser.py` - LL(1) parser with trace
- `slr_parser.py` - SLR parser with trace
- `syntax_analyzer.py` - CFG/derivation/parse-tree display utilities
- `symbol_table.py` - AST-driven scoped symbol table
- `semantic_analyzer.py` - semantic checks using AST + symbol table
- `tac_generator.py` - planned module (not implemented yet)
- `optimizer.py` - planned module (not implemented yet)
- `target_codegen.py` - planned module (not implemented yet)

---

## Quick Start

Run with default source:

```bash
python compiler.py
```

Run with explicit file:

```bash
python compiler.py testPrograms/evaluation_program.txt
```

---

## Demo Flow (Evaluator-Friendly)

Use this sequence during viva/demo:

1. Run `testPrograms/evaluation_program.txt`
2. Option `2` -> token stream
3. Option `3` -> AST
4. Option `1` -> lexical/syntax/semantic summary
5. Option `8` -> symbol table trace + scoped tables
6. Options `4`, `5`, `7` -> LL(1)/SLR traces + FIRST/FOLLOW/tables
7. Option `9` -> TAC
8. Option `10` -> optimize target code

Error-case demonstration:
- Syntax errors: `testPrograms/Q3_SyntaxErrors/`
- Semantic errors: `testPrograms/Q6_Semantic/`

---

## Contributors

- Shambhavi Jha [2023A7PS0009U]
- Venkata Shreya Vella [2023A7PS0096U]
- Yuvaraj Nayak [2023A7PS0006U]
- Krishna Nagpal [2023A7PS0321U]
