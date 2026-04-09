"""Symbol Table with support for nested scopes."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


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
        self.next_offset = 0
        self.history: List[str] = []

    def enter_scope(self, name: str = "Sub-Scope") -> None:
        self.current_level += 1
        new_scope = Scope(self.current_level, name=name, parent=self.current_scope)
        self.current_scope.children.append(new_scope)
        
        # Cross-link: Add the sub-scope as an entry in the parent's table
        entry_name = name if " " not in name else name.split()[-1]
        self.current_scope.insert(Symbol(entry_name, "scope", "inner", self.current_level-1, 0))
        
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
            
        symbol = Symbol(name, kind, symbol_type, self.current_level, self.next_offset)
        
        success = self.current_scope.insert(symbol)
        if success:
            self.next_offset += size
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
