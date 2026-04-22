from pathlib import Path
from modules.lexer import Lexer
from modules.parser import Parser, ast_dump
from modules.ll1_parser import LL1Parser
from modules.slr_parser import SLRParser
from modules.symbol_table import SymbolTable, Symbol, Scope
from modules.syntax_analyzer import print_derivations_and_parse_tree
from modules.semantic_analyzer import SemanticAnalyzer
from modules.intermediate_code import generate_tac, generate_triples
from modules.target_code import optimize_tac, generate_target_code

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


def _errors(lex_errors, syn_errors, sem_errors, src: str) -> None:
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
            print(top)
            if sem_errors is None:
                print(f"  |  Semantic analysis not run.")
            elif sem_errors:
                print(f"  |  Semantic errors ({len(sem_errors)} found):")
                print(f"  |{bar}+")
                for i, err in enumerate(sem_errors, 1):
                    for ln in str(err).split("\n"):
                        print(f"  |  {ln}")
                    if i < len(sem_errors):
                        print(f"  |")
                print(top)
            else:
                print(f"  |  [OK] No semantic errors.")
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
    print(f"  |    6. CFG + Left/Right Derivation + Parse Tree")
    print(f"  |    7. Parser Construction Materials (FIRST/FOLLOW/Tables)")
    print(f"  |    8. Symbol Table Demonstration (Nested Scopes)")
    print(f"  |    9. Generate Intermediate Code (TAC)")
    print(f"  |   10. Optimize & Generate Target Code")
    print(f"  |   11. Exit")
    print(f"  +{bar}+")
    print()
    return input("  Enter choice (1-11): ").strip()


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
    sem_errors = None
    st = None
    st_errors = []
    if not lex_errors:
        parser = Parser(tokens)
        ast = parser.parse()
        syn_errors = parser.errors
        if not syn_errors and ast is not None:
            st = SymbolTable()
            st.build_from_ast(ast)
            st_errors = [f"ERROR: {msg[7:]}" for msg in st.history if msg.startswith("ERROR:")]
            semantic = SemanticAnalyzer(ast, st)
            sem_errors = st_errors + semantic.analyze()

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
            _errors(lex_errors, syn_errors, sem_errors, src)

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
            _heading(6, "CFG + DERIVATIONS + PARSE TREE", src)
            bar = _B * (W - 6)
            if lex_errors:
                print(f"  +{bar}+")
                print("  |  Cannot generate: lexical errors present.")
                print(f"  +{bar}+")
            elif syn_errors:
                print(f"  +{bar}+")
                print("  |  Cannot generate: syntax errors present.")
                print(f"  +{bar}+")
            elif ast is not None:
                print_derivations_and_parse_tree(ast, source_file=src)
            else:
                print(f"  +{bar}+")
                print("  |  Derivation material not available.")
                print(f"  +{bar}+")

        elif choice == "7":
            _heading(7, "PARSER CONSTRUCTION MATERIALS", src)
            from modules.grammar_utils import get_mini_compiler_grammar
            g = get_mini_compiler_grammar()
            print("  [1] FIRST Sets")
            print("  [2] FOLLOW Sets")
            print("  [3] LL(1) Parsing Table")
            print("  [4] SLR(1) Action/Goto Table")
            sub = input("\n  Select material (1-4): ").strip()
            
            if sub == "1":
                print("\n  FIRST SETS:")
                for nt in sorted(g.non_terminals):
                    first_list = sorted(filter(None, g.first[nt]))
                    eps = "eps" if "" in g.first[nt] else ""
                    print(f"    FIRST({nt:<15}) = {{ {', '.join(first_list)} {eps} }}")
            elif sub == "2":
                print("\n  FOLLOW SETS:")
                for nt in sorted(g.non_terminals):
                    follow_list = sorted(g.follow[nt])
                    print(f"    FOLLOW({nt:<15}) = {{ {', '.join(follow_list)} }}")
            elif sub == "3":
                print("\n  LL(1) PARSING TABLE:")
                ll_table = g.get_ll1_table()
                for nt, entries in sorted(ll_table.items()):
                    for t, body in sorted(entries.items()):
                        prod = " ".join(body) if body else "eps"
                        print(f"    M[{nt:<15}, {t:<15}] = {nt} -> {prod}")
            elif sub == "4":
                print("\n  SLR(1) TABLES:")
                action, goto, rules = g.get_slr_table()
                print("  ACTION TABLE (Sample):")
                # Show first 50 entries to avoid overwhelming
                count = 0
                for (state, sym), act in sorted(action.items()):
                    print(f"    Action({state:<3}, {sym:<12}) = {act}")
                    count += 1
                    if count > 50: break
                print("    ...")
                print("\n  GOTO TABLE (Sample):")
                count = 0
                for (state, nt), gt in sorted(goto.items()):
                    print(f"    Goto({state:<3}, {nt:<15}) = {gt}")
                    count += 1
                    if count > 30: break
                print("    ...")

        elif choice == "8":
            _heading(8, "SYMBOL TABLE DEMONSTRATION", src)
            bar = _B * (W - 6)
            if lex_errors:
                print(f"  +{bar}+")
                print("  |  Cannot build symbol table: lexical errors present.")
                print(f"  +{bar}+")
            elif syn_errors:
                print(f"  +{bar}+")
                print("  |  Cannot build symbol table: syntax errors present.")
                print(f"  +{bar}+")
            elif ast is not None:
                if st is None:
                    st = SymbolTable()
                    st.build_from_ast(ast)
                st.dump()
                st.print_multi_tables()
            else:
                print(f"  +{bar}+")
                print("  |  Symbol table not available.")
                print(f"  +{bar}+")

        elif choice == "9":
            _heading(9, "INTERMEDIATE CODE GENERATION (TAC)", src)
            bar = _B * (W - 6)
            if lex_errors or syn_errors:
                print(f"  +{bar}+")
                print("  |  Cannot generate TAC: errors in earlier phases.")
                print(f"  +{bar}+")
            elif ast is not None:
                print(f"  +{bar}+")
                print("  |  Select representation:")
                print("  |    [1] Quadruples (Quadruple format with explicit result)")
                print("  |    [2] Triples (Position-based results)")
                print(f"  +{bar}+")
                sub = input("  Enter choice (1-2): ").strip()
                
                if sub == "1":
                    print(f"  +{bar}+")
                    print("  |  QUADRUPLES (TAC):")
                    print(f"  +{bar}+")
                    tac = generate_tac(ast)
                    for i, inst in enumerate(tac):
                        print(f"  |  {i:<4} {inst}")
                    print(f"  +{bar}+")
                elif sub == "2":
                    print(f"  +{bar}+")
                    print("  |  TRIPLES:")
                    print(f"  +{bar}+")
                    triples = generate_triples(ast)
                    for i, triple in enumerate(triples):
                        print(f"  |  {i:<4} {triple}")
                    print(f"  +{bar}+")
                else:
                    print(f"  +{bar}+")
                    print("  |  Invalid choice.")
                    print(f"  +{bar}+")
            else:
                print("  |  AST not available.")

        elif choice == "10":
            _heading(10, "OPTIMIZATION & TARGET CODE GENERATION", src)
            bar = _B * (W - 6)
            if lex_errors or syn_errors:
                print(f"  +{bar}+")
                print("  |  Cannot generate Target Code: errors in earlier phases.")
                print(f"  +{bar}+")
            elif ast is not None:
                tac = generate_tac(ast)
                optimized = optimize_tac(tac)
                target = generate_target_code(optimized)
                print(f"  +{bar}+")
                print("  |  OPTIMIZED TAC (Constant Folding):")
                print(f"  +{bar}+")
                for inst in optimized:
                    print(f"  |  {inst}")
                print(f"  +{bar}+")
                print("  |  TARGET CODE (Pseudo-Assembly):")
                print(f"  +{bar}+")
                for inst in target:
                    print(f"  |  {inst}")
                print(f"  +{bar}+")
            else:
                print("  |  AST not available.")

        elif choice == "11":
            print()
            print("  Exiting.")
            print()
            break

        else:
            print()
            print("  Invalid choice. Please enter 1-11.")
            print()


if __name__ == "__main__":
    import sys

    arg = sys.argv[1] if len(sys.argv) > 1 else None
    try:
        main(arg)
    except KeyboardInterrupt:
        print()
        print("  Exiting (Keyboard Interrupt).")
        print()
        sys.exit(0)
