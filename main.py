from code_generator import CodeGenerator

def main():
    # Read TAC instructions from external file 'tac_input.txt'
    with open('testCase1.txt') as f:
        tac = [line.strip() for line in f if line.strip()]

    cg = CodeGenerator()
    asm = cg.generate(tac)

    # Write the generated MIPS to 'output.asm'
    with open('output.asm', 'w') as out:
        out.write(asm)

    print("MIPS assembly written to output.asm")

if __name__ == '__main__':
    main()
