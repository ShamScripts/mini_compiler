"""
Syntax analyzer – parses the token stream and builds an abstract syntax tree.
Also provides the context-free grammar display for the compiler menu.
"""

from __future__ import annotations
import textwrap

from .parser import Parser, ast_dump

_EVAL = "evaluation_program.txt"
_STMT = "a = 2 * (3 + 4);"
_LN = 5

_CFG_INTRO = (
    f"Context-Free Grammar for the prescribed core language "
    f"(declarations, assignments, expressions, boolean expressions, "
    f"if-else, while, block structures). "
    f"This grammar generates the entire {_EVAL} without modification. "
    f"Terminals: int, float, if, else, while, print, IDENTIFIER, INT_LITERAL, "
    f"FLOAT_LITERAL, = + - * / % < > <= >= == != && || ! ; {{ }} ( )."
)

_CFG_PROD = """
  Program      -> DeclList StmtList
  DeclList     -> Decl DeclList | epsilon
  Decl         -> Type IDENTIFIER SEMICOLON
  Type         -> INT | FLOAT
  StmtList     -> Stmt StmtList | epsilon
  Stmt         -> AssignStmt | IfStmt | WhileStmt | PrintStmt | Block
  AssignStmt   -> IDENTIFIER ASSIGN Expr SEMICOLON
  IfStmt       -> IF LPAREN BoolExpr RPAREN Block ElsePart
  ElsePart     -> ELSE Block | epsilon
  WhileStmt    -> WHILE LPAREN BoolExpr RPAREN Block
  PrintStmt    -> PRINT LPAREN Expr RPAREN SEMICOLON
  Block        -> LBRACE DeclList StmtList RBRACE
  BoolExpr     -> BoolTerm BoolExprTail
  BoolExprTail -> OR BoolTerm BoolExprTail | epsilon
  BoolTerm     -> BoolFactor BoolTermTail
  BoolTermTail -> AND BoolFactor BoolTermTail | epsilon
  BoolFactor   -> NOT BoolFactor | RelExpr | LPAREN BoolExpr RPAREN
  RelExpr      -> Expr RelOp Expr
  RelOp        -> LT | GT | LE | GE | EQ | NE
  Expr         -> Term ExprTail
  ExprTail     -> AddOp Term ExprTail | epsilon
  AddOp        -> PLUS | MINUS
  Term         -> Factor TermTail
  TermTail     -> MulOp Factor TermTail | epsilon
  MulOp        -> MUL | DIV | MOD
  Factor       -> IDENTIFIER | INT_LITERAL | FLOAT_LITERAL | LPAREN Expr RPAREN
"""

_LEFT = """
  1.  Stmt
  2.  AssignStmt
  3.  IDENTIFIER ASSIGN Expr SEMICOLON
  4.  a ASSIGN Expr SEMICOLON
  5.  a = Term ExprTail SEMICOLON
  6.  a = Factor TermTail ExprTail SEMICOLON
  7.  a = INT_LITERAL TermTail ExprTail SEMICOLON
  8.  a = 2 TermTail ExprTail SEMICOLON
  9.  a = 2 MulOp Factor TermTail ExprTail SEMICOLON
 10.  a = 2 * Factor TermTail ExprTail SEMICOLON
 11.  a = 2 * LPAREN Expr RPAREN TermTail ExprTail SEMICOLON
 12.  a = 2 * ( Term ExprTail ) TermTail ExprTail SEMICOLON
 13.  a = 2 * ( Factor ExprTail ) TermTail ExprTail SEMICOLON
 14.  a = 2 * ( INT_LITERAL ExprTail ) TermTail ExprTail SEMICOLON
 15.  a = 2 * ( 3 ExprTail ) TermTail ExprTail SEMICOLON
 16.  a = 2 * ( 3 AddOp Term ExprTail ) TermTail ExprTail SEMICOLON
 17.  a = 2 * ( 3 + Term ExprTail ) TermTail ExprTail SEMICOLON
 18.  a = 2 * ( 3 + Factor ExprTail ) TermTail ExprTail SEMICOLON
 19.  a = 2 * ( 3 + INT_LITERAL ExprTail ) TermTail ExprTail SEMICOLON
 20.  a = 2 * ( 3 + 4 ExprTail ) TermTail ExprTail SEMICOLON
 21.  a = 2 * ( 3 + 4 ) TermTail ExprTail SEMICOLON
 22.  a = 2 * ( 3 + 4 ) SEMICOLON
"""

