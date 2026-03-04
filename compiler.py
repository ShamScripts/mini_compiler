from pathlib import Path
from modules.lexer import Lexer


def run_lexical_analysis(source_code):
    """Run the lexer and print tokens / errors."""
    lexer = Lexer(source_code)
    tokens, errors = lexer.tokenize()

    print("=" * 80)
    print("PHASE: LEXICAL ANALYSIS (Q1)")
    print("=" * 80)
    print()

    if errors:
        print("Lexical errors found:\n")
        for err in errors:
            print(err)
        print("\nToken stream up to errors:\n")
    else:
        print("No lexical errors.\n")

    print("Token stream:")
    print("-" * 60)
    print(f"{'idx':>3}  {'line':>4} {'col':>4}  {'type':<15}  lexeme")
    print("-" * 60)
    for i, tok in enumerate(tokens):
        print(f"{i:>3}  {tok.line:>4} {tok.column:>4}  {tok.type.name:<15}  {tok.lexeme!r}")


def main(filename=None):
    if filename is None:
        filename = "evaluation_program.txt"

    path = Path(filename)
    if not path.is_file():
        raise SystemExit(f"Input file not found: {filename}")

    source = path.read_text(encoding="utf-8")
    
    run_lexical_analysis(source)    #q1


if __name__ == "__main__":
    import sys

    arg = sys.argv[1] if len(sys.argv) > 1 else None
    main(arg)

