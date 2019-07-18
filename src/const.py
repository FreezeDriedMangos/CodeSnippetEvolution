import math 

# User-editable
BODY_LEN = 13 
NUM_MEMORY_BLOCKS_IN_SOUP = 1000
CHECKED_ADDRESS_STACK_SIZE = 20 # for the monitor command


# Non user editable
HEADER_LEN = 3
#MIN_ALLOWABLE_BODY_LEN = int(math.log(len(INSTRUCTIONS), base=2))
SIGNED_REGISTER_MAX = 2**(BODY_LEN-1)

MEM_BLOCK_LEN = HEADER_LEN + BODY_LEN
TOTAL_MEM_LEN = MEM_BLOCK_LEN * NUM_MEMORY_BLOCKS_IN_SOUP


# limits on the user constants
#BODY_LEN = max(BODY_LEN, MIN_ALLOWABLE_BODY_LEN)
SIGNED_REGISTER_MAX = 2**(BODY_LEN-1) # updating a non-user editable variable that's based on a user-editable one
NUM_MEMORY_BLOCKS_IN_SOUP = min(NUM_MEMORY_BLOCKS_IN_SOUP, SIGNED_REGISTER_MAX)
