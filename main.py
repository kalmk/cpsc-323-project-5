from code_generator import CodeGenerator

def main():
    input_path = "test_cases/testCase2.txt"
    output_path = "output.asm"
    # Read TAC instructions from external file 'testCase1.txt'
    with open(input_path) as f:
        tac = [line.strip() for line in f if line.strip()]

    cg = CodeGenerator()
    asm = cg.generate(tac)

    # Write the generated MIPS to 'output.asm'
    with open(output_path, 'w') as out:
        out.write(asm)

    print("MIPS assembly written to output.asm")

if __name__ == '__main__':
    main()
