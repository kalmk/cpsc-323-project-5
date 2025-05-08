import sys
from code_generator import CodeGenerator

def main():
    # Input and output paths
    input_path = sys.argv[1] if len(sys.argv) > 1 else 'testCase1.txt'
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'output.asm'

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