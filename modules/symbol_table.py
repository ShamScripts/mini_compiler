"""Symbol Table with support for nested scopes."""

from dataclasses import dataclass
from typing import Dict, List, Optional
from . import parser as ast_nodes


@dataclass
class Symbol:
    name: str
    kind: str  # 'var', 'fun', 'arg', 'scope'
    type: str  # data type or return type
    scope_level: int
    offset: int

    def __str__(self):
        return f"Symbol(name='{self.name}', kind='{self.kind}', type='{self.type}', scope={self.scope_level}, offset={self.offset})"


class Scope:
    def __init__(self, level: int, name: str = "Global", parent: Optional["Scope"] = None):
        self.level = level
        self.name = name
        self.symbols: Dict[str, Symbol] = {}
        self.parent = parent
        self.children: List["Scope"] = []
        self.next_offset = 0

    def insert(self, symbol: Symbol) -> bool:
        if symbol.name in self.symbols:
            return False
        self.symbols[symbol.name] = symbol
        return True

    def lookup(self, name: str) -> Optional[Symbol]:
        return self.symbols.get(name)


class SymbolTable:
    def __init__(self):
        self.root = Scope(0, "Global")
        self.current_scope = self.root
        self.current_level = 0
        self.history: List[str] = []

    def enter_scope(self, name: str = "Sub-Scope") -> None:
        self.current_level += 1
        new_scope = Scope(self.current_level, name=name, parent=self.current_scope)
        self.current_scope.children.append(new_scope)

        self.current_scope = new_scope
        self.history.append(f"ENTER SCOPE: {name} (Level {self.current_level})")

    def exit_scope(self) -> None:
        if self.current_scope.parent:
            self.history.append(f"EXIT SCOPE: {self.current_scope.name}")
            self.current_scope = self.current_scope.parent
            self.current_level -= 1
        else:
            self.history.append("WARNING: Cannot exit global scope.")

    def insert(self, name: str, symbol_type: str, kind: str = "var") -> bool:
        # Determine offset based on type
        size = 4 if symbol_type == "int" else 8
        if kind != "var":
            size = 0

        symbol = Symbol(name, kind, symbol_type, self.current_level, self.current_scope.next_offset)
        
        success = self.current_scope.insert(symbol)
        if success:
            self.current_scope.next_offset += size
            self.history.append(f"INSERT: {name} ({kind}: {symbol_type}) at Scope {self.current_level}")
        else:
            self.history.append(f"ERROR: Multiple declaration of '{name}' in scope {self.current_level}")
        return success

    def lookup(self, name: str) -> Optional[Symbol]:
        # Search from innermost to outermost scope using parent pointers
        temp = self.current_scope
        while temp:
            sym = temp.lookup(name)
            if sym:
                return sym
            temp = temp.parent
        return None

    def dump(self):
        print("\n  +-----------------------------------------------------------+")
        print("  |                     SYMBOL TABLE TRACE                    |")
        print("  +-----------------------------------------------------------+")
        for line in self.history:
            print(f"  |  {line:<56} |")
        print("  +-----------------------------------------------------------+\n")

    def print_multi_tables(self):
        print("\n  +===========================================================+")
        print("  |                INDIVIDUAL SYMBOL TABLES                   |")
        print("  +===========================================================+")
        self._print_scope_tables_recursive(self.root)

    def build_from_ast(self, ast: ast_nodes.Program) -> None:
        """Populate symbol table by traversing the parser AST."""
        self.history.append("BUILD: Start AST-driven symbol table construction")
        self._visit_program(ast)
        self.history.append("BUILD: Completed AST-driven symbol table construction")

    def _visit_program(self, program: ast_nodes.Program) -> None:
        for unit in program.units:
            self._visit_unit(unit)

    def _visit_unit(self, unit) -> None:
        if isinstance(unit, ast_nodes.Decl):
            self.insert(unit.name, unit.type_name, kind="var")
        elif isinstance(unit, ast_nodes.FuncDecl):
            sig = f"{unit.return_type} -> {unit.param.type_name if unit.param else 'void'}"
            self.insert(unit.name, sig, kind="fun")
            self.enter_scope(f"func {unit.name}")
            if unit.param:
                self.insert(unit.param.name, unit.param.type_name, kind="arg")
            # Function body uses the function scope already created above.
            for inner in unit.body.units:
                self._visit_unit(inner)
            self.exit_scope()
        elif isinstance(unit, ast_nodes.Stmt):
            self._visit_stmt(unit)

    def _visit_stmt(self, stmt) -> None:
        if isinstance(stmt, ast_nodes.Assign):
            lhs = self.lookup(stmt.name)
            if lhs:
                self.history.append(
                    f"LOOKUP: {stmt.name} resolved to Scope {lhs.scope_level} (offset {lhs.offset})"
                )
            else:
                self.history.append(f"ERROR: Undeclared identifier '{stmt.name}' used in assignment")
            self._visit_expr(stmt.expr)
        elif isinstance(stmt, ast_nodes.PrintStmt):
            self._visit_expr(stmt.expr)
        elif isinstance(stmt, ast_nodes.IfStmt):
            self._visit_bool_expr(stmt.cond)
            self._visit_block(stmt.then_block, name="if-block")
            if stmt.else_block:
                self._visit_block(stmt.else_block, name="else-block")
        elif isinstance(stmt, ast_nodes.WhileStmt):
            self._visit_bool_expr(stmt.cond)
            self._visit_block(stmt.body, name="while-block")
        elif isinstance(stmt, ast_nodes.Block):
            self._visit_block(stmt, name="block")

    def _visit_block(self, block: ast_nodes.Block, name: str) -> None:
        self.enter_scope(name)
        for unit in block.units:
            self._visit_unit(unit)
        self.exit_scope()

    def _visit_bool_expr(self, node) -> None:
        if isinstance(node, ast_nodes.BoolOr) or isinstance(node, ast_nodes.BoolAnd):
            self._visit_bool_expr(node.left)
            self._visit_bool_expr(node.right)
        elif isinstance(node, ast_nodes.BoolNot):
            self._visit_bool_expr(node.inner)
        elif isinstance(node, ast_nodes.RelExpr):
            self._visit_expr(node.left)
            self._visit_expr(node.right)

    def _visit_expr(self, node) -> None:
        if isinstance(node, ast_nodes.Var):
            sym = self.lookup(node.name)
            if sym:
                self.history.append(
                    f"LOOKUP: {node.name} resolved to Scope {sym.scope_level} (offset {sym.offset})"
                )
            else:
                self.history.append(f"ERROR: Undeclared identifier '{node.name}' used in expression")
        elif isinstance(node, ast_nodes.BinOp):
            self._visit_expr(node.left)
            self._visit_expr(node.right)
        elif isinstance(node, ast_nodes.UnaryMinus):
            self._visit_expr(node.inner)

    def _print_scope_tables_recursive(self, scope: Scope):
        parent_name = scope.parent.name if scope.parent else "None"
        header = f"Scope: {scope.name:<15} | Parent: {parent_name:<15}"
        
        bar = "-" * 59
        print(f"  | {header} |")
        print(f"  | +{bar}+ |")
        print(f"  | | {'Label':<15} | {'Kind':<15} | {'Type':<21} | |")
        print(f"  | +{bar}+ |")
        
        if not scope.symbols:
            print(f"  | | {'(empty)':<55} | |")
        else:
            for name, sym in scope.symbols.items():
                kind_display = sym.kind
                type_display = sym.type
                print(f"  | | {name:<15} | {kind_display:<15} | {type_display:<21} | |")
        
        print(f"  | +{bar}+ |\n")
        
        for child in scope.children:
            self._print_scope_tables_recursive(child)
