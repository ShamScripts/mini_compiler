import collections

class Grammar:
    def __init__(self, productions, start_symbol):
        self.productions = productions
        self.start_symbol = start_symbol
        self.non_terminals = set(productions.keys())
        self.terminals = set()
        for head, bodies in productions.items():
            for body in bodies:
                for symbol in body:
                    if symbol not in self.non_terminals:
                        self.terminals.add(symbol)
        self.first = self._compute_first()
        self.follow = self._compute_follow()

    def _compute_first(self):
        first = collections.defaultdict(set)

        for t in self.terminals:
            first[t].add(t)

        changed = True
        while changed:
            changed = False
            for head, bodies in self.productions.items():
                for body in bodies:
                    if not body:
                        if "" not in first[head]:
                            first[head].add("")
                            changed = True
                    else:
                        all_have_epsilon = True

                        for symbol in body:
                            before = len(first[head])

                            first[head].update(first[symbol] - {""})

                            if len(first[head]) > before:
                                changed = True

                            if "" not in first[symbol]:
                                all_have_epsilon = False
                                break

                        if all_have_epsilon:
                            if "" not in first[head]:
                                first[head].add("")
                                changed = True

        return first

    def _compute_follow(self):
        follow = collections.defaultdict(set)
        follow[self.start_symbol].add("$")
        
        changed = True
        while changed:
            changed = False
            for head, bodies in self.productions.items():
                for body in bodies:
                    for i, symbol in enumerate(body):
                        if symbol in self.non_terminals:
                            before = len(follow[symbol])
                            rest = body[i+1:]
                            if not rest:
                                follow[symbol].update(follow[head])
                            else:
                                for next_symbol in rest:
                                    follow[symbol].update(self.first[next_symbol] - {""})
                                    if "" not in self.first[next_symbol]:
                                        break
                                else:
                                    follow[symbol].update(follow[head])
                            if len(follow[symbol]) > before: changed = True
        return follow

    def get_ll1_table(self):
        table = collections.defaultdict(dict)
        for head, bodies in self.productions.items():
            for body in bodies:
                body_first = set()
                if not body:
                    body_first.add("")
                else:
                    for symbol in body:
                        body_first.update(self.first[symbol] - {""})
                        if "" not in self.first[symbol]:
                            break
                    else:
                        body_first.add("")
                
                for terminal in body_first:
                    if terminal != "":
                        table[head][terminal] = body
                    else:
                        for f_terminal in self.follow[head]:
                            table[head][f_terminal] = body
        return table

    def get_slr_table(self):
        augmented_start = self.start_symbol + "'"
        augmented_rules = [(augmented_start, [self.start_symbol])]
        for head, bodies in self.productions.items():
            for body in bodies:
                augmented_rules.append((head, body))
        
        def closure(items):
            res = set(items)
            changed = True
            while changed:
                changed = False
                for head, body, dot in list(res):
                    if dot < len(body):
                        symbol = body[dot]
                        if symbol in self.non_terminals:
                            for prod_body in self.productions[symbol]:
                                new_item = (symbol, tuple(prod_body), 0)
                                if new_item not in res:
                                    res.add(new_item)
                                    changed = True
            return frozenset(res)

        def goto(items, symbol):
            new_items = []
            for head, body, dot in items:
                if dot < len(body) and body[dot] == symbol:
                    new_items.append((head, body, dot + 1))
            return closure(new_items)

        start_item = (augmented_start, (self.start_symbol,), 0)
        initial_state = closure([start_item])
        states = [initial_state]
        transitions = {}
        
        changed = True
        while changed:
            changed = False
            for i in range(len(states)):
                state = states[i]
                symbols = set()
                for head, body, dot in state:
                    if dot < len(body):
                        symbols.add(body[dot])
                
                for symbol in symbols:
                    next_state = goto(state, symbol)
                    if next_state and next_state not in states:
                        states.append(next_state)
                        changed = True
                    if next_state:
                        transitions[(i, symbol)] = states.index(next_state)

        action = {}
        goto_table = {}
        for i, state in enumerate(states):
            for head, body, dot in state:
                if dot < len(body):
                    symbol = body[dot]
                    if symbol in self.terminals:
                        action[(i, symbol)] = f"S{transitions[(i, symbol)]}"
                elif head == augmented_start:
                    action[(i, "$")] = "ACC"
                else:
                    rule_body = list(body)
                    rule_idx = -1
                    for idx, (r_head, r_body) in enumerate(augmented_rules):
                        if r_head == head and r_body == rule_body:
                            rule_idx = idx
                            break
                    for terminal in self.follow[head]:
                        action[(i, terminal)] = f"R{rule_idx}"
            
            for nt in self.non_terminals:
                if (i, nt) in transitions:
                    goto_table[(i, nt)] = transitions[(i, nt)]
        
        return action, goto_table, augmented_rules

MINI_COMPILER_GRAMMAR = {
    "Program": [["Decls", "Stmts"]],
    "Decls": [["Decl", "Decls"], []],
    "Decl": [["Type", "IDENTIFIER", "SEMICOLON"]],
    "Type": [["int"], ["float"]],
    "Stmts": [["Stmt", "Stmts"], []],
    "Stmt": [["Assign"], ["IfStmt"], ["WhileStmt"], ["PrintStmt"], ["Block"]],
    "Assign": [["IDENTIFIER", "ASSIGN", "BoolExpr", "SEMICOLON"]],
    "IfStmt": [["if", "LPAREN", "BoolExpr", "RPAREN", "Block", "ElsePart"]],
    "ElsePart": [["else", "Block"], []],
    "WhileStmt": [["while", "LPAREN", "BoolExpr", "RPAREN", "Block"]],
    "PrintStmt": [["print", "LPAREN", "BoolExpr", "RPAREN", "SEMICOLON"]],
    "Block": [["LBRACE", "Decls", "Stmts", "RBRACE"]],
    
    # Unified Expression Hierarchy (Resolves LL(1) Parentheses Conflict)
    "BoolExpr": [["BoolTerm", "BoolExprPrime"]],
    "BoolExprPrime": [["OR", "BoolTerm", "BoolExprPrime"], []],
    "BoolTerm": [["RelExpr", "BoolTermPrime"]],
    "BoolTermPrime": [["AND", "RelExpr", "BoolTermPrime"], []],
    "RelExpr": [["Expr", "RelExprPrime"]],
    "RelExprPrime": [["RelOp", "Expr"], []],
    "Expr": [["Term", "ExprPrime"]],
    "ExprPrime": [["PLUS", "Term", "ExprPrime"], ["MINUS", "Term", "ExprPrime"], []],
    "Term": [["Factor", "TermPrime"]],
    "TermPrime": [["MUL", "Factor", "TermPrime"], ["DIV", "Factor", "TermPrime"], ["MOD", "Factor", "TermPrime"], []],
    "Factor": [
        ["IDENTIFIER"], 
        ["INT_LITERAL"], 
        ["FLOAT_LITERAL"], 
        ["LPAREN", "BoolExpr", "RPAREN"], 
        ["NOT", "Factor"], 
        ["MINUS", "Factor"]
    ],
    "RelOp": [["LT"], ["GT"], ["LE"], ["GE"], ["EQ"], ["NE"]]
}

def get_mini_compiler_grammar():
    return Grammar(MINI_COMPILER_GRAMMAR, "Program")
