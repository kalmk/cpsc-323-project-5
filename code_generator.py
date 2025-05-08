# Import regular expression module. Using it to parse each TAC line with re.match
import re

class CodeGenerator:
    def __init__(self):
        # mapping variable/temporary name to MIPS register
        self.var_reg = {}
        # pool of general-purpose registers (avoid spills):
        # $t0-$t9, $s1-$s7 (reserve $s0), $a0-$a3, $v0-$v1
        self.reg_pool = [
            '$t0','$t1','$t2','$t3','$t4','$t5','$t6','$t7','$t8','$t9',
            '$s1','$s2','$s3','$s4','$s5','$s6','$s7',
            '$a0','$a1','$a2','$a3','$v0','$v1'
        ]
        self.next_reg = 0

    def get_reg(self, var):
        # numeric constant: return directly
        if var.isdigit():
            return var
        # allocate on first use
        if var not in self.var_reg:
            if var == 'x':
                self.var_reg[var] = '$s0'  # base address for array x
            else:
                self.var_reg[var] = self.reg_pool[self.next_reg]
                self.next_reg += 1
        return self.var_reg[var]

    def generate(self, tac_lines):
        """
        Working under the assumtion that we should read in the test cases verbatim, 
        we are using re.match to strip the (#'s) from the input

        """
        # parse labels
        instrs = []
        label_map = {}
        for line in tac_lines:
            # Strip (#'s) from input using regex
            match = re.match(r"\(?([0-9]+)\)?\s*(.*)", line)
            if not match:
                continue
            label, body = match.groups()
            label_map[label] = f"L{label}"
            instrs.append((label, body.strip()))

        # prologue for .asm file
        code = [
            ".data",
            "  x: .space 400",
            ".text",
            ".globl main",
            "main:"  
        ]

        # translate
        for label, tac_instruc in instrs:
            code.append(f"{label_map[label]}:")
            code.extend(self._gen_instr(tac_instruc, label_map))

        # epilogue
        code.append("  jr $ra")
        return "\n".join(code)

    def _gen_instr(self, tac_instruc, label_map):
        out = []
        # return
        if tac_instruc == 'return':
            return ["  jr $ra"]

        # conditional branch
        if tac_instruc.startswith('if '):
            match = re.match(
                r"if\s+(\w+)\s*(<=|>=|==|!=|<|>)\s*(\w+)\s*then\s*goto\s*\(?([0-9]+)\)?",
                tac_instruc
            )
            if match:
                a, op, b, tgt = match.groups()
                ra, rb = self.get_reg(a), self.get_reg(b)
                label = label_map[tgt]
                op_map = {'<=':'ble','>=':'bge','==':'beq','!=':'bne','<':'blt','>':'bgt'}
                out.append(f"  {op_map[op]} {ra}, {rb}, {label}")
                return out

        # unconditional jump
        if tac_instruc.startswith('goto'):
            match = re.match(r"goto\s*\(?([0-9]+)\)?", tac_instruc)
            if match:
                out.append(f"  j {label_map[match.group(1)]}")
            return out

        # load/store
        if '=' in tac_instruc:
            # array load: dst = arr[idx]
            # m# vars stores the result of re.match
            m1 = re.match(r"(\w+)\s*=\s*(\w+)\[(\w+)\]", tac_instruc)
            if m1:
                dst, arr, idx = m1.groups()
                out.append(f"  add $at, {self.get_reg(arr)}, {self.get_reg(idx)}")
                out.append(f"  lw {self.get_reg(dst)}, 0($at)")
                return out

            # array store: arr[idx] = source
            m2 = re.match(r"(\w+)\[(\w+)\]\s*=\s*(\w+)", tac_instruc)
            if m2:
                arr, idx, source = m2.groups()
                out.append(f"  add $at, {self.get_reg(arr)}, {self.get_reg(idx)}")
                out.append(f"  sw {self.get_reg(source)}, 0($at)")
                return out

            # simple copy or binary op
            lhs, rhs = [s.strip() for s in tac_instruc.split('=',1)]
            toks = rhs.split()

            # copy: lhs = rhs
            if len(toks) == 1:
                source = toks[0]
                destination_register = self.get_reg(lhs)
                if source.isdigit():
                    out.append(f"  li {destination_register}, {source}")
                else:
                    out.append(f"  move {destination_register}, {self.get_reg(source)}")
                return out

            # binary operation: lhs = op1 op op2
            if len(toks) == 3:
                op1, op, op2 = toks
                destination_register = self.get_reg(lhs)
                r1 = self.get_reg(op1)

                # immediate add/sub
                if op2.isdigit() and op in ['+','-']:
                    imm = op2 if op == '+' else f"-{op2}"
                    out.append(f"  addi {destination_register}, {r1}, {imm}")
                else:
                    # load op2 into register or $at
                    if op2.isdigit():
                        out.append(f"  li $at, {op2}")
                        r2 = '$at'
                    else:
                        r2 = self.get_reg(op2)

                    # emit binary instruction
                    if op == '+':      out.append(f"  add {destination_register}, {r1}, {r2}")
                    elif op == '-':    out.append(f"  sub {destination_register}, {r1}, {r2}")
                    elif op == '*':    out.append(f"  mul {destination_register}, {r1}, {r2}")
                    elif op == '/':    
                        out.append(f"  div {r1}, {r2}")
                        out.append(f"  mflo {destination_register}")

                return out

        return out