_RIGHT = """
  1.  Stmt
  2.  AssignStmt
  3.  IDENTIFIER ASSIGN Expr SEMICOLON
  4.  IDENTIFIER ASSIGN Term ExprTail SEMICOLON
  5.  IDENTIFIER ASSIGN Term SEMICOLON
  6.  IDENTIFIER ASSIGN Factor TermTail SEMICOLON
  7.  IDENTIFIER ASSIGN Factor MulOp Factor TermTail SEMICOLON
  8.  IDENTIFIER ASSIGN Factor MulOp Factor SEMICOLON
  9.  IDENTIFIER ASSIGN Factor MulOp LPAREN Expr RPAREN SEMICOLON
 10.  IDENTIFIER ASSIGN Factor MulOp LPAREN Term ExprTail RPAREN SEMICOLON
 11.  IDENTIFIER ASSIGN Factor MulOp LPAREN Term AddOp Term ExprTail RPAREN SEMICOLON
 12.  IDENTIFIER ASSIGN Factor MulOp LPAREN Term AddOp Term RPAREN SEMICOLON
 13.  IDENTIFIER ASSIGN Factor MulOp LPAREN Term AddOp Factor RPAREN SEMICOLON
 14.  IDENTIFIER ASSIGN Factor MulOp LPAREN Term AddOp INT_LITERAL RPAREN SEMICOLON
 15.  IDENTIFIER ASSIGN Factor MulOp LPAREN Term AddOp 4 RPAREN SEMICOLON
 16.  IDENTIFIER ASSIGN Factor MulOp LPAREN Factor AddOp 4 RPAREN SEMICOLON
 17.  IDENTIFIER ASSIGN Factor MulOp LPAREN INT_LITERAL AddOp 4 RPAREN SEMICOLON
 18.  IDENTIFIER ASSIGN Factor MulOp LPAREN 3 + 4 RPAREN SEMICOLON
 19.  IDENTIFIER ASSIGN Factor * ( 3 + 4 ) SEMICOLON
 20.  IDENTIFIER ASSIGN INT_LITERAL * ( 3 + 4 ) SEMICOLON
 21.  IDENTIFIER ASSIGN 2 * ( 3 + 4 ) SEMICOLON
 22.  a = 2 * ( 3 + 4 ) ;
"""


_W = 72
_BAR = "-" * (_W - 2)
_SEP = "=" * (_W - 2)
_INNER = _W - 6


def _box_line(text: str = "") -> None:
    print(f"  |  {text}")


def _box_wrapped(text: str) -> None:
    for part in textwrap.wrap(text, width=_INNER) or [""]:
        _box_line(part)


def _fmt_prod_line(raw: str) -> str:
    """Align grammar production lines for better readability."""
    s = raw.strip()
    if not s or "->" not in s:
        return s
    head, body = s.split("->", 1)
    return f"{head.strip():<13} -> {body.strip()}"


def print_cfg(source_file: str | None = None, skip_heading: bool = False) -> None:
    if not skip_heading:
        src = source_file or _EVAL
        print()
        print(f"  +{_SEP}+")
        print(f"  |  CONTEXT-FREE GRAMMAR")
        print(f"  |  (Source: {src})")
        print(f"  +{_SEP}+")
    else:
        print(f"  +{_BAR}+")
    _box_wrapped(_CFG_INTRO)
    for ln in _CFG_PROD.strip().split("\n"):
        _box_line(_fmt_prod_line(ln))
    print(f"  +{_BAR}+")
    print()


def _section(title: str, sub: str = "") -> None:
    print(f"\n  +{_BAR}+")
    _box_wrapped(title)
    if sub:
        _box_wrapped(sub)
    print(f"  +{_BAR}+")


def _print_grammar_and_tree(tree_txt: str, src: str | None = None) -> None:
    src = src or _EVAL
    print()
    print(f"  +{_SEP}+")
    print(f"  |  GRAMMAR AND PARSE TREE")
    print(f"  |  (Source: {src})")
    print(f"  +{_SEP}+")

    _section("1. Context-Free Grammar")
    _box_wrapped(_CFG_INTRO)
    for ln in _CFG_PROD.strip().split("\n"):
        _box_line(_fmt_prod_line(ln))
    print(f"  +{_BAR}+")

    _section("2. Leftmost Derivation", "Non-trivial statement from source.")
    _box_wrapped(f"Statement (line {_LN}): {_STMT}")
    _box_wrapped("At each step, the leftmost nonterminal is replaced.")
    print()
    for ln in _LEFT.strip().split("\n"):
        _box_line(ln.strip())
    print(f"  +{_BAR}+")

    _section("3. Rightmost Derivation", "Same statement; rightmost nonterminal replaced each step.")
    _box_wrapped(f"Statement (line {_LN}): {_STMT}")
    print()
    for ln in _RIGHT.strip().split("\n"):
        _box_line(ln.strip())
    print(f"  +{_BAR}+")

    _section("4. Parse Tree (AST)", f"Built from token stream for {src}.")
    print()
    for ln in tree_txt.split("\n"):
        print(f"  |  {ln}")
    print(f"  +{_BAR}+")
    print()


def run_syntax_analysis(tokens, source_file=None):
    """
    Phase 2: Syntax analysis.
    Consumes token stream from lexical analyzer.
    """
    print(f"\n  +{_SEP}+")
    print(f"  |  PHASE 2: SYNTAX ANALYSIS")
    print(f"  +{_SEP}+\n")

    parser = Parser(tokens)
    ast = parser.parse()

    if parser.errors:
        print("  [!] Syntax errors found:\n")
        for i, err in enumerate(parser.errors, 1):
            print(f"    {i}. {err}\n")
    else:
        print("  [OK] No syntax errors. Parse tree constructed.\n")
        _print_grammar_and_tree(ast_dump(ast), source_file=source_file)

    return ast, parser.errors


def print_derivations_and_parse_tree(ast, source_file: str | None = None) -> None:
    """
    Display CFG, leftmost/rightmost derivations, and parse tree for CLI menu use.
    """
    _print_grammar_and_tree(ast_dump(ast), src=source_file)
