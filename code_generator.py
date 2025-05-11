# Importing regex module's re.match function
import re


class CodeGenerator:
    def __init__(self):
        # map symbol names to MIPS registers
        self.register_map = {}
        # reserve $s0 for array base 'x', then general-purpose registers
        self.register_pool = [
            '$t0', '$t1', '$t2', '$t3', '$t4', '$t5', '$t6', '$t7', '$t8', '$t9',
            '$s1', '$s2', '$s3', '$s4', '$s5', '$s6', '$s7',
            '$a0', '$a1', '$a2', '$a3', '$v0', '$v1'
        ]
        self.next_register = 0

    def get_register(self, symbol):
        # immediate constants stay as literals
        if symbol.isdigit():
            return symbol
        # allocate a register if first seen
        if symbol not in self.register_map:
            if symbol == 'x':
                self.register_map[symbol] = '$s0'
            else:
                if self.next_register >= len(self.register_pool):
                    raise RuntimeError('Out of registers')
                self.register_map[symbol] = self.register_pool[self.next_register]
                self.next_register += 1
        return self.register_map[symbol]

    def generate(self, tac_lines_list):
        # tac_lines_list is a Python list of TAC instructions in order
        numbered_instructions = list(enumerate(tac_lines_list, start=1))
        label_map = {index: f'L{index}' for index, _ in numbered_instructions}

        # emit prologue
        mips_lines = [
            '.data',
            '  x: .space 400',
            '.text',
            '.globl main',
            'main:'
        ]

        # translate each TAC instruction
        for index, instruction_text in numbered_instructions:
            mips_lines.append(f"{label_map[index]}:")
            mips_lines.extend(self._translate_instruction(
                instruction_text, label_map))

        # emit epilogue
        mips_lines.append('  jr $ra')
        return '\n'.join(mips_lines)

    def _translate_instruction(self, instruction_text, label_map):
        mips_lines = []
        # return
        if instruction_text == 'return':
            return ['  jr $ra']

        # conditional branch
        if instruction_text.startswith('if '):
            match = re.match(
                r'if\s+(\w+)\s*(<=|>=|==|!=|<|>)\s*(\w+)\s*then\s*goto\s*(\d+)', instruction_text)
            if match:
                operand1, operator, operand2, target = match.groups()
                reg1 = self.get_register(operand1)
                reg2 = self.get_register(operand2)
                target_label = label_map[int(target)]
                branch_map = {'<=': 'ble', '>=': 'bge',
                              '==': 'beq', '!=': 'bne', '<': 'blt', '>': 'bgt'}
                mips_lines.append(
                    f"  {branch_map[operator]} {reg1}, {reg2}, {target_label}")
                return mips_lines

        # unconditional jump
        if instruction_text.startswith('goto '):
            match = re.match(r'goto\s*(\d+)', instruction_text)
            if match:
                target = int(match.group(1))
                mips_lines.append(f"  j {label_map[target]}")
            return mips_lines

        # assignment, arithmetic, arrays
        if '=' in instruction_text:
            # array load: dest = arr[index]
            load_match = re.match(
                r'(\w+)\s*=\s*(\w+)\[(\w+)\]', instruction_text)
            if load_match:
                dest, array, index_symbol = load_match.groups()
                mips_lines.append(
                    f"  add $at, {self.get_register(array)}, {self.get_register(index_symbol)}")
                mips_lines.append(f"  lw {self.get_register(dest)}, 0($at)")
                return mips_lines

            # array store: arr[index] = source
            store_match = re.match(
                r'(\w+)\[(\w+)\]\s*=\s*(\w+)', instruction_text)
            if store_match:
                array, index_symbol, source = store_match.groups()
                mips_lines.append(
                    f"  add $at, {self.get_register(array)}, {self.get_register(index_symbol)}")
                mips_lines.append(f"  sw {self.get_register(source)}, 0($at)")
                return mips_lines

            # simple copy or binary op
            left_side, right_side = [s.strip()
                                     for s in instruction_text.split('=', 1)]
            tokens = right_side.split()
            # copy: left = right
            if len(tokens) == 1:
                source = tokens[0]
                dest_reg = self.get_register(left_side)
                if source.isdigit():
                    mips_lines.append(f"  li {dest_reg}, {source}")
                else:
                    mips_lines.append(
                        f"  move {dest_reg}, {self.get_register(source)}")
                return mips_lines

            # binary operation: left = op1 operator op2
            if len(tokens) == 3:
                operand1, operator, operand2 = tokens
                dest_reg = self.get_register(left_side)
                reg1 = self.get_register(operand1)
                # immediate add/sub
                if operand2.isdigit() and operator in ['+', '-']:
                    immediate = operand2 if operator == '+' else f'-{operand2}'
                    mips_lines.append(f"  addi {dest_reg}, {reg1}, {immediate}")
                else:
                    if operand2.isdigit():
                        mips_lines.append(f"  li $at, {operand2}")
                        reg2 = '$at'
                    else:
                        reg2 = self.get_register(operand2)
                    if operator == '+':
                        mips_lines.append(f"  add {dest_reg}, {reg1}, {reg2}")
                    elif operator == '-':
                        mips_lines.append(f"  sub {dest_reg}, {reg1}, {reg2}")
                    elif operator == '*':
                        mips_lines.append(f"  mul {dest_reg}, {reg1}, {reg2}")
                    elif operator == '/':
                        mips_lines.append(f"  div {reg1}, {reg2}")
                        mips_lines.append(f"  mflo {dest_reg}")
                return mips_lines

        return mips_lines
