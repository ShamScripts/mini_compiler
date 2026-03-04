# mini_compiler
Mini Compiler – CS F363 (Python)
This is a small compiler project for the CS F363 Compiler Construction course.  
The goal is to build the full pipeline step by step:

- **Lexical analysis**
- **Syntax analysis**
- **Semantic analysis + symbol table**
- **Intermediate code (TAC)**
- **Basic optimisation + pseudo assembly**

Right now (Week 1 / Midsem Q1) only the **lexer** is implemented and working.

---

### Project layout

- **`compiler.py`** – main script. For now it only runs lexical analysis on an input file.
- **`evaluation_program.txt`** – the uniform test program given in the assignment.
- **`contribution.md`** – member-wise work distribution (M1–M4) for all questions.
- **`modules/`**
  - **`__init__.py`** – marks this as a package.
  - **`tokens.py`** – token kinds (`TokenType`), `Token`, and `LexicalError`.
  - **`lexer.py`** – regex-based lexer used for Q1.

---

### How to run?

From the project folder:

```bash
python compiler.py
```

This will:

- Read `evaluation_program.txt`,
- Run the lexer,
- Print any **lexical errors**,
- Print the full **token stream** (token type, lexeme, line, column).

You can also pass a different source file:

```bash
python compiler.py some_other_program.txt
```

---
