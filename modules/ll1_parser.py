"""LL(1) Table-Driven Parser."""

from .tokens import TokenType, Token
from .grammar_utils import get_mini_compiler_grammar

class LL1Parser:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t.type != TokenType.UNKNOWN]
        self.curr = 0
        self.stack = ["$", "Program"]
        self.log = []
        self.errors = []
        
        # Initialize Grammar and Table
        self.grammar = get_mini_compiler_grammar()
        self.table = self.grammar.get_ll1_table()

    def _get_sym(self, token):
        """Map Token to Grammar Symbol."""
        if token.type == TokenType.EOF:
            return "$"
        if token.type in [TokenType.INT, TokenType.FLOAT, TokenType.IF, TokenType.ELSE, TokenType.WHILE, TokenType.PRINT]:
            return token.lexeme
        return token.type.name

    def parse(self):
        self.log.append("START LL(1) PARSE")
        while self.stack:
            if self.curr >= len(self.tokens):
                self.errors.append("Unexpected end of tokens.")
                return False

            top = self.stack.pop()
            curr_token = self.tokens[self.curr]
            tok_sym = self._get_sym(curr_token)
            
            # Detailed stack logging for trace
            stack_view = str(self.stack + [top])
            if len(stack_view) > 50: stack_view = "..." + stack_view[-47:]
            self.log.append(f"Stack: {stack_view:<50} | Token: {tok_sym} ('{curr_token.lexeme}')")

            if top == "$":
                if tok_sym == "$":
                    self.log.append("SUCCESS: Input consumed.")
                    return True
                else:
                    self.errors.append("Extra input after program end.")
                    return False
            
            # Non-terminal expansion
            if top in self.grammar.non_terminals:
                production = self.table.get(top, {}).get(tok_sym)
                if production is not None:
                    self.log.append(f"EXPAND: {top} -> {' '.join(production) if production else 'eps'}")
                    for sym in reversed(production):
                        self.stack.append(sym)
                else:
                    self.errors.append(f"Line {curr_token.line}: Syntax Error - Unexpected token {tok_sym} for Non-terminal {top}")
                    return False
            else:
                # Terminal matching
                if top == tok_sym:
                    self.log.append(f"MATCH: {top}")
                    self.curr += 1
                else:
                    self.errors.append(f"Line {curr_token.line}: Syntax Error - Expected terminal '{top}', but found '{curr_token.lexeme}' ({tok_sym})")
                    return False
        return True

    def print_trace(self):
        print("\n  +-----------------------------------------------------------+")
        print("  |                     LL(1) PARSE STACK TRACE               |")
        print("  +-----------------------------------------------------------+")
        for line in self.log:
            print(f"  |  {line:<56} |")
        print("  +-----------------------------------------------------------+\n")
