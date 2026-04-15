# Mini Compiler: Overall Documentation

## 1. Introduction

This project is a mini compiler for a small imperative language.  
Current implemented pipeline (as visible in code) is:

- Source program input
- Lexical analysis (`modules/lexer.py`)
- Syntax analysis and AST construction (`modules/parser.py`)
- Symbol table construction with scoped bindings (`modules/symbol_table.py`)
- Additional parser artifacts: LL(1)/SLR parsing, FIRST/FOLLOW, parsing tables

Main entry point: `compiler.py`.

---

## 2. Language Specification (Implemented)

### Data types
- `int`
- `float`

### Supported constructs
- variable declaration
- assignment statement
- arithmetic expressions: `+`, `-`, `*`, `/`, `%`
- relational operators: `<`, `>`, `<=`, `>=`, `==`, `!=`
- boolean operators: `&&`, `||`, `!`
- `if-else`
- `while`
- block structure using `{ }`
- `print(...)`

---

## 3. Compiler Pipeline

## Stage A: Lexer
- Input: raw source code text
- Output: token stream (`Token` list) + lexical errors (`LexicalError` list)
- Module: `modules/lexer.py`

## Stage B: Parser
- Input: token stream
- Output: AST (`Program` root) + syntax errors (`SyntaxErrorReport` list)
- Module: `modules/parser.py`

## Stage C: Symbol Table
- Input: AST
- Output: scope tree + symbol entries + symbol-table history/errors
- Module: `modules/symbol_table.py`

### Data flow summary
- Lexer produces tokens
- Parser consumes lexer tokens and builds AST
- Symbol table traverses AST and builds scoped bindings

---

## 4. Architecture Diagram (Text)

```text
Source Code
   |
   v
Lexer (regex-based scanning)
   |
   v
Token Stream + Lexical Errors
   |
   v
Parser (recursive descent)
   |
   v
AST + Syntax Errors
   |
   v
Symbol Table Builder (AST traversal)
   |
   v
Scope Tree + Symbol Entries + Binding Errors
```

Additional parser-analysis path:

```text
Token Stream
   |-----------------------> LL(1) Parser (stack trace)
   |-----------------------> SLR(1) Parser (shift/reduce trace)
Grammar Utils -----------> FIRST/FOLLOW + parsing tables
```

---

## 5. Mandatory Evaluation Program Walkthrough

For the mandatory program (declarations, loops, nested `if`, arithmetic + boolean expressions):

1. Lexer classifies all lexemes (`int`, identifiers, literals, operators, delimiters).
2. Parser builds AST nodes such as:
   - `Decl`, `Assign`
   - `WhileStmt`, `IfStmt`, `Block`
   - `BinOp`, `RelExpr`, `BoolAnd`, `BoolOr`, `BoolNot`
3. Symbol table traversal:
   - inserts global names (`a`, `b`, `sum`, `avg`)
   - enters loop/block scopes
   - inserts block-local names (for example `temp`)
   - resolves identifier references by nearest visible scope
   - reports duplicate/undeclared errors if any

---

## 6. Design Decisions

### Why AST-based design?
- Keeps syntax structure explicit after parsing.
- Makes later analyses (symbol table, semantic checks, TAC) easier to implement.

### Why scope tree?
- Natural representation of nested blocks and function scopes.
- Enables correct shadowing and nearest-scope lookup.

### Why module separation?
- `lexer.py`: tokenization only
- `parser.py`: syntax + AST
- `symbol_table.py`: bindings/scopes
- `grammar_utils.py`, `ll1_parser.py`, `slr_parser.py`: parser theory artifacts
- `compiler.py`: orchestration/UI

---

## 7. Current Limitations (As Implemented)

- Full semantic phase is limited compared to complete production compilers.
- Intermediate code generation (TAC) is not implemented in this codebase.
- Optimization passes are not implemented.
- Target code generation is not implemented.

---

## 8. How to Run

From project root:

```bash
python compiler.py
```

Or with explicit source file:

```bash
python compiler.py testPrograms/evaluation_program.txt
```

Then use menu options:
- `1`: errors summary
- `2`: token stream
- `3`: parse tree AST
- `4`: LL(1) parser trace
- `5`: SLR(1) parser trace
- `6`: CFG + derivations + parse tree view
- `7`: FIRST/FOLLOW/tables
- `8`: symbol table demonstration

---

## 9. Demo Guide (Evaluator Sequence)

Recommended sequence:

1. Run `evaluation_program.txt`
2. Show Option `2` (token stream)
3. Show Option `3` (AST)
4. Show Option `1` (no lexical/syntax errors)
5. Show Option `8` (symbol scopes + lookup trace)
6. Show Option `7` (FIRST/FOLLOW, LL/SLR tables)
7. Show Option `4` and `5` for parser stack-trace evidence

For error demonstration:
- run one lexical-invalid test
- run one syntax-invalid test
- run one symbol-table-invalid test (duplicate declaration / out-of-scope use)
