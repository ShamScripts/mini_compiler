
from dataclasses import dataclass
from typing import List, Optional
from .parser import *

@dataclass
class TACInst:
    op: str
    arg1: Optional[str] = None
    arg2: Optional[str] = None
    result: Optional[str] = None
    
    def __str__(self):
        if self.op == 'LABEL':
            return f"{self.arg1}:"
        elif self.op == 'GOTO':
            return f"goto {self.arg1}"
        elif self.op == 'IFFALSEGOTO':
            return f"ifFalse {self.arg1} goto {self.arg2}"
        elif self.op == 'ASSIGN':
            return f"{self.result} = {self.arg1}"
        elif self.op == 'PRINT':
            return f"print {self.arg1}"
        elif self.arg2 is not None and self.result is not None:
            return f"{self.result} = {self.arg1} {self.op} {self.arg2}"
        elif self.arg1 is not None and self.result is not None:
            return f"{self.result} = {self.op} {self.arg1}"
        return f"{self.op} {self.arg1} {self.arg2} {self.result}"


@dataclass
class Triple:
    """Represents a triple in Three Address Code.
    In triple format, results are referenced by position rather than explicit result field."""
    op: str
    arg1: Optional[str] = None
    arg2: Optional[str] = None
    
    def __str__(self):
        if self.op == 'LABEL':
            return f"({self.op}, {self.arg1}, -)"
        elif self.op == 'GOTO':
            return f"({self.op}, {self.arg1}, -)"
        elif self.op == 'IFFALSEGOTO':
            return f"({self.op}, {self.arg1}, {self.arg2})"
        elif self.op == 'ASSIGN':
            return f"({self.op}, {self.arg1}, -)"
        elif self.op == 'PRINT':
            return f"({self.op}, {self.arg1}, -)"
        elif self.arg2 is not None:
            return f"({self.op}, {self.arg1}, {self.arg2})"
        elif self.arg1 is not None:
            return f"({self.op}, {self.arg1}, -)"
        return f"({self.op}, -, -)"

class TACGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.temp_count = 0
        self.label_count = 0
        self.code = []

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, inst: TACInst):
        self.code.append(inst)

    def generate(self):
        self.visit(self.ast)
        return self.code

    def visit(self, node):
        if isinstance(node, Program):
            for unit in node.units:
                self.visit(unit)
        elif isinstance(node, FuncDecl):
            self.emit(TACInst('LABEL', arg1=f"func_{node.name}"))
            self.visit(node.body)
        elif isinstance(node, Decl):
            pass # Declarations don't generate execution code directly
        elif isinstance(node, Assign):
            expr_val = self.visit(node.expr)
            self.emit(TACInst('ASSIGN', arg1=expr_val, result=node.name))
        elif isinstance(node, IfStmt):
            l_false = self.new_label()
            l_end = self.new_label()
            
            cond_val = self.visit(node.cond)
            self.emit(TACInst('IFFALSEGOTO', arg1=cond_val, arg2=l_false))
            
            # Then block
            self.visit(node.then_block)
            self.emit(TACInst('GOTO', arg1=l_end))
            
            # Else block
            self.emit(TACInst('LABEL', arg1=l_false))
            if node.else_block:
                self.visit(node.else_block)
            
            # End label
            self.emit(TACInst('LABEL', arg1=l_end))
            
        elif isinstance(node, WhileStmt):
            l_start = self.new_label()
            l_end = self.new_label()
            
            self.emit(TACInst('LABEL', arg1=l_start))
            cond_val = self.visit(node.cond)
            self.emit(TACInst('IFFALSEGOTO', arg1=cond_val, arg2=l_end))
            
            self.visit(node.body)
            self.emit(TACInst('GOTO', arg1=l_start))
            
            self.emit(TACInst('LABEL', arg1=l_end))
            
        elif isinstance(node, PrintStmt):
            val = self.visit(node.expr)
            self.emit(TACInst('PRINT', arg1=val))
            
        elif isinstance(node, Block):
            for unit in node.units:
                self.visit(unit)
                
        elif isinstance(node, BinOp):
            left_val = self.visit(node.left)
            right_val = self.visit(node.right)
            t = self.new_temp()
            self.emit(TACInst(node.op, arg1=left_val, arg2=right_val, result=t))
            return t
            
        elif isinstance(node, UnaryMinus):
            inner_val = self.visit(node.inner)
            t = self.new_temp()
            self.emit(TACInst('-', arg1=inner_val, result=t))
            return t
            
        elif isinstance(node, Var):
            return node.name
            
        elif isinstance(node, IntLit):
            return str(node.value)
            
        elif isinstance(node, FloatLit):
            return str(node.value)
            
        elif isinstance(node, RelExpr):
            left_val = self.visit(node.left)
            right_val = self.visit(node.right)
            t = self.new_temp()
            self.emit(TACInst(node.op, arg1=left_val, arg2=right_val, result=t))
            return t
            
        elif isinstance(node, BoolAnd):
            left_val = self.visit(node.left)
            right_val = self.visit(node.right)
            t = self.new_temp()
            self.emit(TACInst('&&', arg1=left_val, arg2=right_val, result=t))
            return t
            
        elif isinstance(node, BoolOr):
            left_val = self.visit(node.left)
            right_val = self.visit(node.right)
            t = self.new_temp()
            self.emit(TACInst('||', arg1=left_val, arg2=right_val, result=t))
            return t
            
        elif isinstance(node, BoolNot):
            inner_val = self.visit(node.inner)
            t = self.new_temp()
            self.emit(TACInst('!', arg1=inner_val, result=t))
            return t
            
        return None


