from code_generator import CodeGenerator

def main():
    # Set test case path
    input_path = 'testCase1.txt'
    # Create output path for .asm file
    output_path = 'output.asm'

    # Read TAC lines
    with open(input_path) as f:
        tac = [ln.strip() for ln in f if ln.strip()]

    # Generate MIPS code
    cg = CodeGenerator()
    asm_code = cg.generate(tac)

    # Write to .asm file
    with open(output_path, 'w') as out:
        out.write(asm_code)

    print(f"MIPS assembly written to {output_path}")

if __name__ == '__main__':
    main()