from .intermediate_code import TACInst

def is_literal(val):
    if val is None: return False
    # If it is a string representation of a boolean '0' or '1' or floats
    try:
        float(val)
        return True
    except ValueError:
        return False

def evaluate_op(op, a, b):
    try:
        a_val = float(a) if '.' in str(a) else int(a)
        b_val = float(b) if '.' in str(b) else int(b)
        if op == '+': return str(a_val + b_val)
        if op == '-': return str(a_val - b_val)
        if op == '*': return str(a_val * b_val)
        if op == '/': return str(a_val / b_val) if b_val != 0 else None
        if op == '<': return '1' if a_val < b_val else '0'
        if op == '>': return '1' if a_val > b_val else '0'
        if op == '<=': return '1' if a_val <= b_val else '0'
        if op == '>=': return '1' if a_val >= b_val else '0'
        if op == '==': return '1' if a_val == b_val else '0'
        if op == '!=': return '1' if a_val != b_val else '0'
        if op == '&&': return '1' if (a_val and b_val) else '0'
        if op == '||': return '1' if (a_val or b_val) else '0'
    except Exception:
        pass
    return None

def optimize_tac(tac_list):
    optimized = []
    constants = {}
    
    for inst in tac_list:
        # Clear constants on control flow branches to be safe
        if inst.op in ['LABEL', 'GOTO', 'IFFALSEGOTO', 'IFGOTO']:
            constants.clear()
            
        # Copy the instruction to avoid mutating the original
        new_inst = TACInst(inst.op, inst.arg1, inst.arg2, inst.result)
        
        # Substitute known constants
        if new_inst.arg1 in constants:
            new_inst.arg1 = constants[new_inst.arg1]
        if new_inst.arg2 in constants:
            new_inst.arg2 = constants[new_inst.arg2]
            
        # Try to fold
        if new_inst.op in ['+', '-', '*', '/', '<', '>', '<=', '>=', '==', '!=', '&&', '||']:
            if is_literal(new_inst.arg1) and is_literal(new_inst.arg2):
                res = evaluate_op(new_inst.op, new_inst.arg1, new_inst.arg2)
                if res is not None:
                    new_inst.op = 'ASSIGN'
                    new_inst.arg1 = res
                    new_inst.arg2 = None
                    constants[new_inst.result] = res
                else:
                    if new_inst.result:
                        constants.pop(new_inst.result, None)
            else:
                if new_inst.result:
                    constants.pop(new_inst.result, None)
        elif new_inst.op == '!':
            if is_literal(new_inst.arg1):
                try:
                    val = float(new_inst.arg1) if '.' in str(new_inst.arg1) else int(new_inst.arg1)
                    new_inst.op = 'ASSIGN'
                    new_inst.arg1 = '0' if val else '1'
                    constants[new_inst.result] = new_inst.arg1
                except Exception:
                    constants.pop(new_inst.result, None)
            else:
                constants.pop(new_inst.result, None)
        elif new_inst.op == 'ASSIGN':
            if is_literal(new_inst.arg1):
                constants[new_inst.result] = new_inst.arg1
            else:
                constants.pop(new_inst.result, None)
        elif new_inst.op == '-':
            # Unary minus (arg2 is None)
            if new_inst.arg2 is None and is_literal(new_inst.arg1):
                try:
                    val = float(new_inst.arg1) if '.' in str(new_inst.arg1) else int(new_inst.arg1)
                    new_inst.op = 'ASSIGN'
                    new_inst.arg1 = str(-val)
                    constants[new_inst.result] = new_inst.arg1
                except Exception:
                    constants.pop(new_inst.result, None)
            else:
                constants.pop(new_inst.result, None)
                
        optimized.append(new_inst)
        
    return optimized

def generate_target_code(tac_list):
    target_code = []
    # To avoid duplicate labels from memory ids, we use a simple counter
    rel_counter = 0
    for inst in tac_list:
        if inst.op == 'LABEL':
            target_code.append(f"{inst.arg1}:")
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
            # Pseudo-instruction for print
            target_code.append(f"    PUSH {inst.arg1}")
            target_code.append(f"    CALL print")
            target_code.append(f"    ADD ESP, 4")
        elif inst.op == '+':
            target_code.append(f"    MOV {inst.result}, {inst.arg1}")
            target_code.append(f"    ADD {inst.result}, {inst.arg2}")
        elif inst.op == '-':
            if inst.arg2 is None: # Unary minus
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
        elif inst.op in ['<', '>', '<=', '>=', '==', '!=']:
            # Pseudo-instruction for relationals, returning 0 or 1
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
            # Logical operations mapped simply
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
            target_code.append(f"    ; Unknown TAC: {inst}")
    return target_code
