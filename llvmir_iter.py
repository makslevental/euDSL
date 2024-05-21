import llvmlite.binding as llvm


with open("mlir.bc", "rb") as ir:
    m = llvm.parse_bitcode(ir.read())

for f in m.functions:
    print(f'Function: {f.name}/`{f.type}`')
    print(f'Function attributes: {list(f.attributes)}')
    for a in f.arguments:
        print(f'Argument: {a.name}/`{a.type}`')
        print(f'Argument attributes: {list(a.attributes)}')
    for b in f.blocks:
        print(f'Block: {b.name}/`{b.type}`\n{b}\nEnd of Block')
        for i in b.instructions:
            print(f'Instruction: {i.name}/`{i.opcode}`/`{i.type}`: `{i}`')
            print(f'Attributes: {list(i.attributes)}')
            for o in i.operands:
                print(f'Operand: {o.name}/{o.type}')

    break

for g in m.global_variables:
    print(f'Global: {g.name}/`{g.type}`')
    print(f'Attributes: {list(g.attributes)}')
    print(g)
    break
