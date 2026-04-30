from .intermediate_code import TACInst

def is_literal(val):
    if val is None: return False
    try:
        float(val)
        return True
    except ValueError:
        return False

def evaluate_op(op, a, b):
    try:
        # Detect if we should use float or int
        is_float = '.' in str(a) or '.' in str(b)
        a_val = float(a) if is_float else int(a)
        b_val = float(b) if is_float else int(b)
        
        if op == '+': res = a_val + b_val
        elif op == '-': res = a_val - b_val
        elif op == '*': res = a_val * b_val
        elif op == '/': 
            if b_val == 0: return None
            res = a_val / b_val
        elif op == '<': res = 1 if a_val < b_val else 0
        elif op == '>': res = 1 if a_val > b_val else 0
        elif op == '<=': res = 1 if a_val <= b_val else 0
        elif op == '>=': res = 1 if a_val >= b_val else 0
        elif op == '==': res = 1 if a_val == b_val else 0
        elif op == '!=': res = 1 if a_val != b_val else 0
        elif op == '&&': res = 1 if (a_val and b_val) else 0
        elif op == '||': res = 1 if (a_val or b_val) else 0
        elif op == '%': 
            if b_val == 0: return None
            res = a_val % b_val
        else: return None
        
        return str(res)
    except Exception:
        pass
    return None

def algebraic_simplify(op, a, b):
    """Apply algebraic identities."""
    if not is_literal(a) and not is_literal(b):
        return None
        
    # x + 0 = x, 0 + x = x
    if op == '+':
        if b == '0': return a
        if a == '0': return b
    # x - 0 = x, x - x = 0
    if op == '-':
        if b == '0': return a
        if a == b: return '0'
    # x * 1 = x, 1 * x = x, x * 0 = 0, 0 * x = 0
    if op == '*':
        if b == '1': return a
        if a == '1': return b
        if b == '0' or a == '0': return '0'
    # x / 1 = x, x / x = 1
    if op == '/':
        if b == '1': return a
        if a == b and a != '0': return '1'
        
    return None

def optimize_tac(tac_list):
    """
    Enhanced Optimization:
    1. Constant Folding & Propagation (Basic Block aware)
    2. Algebraic Simplification
    3. Dead Code Elimination
    """
    # --- PASS 1: Constant Folding, Propagation & Algebraic Simplification ---
    pass1 = []
    constants = {}
    
    for inst in tac_list:
        # Reset constants on any label or jump (very conservative basic block boundary)
        if inst.op in ['LABEL', 'GOTO', 'IFFALSEGOTO', 'IFGOTO']:
            constants.clear()
            
        new_inst = TACInst(inst.op, inst.arg1, inst.arg2, inst.result)
        
        # Substitute constants
        if new_inst.arg1 in constants:
            new_inst.arg1 = constants[new_inst.arg1]
        if new_inst.arg2 in constants:
            new_inst.arg2 = constants[new_inst.arg2]
            
        # 1. Constant Folding
        if new_inst.op in ['+', '-', '*', '/', '<', '>', '<=', '>=', '==', '!=', '&&', '||']:
            if is_literal(new_inst.arg1) and is_literal(new_inst.arg2):
                res = evaluate_op(new_inst.op, new_inst.arg1, new_inst.arg2)
                if res is not None:
                    new_inst.op = 'ASSIGN'
                    new_inst.arg1 = res
                    new_inst.arg2 = None
                    if new_inst.result: constants[new_inst.result] = res
                else:
                    if new_inst.result: constants.pop(new_inst.result, None)
            else:
                # 2. Algebraic Simplification
                simp = algebraic_simplify(new_inst.op, new_inst.arg1, new_inst.arg2)
                if simp is not None:
                    new_inst.op = 'ASSIGN'
                    new_inst.arg1 = simp
                    new_inst.arg2 = None
                    if new_inst.result and is_literal(simp): constants[new_inst.result] = simp
                else:
                    if new_inst.result: constants.pop(new_inst.result, None)
                    
        elif new_inst.op == 'ASSIGN':
            if is_literal(new_inst.arg1):
                constants[new_inst.result] = new_inst.arg1
            else:
                constants.pop(new_inst.result, None)
        
        pass1.append(new_inst)

    # --- PASS 2: Dead Code Elimination ---
    # Find all used variables
    used = set()
    for inst in pass1:
        if inst.op not in ['LABEL', 'GOTO']:
            if inst.arg1 and not is_literal(inst.arg1): used.add(inst.arg1)
            if inst.arg2 and not is_literal(inst.arg2): used.add(inst.arg2)
            # PRINT is a side-effect, so its argument is 'used'
            if inst.op == 'PRINT' and inst.arg1: used.add(inst.arg1)
            # For IFFALSEGOTO/IFGOTO
            if inst.op in ['IFFALSEGOTO', 'IFGOTO'] and inst.arg1: used.add(inst.arg1)

    # We only remove assignments to temporary variables (starting with 't')
    # assignments to user variables (x, y, etc.) are kept as they might be global or live out.
    optimized = []
    for inst in pass1:
        if inst.op == 'ASSIGN' and inst.result and inst.result.startswith('t'):
            if inst.result not in used:
                continue # Skip dead assignment
        optimized.append(inst)
        
    return optimized

