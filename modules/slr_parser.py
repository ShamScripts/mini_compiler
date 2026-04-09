"""SLR(1) Shift-Reduce Parser."""

from .tokens import TokenType, Token
from .grammar_utils import get_mini_compiler_grammar

class SLRParser:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t.type != TokenType.UNKNOWN]
        self.curr = 0
        self.stack = [0]  # State stack
        self.log = []
        self.errors = []
        
        # Initialize Grammar and Tables
        self.grammar = get_mini_compiler_grammar()
        self.action_table, self.goto_table, self.rules = self.grammar.get_slr_table()

    def _get_sym(self, token):
        """Map Token to Grammar Symbol."""
        if token.type == TokenType.EOF:
            return "$"
        # Keywords use lexemes in grammar
        if token.type in [TokenType.INT, TokenType.FLOAT, TokenType.IF, TokenType.ELSE, TokenType.WHILE, TokenType.PRINT]:
            return token.lexeme
        # Others use TokenType name
        return token.type.name

    def parse(self):
        self.log.append("START SLR(1) SHIFT-REDUCE PARSE")
        while True:
            if self.curr >= len(self.tokens):
                self.errors.append("Unexpected end of tokens.")
                return False

            state = self.stack[-1]
            curr_token = self.tokens[self.curr]
            tok_sym = self._get_sym(curr_token)
            
            # Format stack for trace
            stack_view = str(self.stack)
            if len(stack_view) > 50: stack_view = "..." + stack_view[-47:]
            self.log.append(f"Stack: {stack_view:<50} | Token: {tok_sym} ('{curr_token.lexeme}')")
            
            action = self.action_table.get((state, tok_sym))
            if not action:
                self.errors.append(f"Line {curr_token.line}: SLR Syntax Error at {tok_sym} in State {state}")
                return False
            
            if action == "ACC":
                self.log.append("SUCCESS: ACCEPT")
                return True
            
            if action.startswith("S"):
                next_state = int(action[1:])
                self.log.append(f"SHIFT to State {next_state}")
                self.stack.append(next_state)
                self.curr += 1
            elif action.startswith("R"):
                rule_idx = int(action[1:])
                lhs, rhs = self.rules[rule_idx]
                self.log.append(f"REDUCE by {lhs} -> {' '.join(rhs) if rhs else 'eps'}")
                
                # Pop RHS symbols (states) from stack
                for _ in range(len(rhs)):
                    self.stack.pop()
                
                # Push GOTO state
                top_state = self.stack[-1]
                goto_state = self.goto_table.get((top_state, lhs))
                if goto_state is None:
                    self.errors.append(f"Goto Error: No transition from {top_state} on {lhs}")
                    return False
                self.log.append(f"GOTO State {goto_state}")
                self.stack.append(goto_state)
            else:
                self.errors.append("Fatal Parser Error")
                return False

    def print_trace(self):
        print("\n  +-----------------------------------------------------------+")
        print("  |                     SLR(1) PARSE STACK TRACE              |")
        print("  +-----------------------------------------------------------+")
        for line in self.log:
            print(f"  |  {line:<56} |")
        print("  +-----------------------------------------------------------+\n")
