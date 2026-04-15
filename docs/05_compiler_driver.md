# Module Documentation: `compiler.py`

## 1. Module Overview

`compiler.py` is the main driver and CLI entry point for the mini compiler.

It coordinates:
- lexing
- parsing
- symbol table build
- parser artifacts (LL(1), SLR, FIRST/FOLLOW/tables)
- user-facing menu output

---

## 2. Imports

- `from pathlib import Path`  
  Input-file existence and reading.
- `from modules.lexer import Lexer`  
  Tokenization.
- `from modules.parser import Parser, ast_dump`  
  AST parse + tree display.
- `from modules.ll1_parser import LL1Parser`  
  LL(1) parser trace path.
- `from modules.slr_parser import SLRParser`  
  SLR parser trace path.
- `from modules.symbol_table import SymbolTable, Symbol, Scope`  
  Symbol table construction and display.
- `from modules.syntax_analyzer import print_derivations_and_parse_tree`  
  CFG + derivation + parse-tree formatted presentation.
- `from modules.semantic_analyzer import SemanticAnalyzer`  
  Semantic phase integration exists in current driver.

---

## 3. Utility Functions

## `_heading(num, title, src=None)`
Prints standardized section header boxes.

## `_tokens(tok_list)`
Prints token stream in table format:
- index
- line
- column
- token type
- lexeme

## `_errors(lex_errors, syn_errors, sem_errors, src)`
Central error-report display:
- lexical summary
- syntax summary
- semantic summary (if run)

## `_tree(ast)`
Prints AST tree using `ast_dump`.

## `_menu()`
Displays interactive options and returns user selection.

---

## 4. Main Flow: `main(filename=None)`

Execution sequence:

1. Resolve source path (default `testPrograms/evaluation_program.txt`).
2. Read source.
3. Run lexer:
   - `tokens, lex_errors = lexer.tokenize()`
4. If no lexical errors:
   - run parser
   - collect syntax errors
5. If no syntax errors:
   - build symbol table from AST
   - collect symbol-table errors from history
   - run semantic analyzer (currently integrated in driver)
6. Enter interactive menu loop for display/report options.

---

## 5. Menu Options and Behavior

- **1**: Error report (lex/syntax/semantic summary)
- **2**: Token stream
- **3**: Parse tree AST
- **4**: LL(1) parser run + stack trace
- **5**: SLR parser run + stack trace
- **6**: CFG + derivations + parse tree view
- **7**: FIRST/FOLLOW/tables viewer
- **8**: Symbol table trace + per-scope tables
- **9**: Exit

Guard conditions prevent parse/tree/symbol actions when earlier phases failed.

---

## 6. Data Structures Used

- `tokens`: list of `Token`
- `lex_errors`, `syn_errors`, `sem_errors`: error lists
- `ast`: parser AST root
- `st`: `SymbolTable` instance
- formatted console strings for report rendering

---

## 7. Error Handling

- Missing input file: exits with message.
- Lexical errors: parser/symbol phases skipped.
- Syntax errors: AST-dependent outputs guarded.
- Menu input fallback:
  - invalid choice handled with prompt.

---

## 8. Example Run (Typical)

Command:
```bash
python compiler.py testPrograms/evaluation_program.txt
```

Recommended demo path:
1. Option `2` (token stream)
2. Option `3` (AST)
3. Option `1` (error summary)
4. Option `8` (symbol table)
5. Option `7`, `4`, `5` (parser-construction evidence)

---

## 9. Strengths and Limitations

### Strengths
- central orchestration is clear and readable
- supports both practical parse and parser-theory demonstrations
- good menu-driven demo UX

### Limitations
- CLI and analysis logic are tightly coupled in one file
- large single-file driver; could be split later (not required for coursework)
