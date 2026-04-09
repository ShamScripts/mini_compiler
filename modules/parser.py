"""Parser and AST for syntax analysis. Consumes token stream from lexer."""

from dataclasses import dataclass
from typing import List, Optional

from .tokens import TokenType, Token, SyntaxErrorReport


# --- AST node classes ---

@dataclass
class Param:
    type_name: str
    name: str


@dataclass
class FuncDecl:
    return_type: str
    name: str
    param: Optional[Param]
    body: "Block"


@dataclass
class Program:
    units: List


@dataclass
class Decl:
    type_name: str
    name: str


@dataclass
class Stmt:
    pass


@dataclass
class Assign(Stmt):
    name: str
    expr: "Expr"


@dataclass
class IfStmt(Stmt):
    cond: "BoolExpr"
    then_block: "Block"
    else_block: Optional["Block"]


@dataclass
class WhileStmt(Stmt):
    cond: "BoolExpr"
    body: "Block"


@dataclass
class PrintStmt(Stmt):
    expr: "Expr"


@dataclass
class Block(Stmt):
    units: List


@dataclass
class BoolExpr:
    pass


@dataclass
class BoolOr(BoolExpr):
    left: BoolExpr
    right: BoolExpr


@dataclass
class BoolAnd(BoolExpr):
    left: BoolExpr
    right: BoolExpr


@dataclass
class BoolNot(BoolExpr):
    inner: BoolExpr


@dataclass
class RelExpr(BoolExpr):
    left: "Expr"
    op: str
    right: "Expr"


@dataclass
class Expr:
    pass


@dataclass
class BinOp(Expr):
    left: Expr
    op: str
    right: Expr


@dataclass
class UnaryMinus(Expr):
    inner: Expr


@dataclass
class Var(Expr):
    name: str


@dataclass
class IntLit(Expr):
    value: int


@dataclass
class FloatLit(Expr):
    value: float


# --- Parse tree printer (ast_dump) ---

def _label(node) -> str:
    if isinstance(node, Program):
        return "Program"
    if isinstance(node, Param):
        return f"Param({node.type_name} {node.name})"
    if isinstance(node, FuncDecl):
        return f"FuncDecl({node.return_type} {node.name})"
    if isinstance(node, Decl):
        return f"Decl({node.type_name} {node.name})"
    if isinstance(node, Assign):
        return f"Assign({node.name})"
    if isinstance(node, IfStmt):
        return "IfStmt"
    if isinstance(node, WhileStmt):
        return "WhileStmt"
    if isinstance(node, PrintStmt):
        return "PrintStmt"
    if isinstance(node, Block):
        return "Block"
    if isinstance(node, BoolOr):
        return "BoolOr(||)"
    if isinstance(node, BoolAnd):
        return "BoolAnd(&&)"
    if isinstance(node, BoolNot):
        return "BoolNot(!)"
    if isinstance(node, RelExpr):
        return f"RelExpr({node.op})"
    if isinstance(node, BinOp):
        return f"BinOp({node.op})"
    if isinstance(node, Var):
        return f"Var({node.name})"
    if isinstance(node, IntLit):
        return f"IntLit({node.value})"
    if isinstance(node, FloatLit):
        return f"FloatLit({node.value})"
    if isinstance(node, UnaryMinus):
        return "UnaryMinus(-)"
    return "?"


def _children(node) -> list:
    if isinstance(node, Program):
        return list(node.units)
    if isinstance(node, Param):
        return []
    if isinstance(node, FuncDecl):
        return ([node.param] if node.param else []) + [node.body]
    if isinstance(node, Decl):
        return []
    if isinstance(node, Assign):
        return [node.expr]
    if isinstance(node, IfStmt):
        return [node.cond, node.then_block] + ([node.else_block] if node.else_block else [])
    if isinstance(node, WhileStmt):
        return [node.cond, node.body]
    if isinstance(node, PrintStmt):
        return [node.expr]
    if isinstance(node, Block):
        return list(node.units)
    if isinstance(node, BoolOr):
        return [node.left, node.right]
    if isinstance(node, BoolAnd):
        return [node.left, node.right]
    if isinstance(node, BoolNot):
        return [node.inner]
    if isinstance(node, RelExpr):
        return [node.left, node.right]
    if isinstance(node, BinOp):
        return [node.left, node.right]
    if isinstance(node, (Var, IntLit, FloatLit)):
        return []
    if isinstance(node, UnaryMinus):
        return [node.inner]
    return []


