"""LL(1) Table-Driven Parser."""

from .tokens import TokenType, Token, SyntaxErrorReport

class LL1Parser:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t.type != TokenType.UNKNOWN]
        self.curr = 0
        self.stack = ["$", "Program"]
        self.log = []
        self.errors = []
        
        # Comprehensive LL(1) Table for Mini Compiler
        self.table = {
            "Program": {
                TokenType.INT: ["Decls", "Stmts"],
                TokenType.FLOAT: ["Decls", "Stmts"],
                TokenType.IDENTIFIER: ["Decls", "Stmts"],
                TokenType.IF: ["Decls", "Stmts"],
                TokenType.WHILE: ["Decls", "Stmts"],
                TokenType.PRINT: ["Decls", "Stmts"],
                TokenType.LBRACE: ["Decls", "Stmts"],
                TokenType.EOF: ["Decls", "Stmts"],
            },
            "Decls": {
                TokenType.INT: ["Decl", "Decls"],
                TokenType.FLOAT: ["Decl", "Decls"],
                TokenType.IDENTIFIER: [],
                TokenType.IF: [],
                TokenType.WHILE: [],
                TokenType.PRINT: [],
                TokenType.LBRACE: [],
                TokenType.RBRACE: [],
                TokenType.EOF: [],
            },
            "Decl": {
                TokenType.INT: ["Type", "IDENTIFIER", "SEMICOLON"],
                TokenType.FLOAT: ["Type", "IDENTIFIER", "SEMICOLON"],
            },
            "Type": {
                TokenType.INT: ["int"],
                TokenType.FLOAT: ["float"],
            },
            "Stmts": {
                TokenType.IDENTIFIER: ["Stmt", "Stmts"],
                TokenType.IF: ["Stmt", "Stmts"],
                TokenType.WHILE: ["Stmt", "Stmts"],
                TokenType.PRINT: ["Stmt", "Stmts"],
                TokenType.LBRACE: ["Stmt", "Stmts"],
                TokenType.RBRACE: [],
                TokenType.EOF: [],
            },
            "Stmt": {
                TokenType.IDENTIFIER: ["Assign"],
                TokenType.IF: ["IfStmt"],
                TokenType.WHILE: ["WhileStmt"],
                TokenType.PRINT: ["PrintStmt"],
                TokenType.LBRACE: ["Block"],
            },
            "Assign": {
                TokenType.IDENTIFIER: ["IDENTIFIER", "ASSIGN", "Expr", "SEMICOLON"],
            },
            "IfStmt": {
                TokenType.IF: ["if", "LPAREN", "BoolExpr", "RPAREN", "Block", "ElsePart"],
            },
            "ElsePart": {
                TokenType.ELSE: ["else", "Block"],
                TokenType.IDENTIFIER: [],
                TokenType.IF: [],
                TokenType.WHILE: [],
                TokenType.PRINT: [],
                TokenType.LBRACE: [],
                TokenType.RBRACE: [],
                TokenType.EOF: [],
            },
            "WhileStmt": {
                TokenType.WHILE: ["while", "LPAREN", "BoolExpr", "RPAREN", "Block"],
            },
            "PrintStmt": {
                TokenType.PRINT: ["print", "LPAREN", "Expr", "RPAREN", "SEMICOLON"],
            },
            "Block": {
                TokenType.LBRACE: ["LBRACE", "Decls", "Stmts", "RBRACE"],
            },
            "Expr": {
                TokenType.IDENTIFIER: ["Term", "ExprPrime"],
                TokenType.INT_LITERAL: ["Term", "ExprPrime"],
                TokenType.FLOAT_LITERAL: ["Term", "ExprPrime"],
                TokenType.LPAREN: ["Term", "ExprPrime"],
            },
            "ExprPrime": {
                TokenType.PLUS: ["PLUS", "Term", "ExprPrime"],
                TokenType.MINUS: ["MINUS", "Term", "ExprPrime"],
                TokenType.SEMICOLON: [],
                TokenType.RPAREN: [],
                # FOLLOW(Expr) includes relational operators and AND/OR
                TokenType.LT: [], TokenType.GT: [], TokenType.LE: [], TokenType.GE: [], TokenType.EQ: [], TokenType.NE: [],
                TokenType.AND: [], TokenType.OR: [],
            },
            "Term": {
                TokenType.IDENTIFIER: ["Factor", "TermPrime"],
                TokenType.INT_LITERAL: ["Factor", "TermPrime"],
                TokenType.FLOAT_LITERAL: ["Factor", "TermPrime"],
                TokenType.LPAREN: ["Factor", "TermPrime"],
            },
            "TermPrime": {
                TokenType.MUL: ["MUL", "Factor", "TermPrime"],
                TokenType.DIV: ["DIV", "Factor", "TermPrime"],
                TokenType.MOD: ["MOD", "Factor", "TermPrime"],
                TokenType.PLUS: [], TokenType.MINUS: [],
                TokenType.SEMICOLON: [], TokenType.RPAREN: [],
                TokenType.LT: [], TokenType.GT: [], TokenType.LE: [], TokenType.GE: [], TokenType.EQ: [], TokenType.NE: [],
                TokenType.AND: [], TokenType.OR: [],
            },
            "Factor": {
                TokenType.IDENTIFIER: ["IDENTIFIER"],
                TokenType.INT_LITERAL: ["INT_LITERAL"],
                TokenType.FLOAT_LITERAL: ["FLOAT_LITERAL"],
                TokenType.LPAREN: ["LPAREN", "Expr", "RPAREN"],
            },
            "BoolExpr": {
                TokenType.NOT: ["BoolTerm", "BoolExprPrime"],
                TokenType.LPAREN: ["BoolTerm", "BoolExprPrime"],
                TokenType.IDENTIFIER: ["BoolTerm", "BoolExprPrime"],
                TokenType.INT_LITERAL: ["BoolTerm", "BoolExprPrime"],
                TokenType.FLOAT_LITERAL: ["BoolTerm", "BoolExprPrime"],
            },
            "BoolExprPrime": {
                TokenType.OR: ["OR", "BoolTerm", "BoolExprPrime"],
                TokenType.RPAREN: [],
                TokenType.EOF: [],
            },
            "BoolTerm": {
                TokenType.NOT: ["BoolFactor", "BoolTermPrime"],
                TokenType.LPAREN: ["BoolFactor", "BoolTermPrime"],
                TokenType.IDENTIFIER: ["BoolFactor", "BoolTermPrime"],
                TokenType.INT_LITERAL: ["BoolFactor", "BoolTermPrime"],
                TokenType.FLOAT_LITERAL: ["BoolFactor", "BoolTermPrime"],
            },
            "BoolTermPrime": {
                TokenType.AND: ["AND", "BoolFactor", "BoolTermPrime"],
                TokenType.OR: [],
                TokenType.RPAREN: [],
            },
            "BoolFactor": {
                TokenType.NOT: ["NOT", "BoolFactor"],
                TokenType.LPAREN: ["LPAREN", "BoolExpr", "RPAREN"],
                TokenType.IDENTIFIER: ["RelExpr"],
                TokenType.INT_LITERAL: ["RelExpr"],
                TokenType.FLOAT_LITERAL: ["RelExpr"],
            },
            "RelExpr": {
                TokenType.IDENTIFIER: ["Expr", "RelOp", "Expr"],
                TokenType.INT_LITERAL: ["Expr", "RelOp", "Expr"],
                TokenType.FLOAT_LITERAL: ["Expr", "RelOp", "Expr"],
                TokenType.LPAREN: ["Expr", "RelOp", "Expr"],
            },
            "RelOp": {
                TokenType.LT: ["LT"], TokenType.GT: ["GT"],
                TokenType.LE: ["LE"], TokenType.GE: ["GE"],
                TokenType.EQ: ["EQ"], TokenType.NE: ["NE"],
            }
        }

    def parse(self):
        self.log.append("START LL(1) PARSE")
        while self.stack:
            if self.curr >= len(self.tokens):
                self.errors.append("Unexpected end of tokens.")
                return False

            top = self.stack.pop()
            curr_token = self.tokens[self.curr]
            
            # Detailed stack logging for trace
            stack_view = str(self.stack + [top])
            if len(stack_view) > 50: stack_view = "..." + stack_view[-47:]
            self.log.append(f"Stack: {stack_view:<50} | Token: {curr_token.type.name} ('{curr_token.lexeme}')")

            if top == "$":
                if curr_token.type == TokenType.EOF:
                    self.log.append("SUCCESS: Input consumed.")
                    return True
                else:
                    self.errors.append("Extra input after program end.")
                    return False
            
            # Determine if 'top' is a terminal or non-terminal
            if top in self.table:
                # Non-terminal expansion
                if curr_token.type in self.table[top]:
                    production = self.table[top][curr_token.type]
                    self.log.append(f"EXPAND: {top} -> {' '.join(production) if production else 'ε'}")
                    for sym in reversed(production):
                        self.stack.append(sym)
                else:
                    self.errors.append(f"Line {curr_token.line}: Syntax Error - Unexpected token {curr_token.type.name} ('{curr_token.lexeme}') for Non-terminal {top}")
                    return False
            else:
                # Terminal matching
                is_match = False
                if top.isupper(): # Token type name like IDENTIFIER, RPAREN, etc.
                    if top == curr_token.type.name:
                        is_match = True
                elif top in ["int", "float", "if", "else", "while", "print"]:
                    if curr_token.lexeme == top:
                        is_match = True
                
                if is_match:
                    self.log.append(f"MATCH: {top}")
                    self.curr += 1
                else:
                    self.errors.append(f"Line {curr_token.line}: Syntax Error - Expected terminal '{top}', but found '{curr_token.lexeme}' ({curr_token.type.name})")
                    return False
        return True

    def get_trace(self):
        return "\n".join(self.log)

    def print_trace(self):
        print("\n  +-----------------------------------------------------------+")
        print("  |                     LL(1) PARSE STACK TRACE               |")
        print("  +-----------------------------------------------------------+")
        for line in self.log:
            print(f"  |  {line:<56} |")
        print("  +-----------------------------------------------------------+\n")
