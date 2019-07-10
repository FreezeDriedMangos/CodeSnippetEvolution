
def takeFromDump(amt, at):
    retval = min(amt, at.registers[10])
    at.registers[10] -= retval
    return retval


def emptyRegister(reg, at):
    at.registers[10] += at.registers[reg]
    at.registers[reg] = 0


def add(a, b, c, at, soup):
    # if a is a register index, empty that register into temp1, otherwise take a amount from the dump
    if type(a) == str and a[0] == 'r':
        temp1 = at.registers[int(a[1:])]
        emptyRegister(a, at)
    else:
        temp1 = takeFromDump(a, at)

    # if a is a register index, empty that register into temp1, otherwise take a amount from the dump
    if type(b) == str and b[0] == 'r':
        temp2 = at.registers[int(b[1:])]
        emptyRegister(b, at)
    else:
        temp2 = takeFromDump(b, at)

    # prepare register c to recieve the sum
    emptyRegister(c, at)
    at.registers[c] += temp1 + temp2

    # if a or b were register indecies, refill those registers
    if type(a) == str and a[0] == 'r':
        at.registers[a] += takeFromDump(temp1, at)

    if type(b) == str and b[0] == 'r':
        at.registers[b] += takeFromDump(temp2, at)

    return 1


def subtract(a, b, c, at, soup):
    # if a is a register index, empty that register into temp1, otherwise take a amount from the dump
    if type(a) == str and a[0] == 'r':
        temp1 = at.registers[int(a[1:])]
        emptyRegister(a, at)
    else:
        temp1 = takeFromDump(a, at)

    # if a is a register index, empty that register into temp1, otherwise take a amount from the dump
    if type(b) == str and b[0] == 'r':
        temp2 = at.registers[int(b[1:])]
        emptyRegister(b, at)
    else:
        temp2 = takeFromDump(b, at)

    # prepare register c to recieve the new total
    emptyRegister(c, at)
    at.registers[c] += temp1 - temp2

    # if a or b were register indecies, refill those registers
    if type(a) == str and a[0] == 'r':
        at.registers[a] += takeFromDump(temp1, at)

    if type(b) == str and b[0] == 'r':
        at.registers[b] += takeFromDump(temp2, at)

    return 1


# returns true if two instructions are the same one
def ifeq(a, b, c, at, soup):
    if type(a) == str and a[0] == 'r':
        a = at.registers[int(a[1:])]

    if type(b) == str and b[0] == 'r':
        b = at.registers[int(b[1:])]

    if soup[INSTRUCTION_LENGTH*a + at.index] == soup[INSTRUCTION_LENGTH*b + at.index]:
        return 2
    return 1
    

def register(a, b, c, at, soup):
    return noop(a, b, c, at, soup)
    
    
def noop(a, b, c, at, soup):
    return 1
    
    
def jump(a, b, c, at, soup):
    return a
