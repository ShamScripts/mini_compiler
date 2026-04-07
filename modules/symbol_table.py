"""Symbol Table with support for nested scopes."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Symbol:
    name: str
    type: str
    scope_level: int
    offset: int

    def __str__(self):
        return f"Symbol(name='{self.name}', type='{self.type}', scope={self.scope_level}, offset={self.offset})"


class Scope:
    def __init__(self, level: int):
        self.level = level
        self.symbols: Dict[str, Symbol] = {}

    def insert(self, symbol: Symbol) -> bool:
        if symbol.name in self.symbols:
            return False
        self.symbols[symbol.name] = symbol
        return True

    def lookup(self, name: str) -> Optional[Symbol]:
        return self.symbols.get(name)


class SymbolTable:
    def __init__(self):
        self.scopes: List[Scope] = [Scope(0)]  # Global scope
        self.current_level = 0
        self.next_offset = 0
        self.history: List[str] = []

    def enter_scope(self):
        self.current_level += 1
        self.scopes.append(Scope(self.current_level))
        self.history.append(f"ENTER SCOPE: Level {self.current_level}")

    def exit_scope(self):
        if self.current_level > 0:
            self.history.append(f"EXIT SCOPE: Level {self.current_level}")
            self.scopes.pop()
            self.current_level -= 1
        else:
            self.history.append("WARNING: Cannot exit global scope.")

    def insert(self, name: str, symbol_type: str) -> bool:
        # Determine offset based on type
        size = 4 if symbol_type == "int" else 8
        symbol = Symbol(name, symbol_type, self.current_level, self.next_offset)
        
        success = self.scopes[-1].insert(symbol)
        if success:
            self.next_offset += size
            self.history.append(f"INSERT: {symbol}")
        else:
            self.history.append(f"ERROR: Multiple declaration of '{name}' in scope {self.current_level}")
        return success

    def lookup(self, name: str) -> Optional[Symbol]:
        # Search from innermost to outermost scope
        for scope in reversed(self.scopes):
            sym = scope.lookup(name)
            if sym:
                return sym
        return None

    def dump(self):
        print("\n  +-----------------------------------------------------------+")
        print("  |                     SYMBOL TABLE TRACE                    |")
        print("  +-----------------------------------------------------------+")
        for line in self.history:
            print(f"  |  {line:<56} |")
        print("  +-----------------------------------------------------------+\n")