def generate_target_code(tac_list):
    target_code = []
    target_code.append("; ---------------------------------------------------")
    target_code.append("; TARGET CODE (Pseudo-Assembly)")
    target_code.append("; Generated by Mini Compiler")
    target_code.append("; ---------------------------------------------------")
    
    rel_counter = 0
    for inst in tac_list:
        target_code.append("")
        target_code.append(f"    ; TAC: {inst}")
        
        if inst.op == 'LABEL':
            target_code[-1] = f"{inst.arg1}:" # Replace the comment with label
        elif inst.op == 'GOTO':
            target_code.append(f"    JMP {inst.arg1}")
        elif inst.op == 'IFFALSEGOTO':
            target_code.append(f"    CMP {inst.arg1}, 0")
            target_code.append(f"    JE {inst.arg2}")
        elif inst.op == 'IFGOTO':
            target_code.append(f"    CMP {inst.arg1}, 0")
            target_code.append(f"    JNE {inst.arg2}")
        elif inst.op == 'ASSIGN':
            target_code.append(f"    MOV {inst.result}, {inst.arg1}")
        elif inst.op == 'PRINT':
            target_code.append(f"    PUSH {inst.arg1}")
            target_code.append(f"    CALL print")
            target_code.append(f"    ADD ESP, 4")
        elif inst.op == '+':
            target_code.append(f"    MOV {inst.result}, {inst.arg1}")
            target_code.append(f"    ADD {inst.result}, {inst.arg2}")
        elif inst.op == '-':
            if inst.arg2 is None:
                target_code.append(f"    MOV {inst.result}, {inst.arg1}")
                target_code.append(f"    NEG {inst.result}")
            else:
                target_code.append(f"    MOV {inst.result}, {inst.arg1}")
                target_code.append(f"    SUB {inst.result}, {inst.arg2}")
        elif inst.op == '*':
            target_code.append(f"    MOV {inst.result}, {inst.arg1}")
            target_code.append(f"    MUL {inst.result}, {inst.arg2}")
        elif inst.op == '/':
            target_code.append(f"    MOV {inst.result}, {inst.arg1}")
            target_code.append(f"    DIV {inst.result}, {inst.arg2}")
        elif inst.op == '%':
            target_code.append(f"    MOV {inst.result}, {inst.arg1}")
            target_code.append(f"    MOD {inst.result}, {inst.arg2}")
        elif inst.op in ['<', '>', '<=', '>=', '==', '!=']:
            rel_counter += 1
            target_code.append(f"    CMP {inst.arg1}, {inst.arg2}")
            cc = {'<': 'JL', '>': 'JG', '<=': 'JLE', '>=': 'JGE', '==': 'JE', '!=': 'JNE'}[inst.op]
            l_true = f"L_REL_TRUE_{rel_counter}"
            l_end = f"L_REL_END_{rel_counter}"
            target_code.append(f"    {cc} {l_true}")
            target_code.append(f"    MOV {inst.result}, 0")
            target_code.append(f"    JMP {l_end}")
            target_code.append(f"{l_true}:")
            target_code.append(f"    MOV {inst.result}, 1")
            target_code.append(f"{l_end}:")
        elif inst.op in ['&&', '||', '!']:
            if inst.op == '&&':
                target_code.append(f"    MOV {inst.result}, {inst.arg1}")
                target_code.append(f"    AND {inst.result}, {inst.arg2}")
            elif inst.op == '||':
                target_code.append(f"    MOV {inst.result}, {inst.arg1}")
                target_code.append(f"    OR {inst.result}, {inst.arg2}")
            elif inst.op == '!':
                target_code.append(f"    MOV {inst.result}, {inst.arg1}")
                target_code.append(f"    NOT {inst.result}")
        else:
            target_code.append(f"    ; Unknown instruction mapping")
            
    return target_code
