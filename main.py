from code_generator import CodeGenerator


def main():
    input_path = "test_cases/3.in"

    if input_path == "test_cases/1.in":
        output_path = "output_1.asm"
    elif input_path == "test_cases/2.in":
        output_path = "output_2.asm"
    elif input_path == "test_cases/3.in":
        output_path = "output_3.asm"
    else:
        output_path = "output.asm"

    # Read TAC instructions from external file
    with open(input_path) as f:
        tac = [line.strip() for line in f if line.strip()]

    cg = CodeGenerator()
    asm = cg.generate(tac)

    # Write the generated MIPS to output
    with open(output_path, 'w') as out:
        out.write(asm)

    print("MIPS assembly written. Check the files.")


if __name__ == '__main__':
    main()