class TripleGenerator:
    """Generates intermediate code in Triple format.
    In triples, the result is implicit - it's referenced by the position/index of the triple."""
    
    def __init__(self, ast):
        self.ast = ast
        self.temp_count = 0
        self.label_count = 0
        self.code = []
        self.temp_positions = {}  # Maps temporary variable names to their position

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, triple: Triple) -> Optional[str]:
        """Emit a triple and return its position reference if it has a result."""
        position = len(self.code)
        self.code.append(triple)
        
        # For operations that produce results, return a reference to the position
        if triple.op not in ['LABEL', 'GOTO', 'IFFALSEGOTO', 'PRINT', 'ASSIGN']:
            return f"({position})"
        return None

    def generate(self):
        self.visit(self.ast)
        return self.code

    def visit(self, node):
        if isinstance(node, Program):
            for unit in node.units:
                self.visit(unit)
        elif isinstance(node, FuncDecl):
            self.emit(Triple('LABEL', arg1=f"func_{node.name}"))
            self.visit(node.body)
        elif isinstance(node, Decl):
            pass  # Declarations don't generate execution code directly
        elif isinstance(node, Assign):
            expr_val = self.visit(node.expr)
            self.emit(Triple('ASSIGN', arg1=expr_val, arg2=node.name))
        elif isinstance(node, IfStmt):
            l_false = self.new_label()
            l_end = self.new_label()
            
            cond_val = self.visit(node.cond)
            self.emit(Triple('IFFALSEGOTO', arg1=cond_val, arg2=l_false))
            
            # Then block
            self.visit(node.then_block)
            self.emit(Triple('GOTO', arg1=l_end))
            
            # Else block
            self.emit(Triple('LABEL', arg1=l_false))
            if node.else_block:
                self.visit(node.else_block)
            
            # End label
            self.emit(Triple('LABEL', arg1=l_end))
            
        elif isinstance(node, WhileStmt):
            l_start = self.new_label()
            l_end = self.new_label()
            
            self.emit(Triple('LABEL', arg1=l_start))
            cond_val = self.visit(node.cond)
            self.emit(Triple('IFFALSEGOTO', arg1=cond_val, arg2=l_end))
            
            self.visit(node.body)
            self.emit(Triple('GOTO', arg1=l_start))
            
            self.emit(Triple('LABEL', arg1=l_end))
            
        elif isinstance(node, PrintStmt):
            val = self.visit(node.expr)
            self.emit(Triple('PRINT', arg1=val))
            
        elif isinstance(node, Block):
            for unit in node.units:
                self.visit(unit)
                
        elif isinstance(node, BinOp):
            left_val = self.visit(node.left)
            right_val = self.visit(node.right)
            triple = Triple(node.op, arg1=left_val, arg2=right_val)
            return self.emit(triple)
            
        elif isinstance(node, UnaryMinus):
            inner_val = self.visit(node.inner)
            triple = Triple('-', arg1=inner_val)
            return self.emit(triple)
            
        elif isinstance(node, Var):
            return node.name
            
        elif isinstance(node, IntLit):
            return str(node.value)
            
        elif isinstance(node, FloatLit):
            return str(node.value)
            
        elif isinstance(node, RelExpr):
            left_val = self.visit(node.left)
            right_val = self.visit(node.right)
            triple = Triple(node.op, arg1=left_val, arg2=right_val)
            return self.emit(triple)
            
        elif isinstance(node, BoolAnd):
            left_val = self.visit(node.left)
            right_val = self.visit(node.right)
            triple = Triple('&&', arg1=left_val, arg2=right_val)
            return self.emit(triple)
            
        elif isinstance(node, BoolOr):
            left_val = self.visit(node.left)
            right_val = self.visit(node.right)
            triple = Triple('||', arg1=left_val, arg2=right_val)
            return self.emit(triple)
            
        elif isinstance(node, BoolNot):
            inner_val = self.visit(node.inner)
            triple = Triple('!', arg1=inner_val)
            return self.emit(triple)
            
        return None


def generate_tac(ast):
    generator = TACGenerator(ast)
    return generator.generate()


def generate_triples(ast):
    """Generate intermediate code in triple format."""
    generator = TripleGenerator(ast)
    return generator.generate()