def _tree_lines(node, prefix: str, is_last: bool) -> list:
    branch = "\\-- " if is_last else "+-- "
    line = prefix + branch + _label(node)
    lines = [line]
    kids = _children(node)
    for i, child in enumerate(kids):
        is_last_child = i == len(kids) - 1
        extension = "    " if is_last else "|   "
        lines.extend(_tree_lines(child, prefix + extension, is_last_child))
    return lines


def ast_dump(node) -> str:
    """Pretty-print AST as a tree."""
    lines = [_label(node)]
    kids = _children(node)
    for i, child in enumerate(kids):
        is_last = i == len(kids) - 1
        lines.extend(_tree_lines(child, "", is_last))
    return "\n".join(lines)


# --- Parser ---

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0
        self.errors = []

    def current(self):
        if self.i >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.i]

    def advance(self):
        if self.i < len(self.tokens):
            self.i += 1

    def _syntax_error_type(self, tt):
        if tt == TokenType.SEMICOLON:
            return "Missing semicolon"
        if tt == TokenType.RPAREN:
            return "Missing closing parenthesis"
        if tt == TokenType.RBRACE:
            return "Missing closing brace"
        if tt == TokenType.LPAREN:
            return "Missing opening parenthesis"
        if tt == TokenType.IDENTIFIER:
            return "Missing identifier (e.g. variable name)"
        if tt == TokenType.ASSIGN:
            return "Missing assignment operator (=)"
        return f"Expected {tt.name}"

    def expect(self, tt):
        t = self.current()
        if t.type == tt:
            self.advance()
            return t
        self.errors.append(SyntaxErrorReport(
            error_type=self._syntax_error_type(tt),
            expected=tt.name,
            found=t.type.name,
            line=t.line,
            column=t.column,
        ))
        return None

    def parse(self):
        units = []
        while self.current().type != TokenType.EOF and self.current().type != TokenType.RBRACE:
            u = self.parse_unit()
            if u:
                units.append(u)
        return Program(units=units)

    def parse_unit(self):
        t = self.current()
        if t.type in (TokenType.INT, TokenType.FLOAT):
            type_name = t.lexeme
            self.advance()
            id_tok = self.expect(TokenType.IDENTIFIER)
            if not id_tok:
                return None
            
            if self.current().type == TokenType.LPAREN:
                # Function declaration
                self.advance()
                param = None
                if self.current().type in (TokenType.INT, TokenType.FLOAT):
                    ptype = self.current().lexeme
                    self.advance()
                    pid = self.expect(TokenType.IDENTIFIER)
                    if pid:
                        param = Param(type_name=ptype, name=pid.lexeme)
                self.expect(TokenType.RPAREN)
                body = self.parse_block()
                return FuncDecl(return_type=type_name, name=id_tok.lexeme, param=param, body=body)
            else:
                # Variable declaration
                self.expect(TokenType.SEMICOLON)
                return Decl(type_name=type_name, name=id_tok.lexeme)
        else:
            return self.parse_stmt()

    def parse_stmt(self):
        t = self.current()
        if t.type == TokenType.IDENTIFIER:
            return self.parse_assign()
        if t.type == TokenType.IF:
            return self.parse_if()
        if t.type == TokenType.WHILE:
            return self.parse_while()
        if t.type == TokenType.PRINT:
            return self.parse_print()
        if t.type == TokenType.LBRACE:
            return self.parse_block()
        self.errors.append(SyntaxErrorReport(
            error_type="Unexpected token",
            expected="statement start (identifier, if, while, print, or {)",
            found=t.type.name,
            line=t.line,
            column=t.column,
        ))
        self.advance()
        return None

    def parse_assign(self):
        id_tok = self.expect(TokenType.IDENTIFIER)
        if not id_tok:
            return None
        self.expect(TokenType.ASSIGN)
        expr = self.parse_expr()
        if not expr:
            return None
        self.expect(TokenType.SEMICOLON)
        return Assign(name=id_tok.lexeme, expr=expr)

    def parse_if(self):
        self.expect(TokenType.IF)
        self.expect(TokenType.LPAREN)
        cond = self.parse_bool_expr()
        if not cond:
            return None
        self.expect(TokenType.RPAREN)
        then_b = self.parse_block()
        else_b = None
        if self.current().type == TokenType.ELSE:
            self.advance()
            else_b = self.parse_block()
        return IfStmt(cond=cond, then_block=then_b, else_block=else_b)

    def parse_while(self):
        self.expect(TokenType.WHILE)
        self.expect(TokenType.LPAREN)
        cond = self.parse_bool_expr()
        if not cond:
            return None
        self.expect(TokenType.RPAREN)
        body = self.parse_block()
        return WhileStmt(cond=cond, body=body)

    def parse_print(self):
        self.expect(TokenType.PRINT)
        self.expect(TokenType.LPAREN)
        expr = self.parse_expr()
        if not expr:
            return None
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.SEMICOLON)
        return PrintStmt(expr=expr)

    def parse_block(self):
        self.expect(TokenType.LBRACE)
        units = []
        while self.current().type != TokenType.RBRACE and self.current().type != TokenType.EOF:
            u = self.parse_unit()
            if u:
                units.append(u)
        self.expect(TokenType.RBRACE)
        return Block(units=units)

    def parse_bool_expr(self):
        left = self.parse_bool_term()
        if not left:
            return None
        while self.current().type == TokenType.OR:
            self.advance()
            right = self.parse_bool_term()
            if not right:
                return left
            left = BoolOr(left=left, right=right)
        return left

    def parse_bool_term(self):
        left = self.parse_bool_factor()
        if not left:
            return None
        while self.current().type == TokenType.AND:
            self.advance()
            right = self.parse_bool_factor()
            if not right:
                return left
            left = BoolAnd(left=left, right=right)
        return left

    def parse_bool_factor(self):
        t = self.current()
        if t.type == TokenType.NOT:
            self.advance()
            inner = self.parse_bool_factor()
            if not inner:
                return None
            return BoolNot(inner=inner)
        if t.type == TokenType.LPAREN:
            self.advance()
            inner = self.parse_bool_expr()
            if not inner:
                return None
            self.expect(TokenType.RPAREN)
            return inner
        return self.parse_rel_expr()

    def parse_rel_expr(self):
        left = self.parse_expr()
        if not left:
            return None
        t = self.current()
        if t.type in (TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE, TokenType.EQ, TokenType.NE):
            op = t.lexeme
            self.advance()
            right = self.parse_expr()
            if not right:
                return None
            return RelExpr(left=left, op=op, right=right)
        return None

    def parse_expr(self):
        left = self.parse_term()
        if not left:
            return None
        while self.current().type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current().lexeme
            self.advance()
            right = self.parse_term()
            if not right:
                return left
            left = BinOp(left=left, op=op, right=right)
        return left

    def parse_term(self):
        left = self.parse_factor()
        if not left:
            return None
        while self.current().type in (TokenType.MUL, TokenType.DIV, TokenType.MOD):
            op = self.current().lexeme
            self.advance()
            right = self.parse_factor()
            if not right:
                return left
            left = BinOp(left=left, op=op, right=right)
        return left

    def parse_factor(self):
        t = self.current()
        if t.type == TokenType.IDENTIFIER:
            self.advance()
            return Var(name=t.lexeme)
        if t.type == TokenType.INT_LITERAL:
            self.advance()
            return IntLit(value=int(t.lexeme))
        if t.type == TokenType.FLOAT_LITERAL:
            self.advance()
            return FloatLit(value=float(t.lexeme))
        if t.type == TokenType.LPAREN:
            self.advance()
            e = self.parse_expr()
            if not e:
                return None
            self.expect(TokenType.RPAREN)
            return e
        self.errors.append(SyntaxErrorReport(
            error_type="Invalid expression",
            expected="factor (identifier, number, or parenthesized expression)",
            found=t.type.name,
            line=t.line,
            column=t.column,
        ))
        return None
