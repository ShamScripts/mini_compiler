"""Semantic analyzer for type and condition validation."""

from typing import Dict, Optional

from . import parser as ast_nodes
from .symbol_table import SymbolTable
from .symbol_table import Scope


class SemanticAnalyzer:
    def __init__(self, ast, symbol_table: Optional[SymbolTable] = None):
        self.ast = ast
        self.errors = []
        self.st = symbol_table if symbol_table is not None else SymbolTable()
        if symbol_table is None:
            self.st.build_from_ast(ast)
        self.current_scope = self.st.root
        self._child_idx: Dict[int, int] = {}

    def analyze(self):
        self._visit_program(self.ast)
        return self.errors

    def _error(self, message: str) -> None:
        self.errors.append(f"ERROR: {message}")

    def _is_numeric(self, t: Optional[str]) -> bool:
        return t in ("int", "float")

    def _is_assignable(self, expected: str, got: str) -> bool:
        if expected == "float" and got in ("int", "float"):
            return True
        return expected == got

    def _visit_program(self, program: ast_nodes.Program) -> None:
        for unit in program.units:
            self._visit_unit(unit)

    def _next_child_scope(self) -> Optional[Scope]:
        idx = self._child_idx.get(id(self.current_scope), 0)
        if idx >= len(self.current_scope.children):
            return None
        child = self.current_scope.children[idx]
        self._child_idx[id(self.current_scope)] = idx + 1
        return child

    def _enter_existing_scope(self) -> bool:
        child = self._next_child_scope()
        if child is None:
            return False
        self.current_scope = child
        return True

    def _exit_existing_scope(self) -> None:
        if self.current_scope.parent is not None:
            self.current_scope = self.current_scope.parent

    def _lookup(self, name: str):
        temp = self.current_scope
        while temp is not None:
            sym = temp.lookup(name)
            if sym is not None:
                return sym
            temp = temp.parent
        return None

    def _visit_unit(self, unit) -> None:
        if isinstance(unit, ast_nodes.Decl):
            return

        if isinstance(unit, ast_nodes.FuncDecl):
            if not self._enter_existing_scope():
                self._error(f"Internal semantic scope mismatch for function '{unit.name}'")
                return
            for inner in unit.body.units:
                self._visit_unit(inner)
            self._exit_existing_scope()
            return

        if isinstance(unit, ast_nodes.Stmt):
            self._visit_stmt(unit)

    def _visit_stmt(self, stmt) -> None:
        if isinstance(stmt, ast_nodes.Assign):
            lhs = self._lookup(stmt.name)
            rhs_t = self._visit_expr(stmt.expr)
            if lhs is None:
                # Undeclared diagnostics are already handled by symbol table phase.
                return
            if rhs_t and lhs.type in ("int", "float") and not self._is_assignable(lhs.type, rhs_t):
                self._error(
                    f"Type mismatch in assignment to '{stmt.name}' "
                    f"(expected {lhs.type}, got {rhs_t})"
                )
            return

        if isinstance(stmt, ast_nodes.PrintStmt):
            self._visit_expr(stmt.expr)
            return

        if isinstance(stmt, ast_nodes.IfStmt):
            cond_t = self._visit_bool_expr(stmt.cond)
            if cond_t != "bool":
                self._error("Invalid condition in if statement (expected boolean expression)")
            self._visit_block(stmt.then_block, "if-block")
            if stmt.else_block:
                self._visit_block(stmt.else_block, "else-block")
            return

        if isinstance(stmt, ast_nodes.WhileStmt):
            cond_t = self._visit_bool_expr(stmt.cond)
            if cond_t != "bool":
                self._error("Invalid condition in while statement (expected boolean expression)")
            self._visit_block(stmt.body, "while-block")
            return

        if isinstance(stmt, ast_nodes.Block):
            self._visit_block(stmt, "block")

    def _visit_block(self, block: ast_nodes.Block, name: str) -> None:
        if not self._enter_existing_scope():
            self._error(f"Internal semantic scope mismatch for block '{name}'")
            return
        for unit in block.units:
            self._visit_unit(unit)
        self._exit_existing_scope()

    def _visit_bool_expr(self, node) -> Optional[str]:
        if isinstance(node, ast_nodes.BoolOr) or isinstance(node, ast_nodes.BoolAnd):
            lt = self._visit_bool_expr(node.left)
            rt = self._visit_bool_expr(node.right)
            if lt != "bool" or rt != "bool":
                self._error("Logical operators require boolean operands")
            return "bool"

        if isinstance(node, ast_nodes.BoolNot):
            it = self._visit_bool_expr(node.inner)
            if it != "bool":
                self._error("Logical NOT requires a boolean operand")
            return "bool"

        if isinstance(node, ast_nodes.RelExpr):
            lt = self._visit_expr(node.left)
            rt = self._visit_expr(node.right)
            if not self._is_numeric(lt) or not self._is_numeric(rt):
                self._error("Relational operators require numeric operands")
            return "bool"

        # Fallback to expression type if caller passes expression nodes directly.
        return self._visit_expr(node)

    def _visit_expr(self, node) -> Optional[str]:
        if isinstance(node, ast_nodes.Var):
            sym = self._lookup(node.name)
            if sym is None:
                # Undeclared diagnostics are already handled by symbol table phase.
                return None
            if sym.type in ("int", "float"):
                return sym.type
            return None

        if isinstance(node, ast_nodes.IntLit):
            return "int"

        if isinstance(node, ast_nodes.FloatLit):
            return "float"

        if isinstance(node, ast_nodes.UnaryMinus):
            t = self._visit_expr(node.inner)
            if not self._is_numeric(t):
                self._error("Unary minus requires numeric operand")
                return None
            return t

        if isinstance(node, ast_nodes.BinOp):
            lt = self._visit_expr(node.left)
            rt = self._visit_expr(node.right)
            if lt is None or rt is None:
                return None

            if node.op == "%":
                if lt != "int" or rt != "int":
                    self._error("Modulus operator requires integer operands")
                    return None
                return "int"

            if node.op in ("+", "-", "*", "/"):
                if not self._is_numeric(lt) or not self._is_numeric(rt):
                    self._error(
                        f"Type mismatch in expression for operator '{node.op}' "
                        f"(got {lt} and {rt})"
                    )
                    return None
                if lt == "float" or rt == "float":
                    return "float"
                return "int"

            return None

        return None
