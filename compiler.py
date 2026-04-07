from pathlib import Path
from modules.lexer import Lexer
from modules.parser import Parser, ast_dump
from modules.ll1_parser import LL1Parser
from modules.slr_parser import SLRParser
from modules.symbol_table import SymbolTable, Symbol, Scope

W = 76
_B = "-"
_EQ = "="


def _heading(num: int, title: str, src: str | None = None) -> None:
    line = _EQ * (W - 4)
    print()
    print(f"  +{line}+")
    print(f"  |  {num}. {title:<{W - 10}} |")
    if src:
        print(f"  |  Source: {src:<{W - 14}} |")
    print(f"  +{line}+")
    print()


def _tokens(tok_list) -> None:
    col_idx, col_ln, col_col, col_type, col_lex = 4, 5, 5, 16, 30
    d = _B * (col_idx + 1)
    h = f"  +{d}+{_B * (col_ln + 1)}+{_B * (col_col + 1)}+{_B * (col_type + 1)}+{_B * (col_lex + 1)}+"
    print(h)
    print(f"  | {'#':<{col_idx}} | {'Line':<{col_ln}} | {'Col':<{col_col}} | {'Type':<{col_type}} | {'Lexeme':<{col_lex}} |")
    print(h)
    for i, tok in enumerate(tok_list):
        lex = tok.lexeme if tok.lexeme else "<EOF>"
        if len(lex) > col_lex - 2:
            lex = lex[: col_lex - 5] + "..."
        print(f"  | {i:<{col_idx}} | {tok.line:<{col_ln}} | {tok.column:<{col_col}} | {tok.type.name:<{col_type}} | {lex:<{col_lex}} |")
    print(h)
    print()


def _errors(lex_errors, syn_errors, src: str) -> None:
    _heading(1, "CHECK FOR ERRORS", src)
    bar = _B * (W - 6)
    top = f"  +{bar}+"
    print(top)
    if lex_errors:
        print(f"  |  Lexical errors ({len(lex_errors)} found):")
        print(f"  |{bar}+")
        for i, err in enumerate(lex_errors, 1):
            for ln in str(err).split("\n"):
                print(f"  |  {ln}")
            if i < len(lex_errors):
                print(f"  |")
        print(top)
    else:
        print(f"  |  [OK] No lexical errors.")
        print(top)

    print()
    if lex_errors:
        print(top)
        print(f"  |  Syntax analysis skipped (lexical errors present).")
        print(top)
    elif syn_errors is not None:
        print(top)
        if syn_errors:
            print(f"  |  Syntax errors ({len(syn_errors)} found):")
            print(f"  |{bar}+")
            for i, err in enumerate(syn_errors, 1):
                for ln in str(err).split("\n"):
                    print(f"  |  {ln}")
                if i < len(syn_errors):
                    print(f"  |")
            print(top)
        else:
            print(f"  |  [OK] No syntax errors.")
            print(top)
    print()


def _tree(ast) -> None:
    bar = _B * (W - 6)
    print(f"  +{bar}+")
    for ln in ast_dump(ast).split("\n"):
        print(f"  |  {ln}")
    print(f"  +{bar}+")
    print()


def _menu() -> str:
    bar = _B * (W - 6)
    print()
    print(f"  +{bar}+")
    print(f"  |  MENU:")
    print(f"  |    1. Check for errors")
    print(f"  |    2. Generate stream of tokens")
    print(f"  |    3. Parse Tree (AST)")
    print(f"  |    4. LL(1) Parser Evaluation (Stack Trace)")
    print(f"  |    5. SLR(1) Parser Evaluation (Stack Trace)")
    print(f"  |    6. Symbol Table Demonstration (Nested Scopes)")
    print(f"  |    7. Exit")
    print(f"  +{bar}+")
    print()
    return input("  Enter choice (1-7): ").strip()


def main(filename: str | None = None) -> None:
    path = Path(filename or "testPrograms/evaluation_program.txt")
    if not path.is_file():
        raise SystemExit(f"Input file not found: {filename}")

    source = path.read_text(encoding="utf-8")
    src = path.name

    lexer = Lexer(source)
    tokens, lex_errors = lexer.tokenize()

    ast = None
    syn_errors = None
    if not lex_errors:
        parser = Parser(tokens)
        ast = parser.parse()
        syn_errors = parser.errors

    h = _EQ * (W - 2)
    print()
    print(f"  {h}")
    print("  MINI COMPILER")
    print(f"  {h}")
    print(f"  Source file: {src}")
    print(f"  {h}")

    while True:
        choice = _menu()

        if choice == "1":
            _errors(lex_errors, syn_errors, src)

        elif choice == "2":
            _heading(2, "GENERATE STREAM OF TOKENS", src)
            _tokens(tokens)

        elif choice == "3":
            _heading(3, "PARSE TREE (AST)", src)
            bar = _B * (W - 6)
            if lex_errors:
                print(f"  +{bar}+")
                print(f"  |  Cannot generate: lexical errors present.")
                print(f"  +{bar}+")
            elif syn_errors:
                print(f"  +{bar}+")
                print(f"  |  Cannot generate: syntax errors present.")
                print(f"  +{bar}+")
            elif ast is not None:
                _tree(ast)
            else:
                print(f"  +{bar}+")
                print(f"  |  Parse tree not available.")
                print(f"  +{bar}+")
            print()

        elif choice == "4":
            _heading(4, "LL(1) PARSER EVALUATION", src)
            if lex_errors:
                print("  Lexical errors present. Skipping.")
            else:
                ll1 = LL1Parser(tokens)
                if ll1.parse():
                    ll1.print_trace()
                else:
                    print(f"  LL(1) Parsing failed: {ll1.errors[0] if ll1.errors else 'Unknown error'}")
                    ll1.print_trace()

        elif choice == "5":
            _heading(5, "SLR(1) PARSER EVALUATION", src)
            if lex_errors:
                print("  Lexical errors present. Skipping.")
            else:
                slr = SLRParser(tokens)
                if slr.parse():
                    slr.print_trace()
                else:
                    print(f"  SLR(1) Parsing failed: {slr.errors[0] if slr.errors else 'Unknown error'}")
                    slr.print_trace()

        elif choice == "6":
            _heading(6, "SYMBOL TABLE DEMONSTRATION", src)
            st = SymbolTable()
            # Simulation of symbol table updates for evaluation program
            st.insert("a", "int")
            st.insert("b", "int")
            st.insert("sum", "int")
            st.insert("avg", "float")
            st.enter_scope() # while scope
            st.insert("temp", "int")
            st.exit_scope()
            st.dump()

        elif choice == "7":
            print()
            print("  Exiting.")
            print()
            break

        else:
            print()
            print("  Invalid choice. Please enter 1-7.")
            print()


if __name__ == "__main__":
    import sys

    arg = sys.argv[1] if len(sys.argv) > 1 else None
    main(arg)