from instructionFunctions import *

# '[instruction character]': ([function to call], '[argument decoding]'),
# capital letter argument decoding keys mean use two digits for this argument
INSTRUCTIONS = {'a': (add, 'rr0'),
                # b means backwards (make negative), f means forwards (make positive), _ means ignore this argument
                # 0 means use the same value as the first argument (1 means the second)
                # in add, a = source1, b = source2, c = destination
                'å': (add, 'r+0'),
                's': (subtract, 'rr0'),
                '̐s': (subtract, 'r+0'),
                #'m': (multiply, 'rr0'),
                #'̐m': (multiply, 'r+0'),
                #'q': (divide, 'rr0'),
                #'̐q': (divide, 'r+0'),
                'i': (ifeq, 'rr_'),
                '̐i': (ifeq, 'r+_'),
                #'r': (register, '___'), # I'm a register, my arguments are my contents
                #'r̃': (register, '___'), # I'm a register with a negative value, my arguments are my contents
                #'R': (register, '___'), # I'm a dump register
                #'R̃': (register, '___'), # I'm a dump register with a negative value
                '.': (noop, '___'),
                ',': (noop, '___'),
                ' ': (noop, '___'),
                '́f': (find, 'rr_'),
                'j': (jump, '+__'), # + means interpret the next three as one number 
                'j̀': (jump, '-__'), # +, but a negative number
                #'t': # find the next address after a matching template
                #'T': # find the first address before a matching template
                'w': (swap, 'ff_'), # swap the instructions from one adr to another
                '#': (addToDump, '+__'), # I'm a raw number! I add my argument to the dump register nearest the @ that executed me
                '@': (register, '+__') # I'm an instruction pointer! I execute code :)
               }

#a93_ means find the register 9 after self, and 3 before self, use the first as source, use the second as source, and use the first register again as destination (_ means don't care what's here)

# instructions are of the form [c000] and instruction functions take 3 arguments
# how those 3 digits are interpreted into 3 arguments is determined by a decoding key
