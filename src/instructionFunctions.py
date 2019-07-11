_ = 0

def takeFromDump(amt, at):
    retval = min(amt, at.registers[10])
    at.registers[10] -= retval
    return retval


def emptyRegister(a, b=0, c=0, at=None, soup=[], myIndex=0):
    if type(a) == str and a[0] == 'r':
        a = int(a[1:])
    at.registers[10] += at.registers[a]
    at.registers[a] = 0


def add(a, b, c, at, soup, myIndex):
    # if a is a register index, empty that register into temp1, otherwise take a amount from the dump
    if type(a) == str and a[0] == 'r':
        temp1 = at.registers[int(a[1:])]
        emptyRegister(a, _, _, at, _, _)
    else:
        temp1 = takeFromDump(a, at)

    # if a is a register index, empty that register into temp1, otherwise take a amount from the dump
    if type(b) == str and b[0] == 'r':
        temp2 = at.registers[int(b[1:])]
        emptyRegister(b, _, _, at, _, _)
    else:
        temp2 = takeFromDump(b, at)
        
    # argument c should always specify a register
    if type(c) == str and c[0] == 'r':
        c = at.registers[int(c[1:])]

    # prepare register c to recieve the sum
    emptyRegister(c, _, _, at, _, _)
    at.registers[c] += temp1 + temp2

    # if a or b were register indecies, refill those registers
    if type(a) == str and a[0] == 'r':
        at.registers[int(a[1:])] += takeFromDump(temp1, at)

    if type(b) == str and b[0] == 'r':
        at.registers[int(b[1:])] += takeFromDump(temp2, at)

    return 1


def subtract(a, b, c, at, soup, myIndex):
    # if a is a register index, empty that register into temp1, otherwise take a amount from the dump
    if type(a) == str and a[0] == 'r':
        temp1 = at.registers[int(a[1:])]
        emptyRegister(a, _, _, at, _, _)
    else:
        temp1 = takeFromDump(a, at)

    # if a is a register index, empty that register into temp1, otherwise take a amount from the dump
    if type(b) == str and b[0] == 'r':
        temp2 = at.registers[int(b[1:])]
        emptyRegister(b, _, _, at, _, _)
    else:
        temp2 = takeFromDump(b, at)

    # prepare register c to recieve the new total
    emptyRegister(c, _, _, at, _, _)
    at.registers[c] += temp1 - temp2

    # if a or b were register indecies, refill those registers
    if type(a) == str and a[0] == 'r':
        at.registers[a] += takeFromDump(temp1, at)

    if type(b) == str and b[0] == 'r':
        at.registers[b] += takeFromDump(temp2, at)

    return 1


# returns true if two instructions are the same one
def ifinstr(a, b, c, at, soup, myIndex):
    if type(a) == str and a[0] == 'r':
        a = at.registers[int(a[1:])]

    if type(b) == str and b[0] == 'r':
        b = at.registers[int(b[1:])]

    if soup[INSTRUCTION_LENGTH*a + at.index] == soup[INSTRUCTION_LENGTH*b + at.index]:
        return 1
    return 2
    
    
def ifzero(a, b, c, at, soup, myIndex):
    if type(a) == str and a[0] == 'r':
        a = at.registers[int(a[1:])]

    if soup[INSTRUCTION_LENGTH*a + at.index] == 0:
        return 1
    return 2
    
    
def find(a, b, c, at, soup, myIndex):
    if type(a) == str and a[0] == 'r':
        a = at.registers[int(a[1:])]

    if type(b) == str and b[0] == 'r':
        b = at.registers[int(b[1:])]
        
    instrIdx  = at.index + at.registers[a];
    instrType = soup[instrIdx]
    instrId   = soup[instrIdx + INSTRUCTION_LENGTH-1]
    
    for i in range(0, len(soup), INSTRUCTION_LENGTH):
        if soup[i] == instrType and soup[i + INSTRUCTION_LENGTH-1] != instrId:
            at.registers[b] = takeFromDump(i, at)
            at.foundStacks[instrType].push(i)
    
    return 1
    
    
def swap(a, b, c, at, soup, myIndex):
    if type(a) == str and a[0] == 'r':
        a = at.registers[int(a[1:])]

    if type(b) == str and b[0] == 'r':
        b = at.registers[int(b[1:])]
        
    temp = soup[a:a+INSTRUCTION_LENGTH]
    soup[a:a+INSTRUCTION_LENGTH] = soup[b:b+INSTRUCTION_LENGTH]
    soup[b:b+INSTRUCTION_LENGTH] = temp
    return 1
    
    
def setArgs(a, b, c, at, soup, myIndex):
    if type(a) == str and a[0] == 'r':
        a = at.registers[int(a[1:])]

    if type(b) == str and b[0] == 'r':
        b = at.registers[int(b[1:])]
        
    src = at.index+a+1
    dst = at.index+b+1
    
    soup[dst:dst+INSTRUCTION_LENGTH] = soup[src:src+INSTRUCTION_LENGTH]
        

def register(a, b, c, at, soup, myIndex):
    return noop(a, b, c, at, soup, myIndex)
    
    
def noop(a, b, c, at, soup, myIndex):
    return 1
    
    
def jump(a, b, c, at, soup, myIndex):
    return a
    

def addToDump(a, b, c, at, soup, myIndex):
    at.registers[10] += a
    soup[myIndex+1:myIndex+INSTRUCTION_LENGTH] = '0'*INSTRUCTION_LENGTH
    return 1
