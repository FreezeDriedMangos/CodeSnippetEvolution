
# User-editable
BODY_LEN = 13 
NUM_MEMORY_BLOCKS_IN_SOUP = 1000


# Non user editable
HEADER_LEN = 3
MIN_ALLOWABLE_BODY_LEN = int(log_2(len(INSTRUCTIONS)))
SIGNED_REGISTER_MAX = 2**(BODY_LEN-1)


# limits on the user constants
BODY_LEN = max(BODY_LEN, MIN_ALLOWABLE_BODY_LEN)
SIGNED_REGISTER_MAX = 2**(BODY_LEN-1) # updating a non-user editable variable that's based on a user-editable one
NUM_MEMORY_BLOCKS_IN_SOUP = min(NUM_MEMORY_BLOCKS_IN_SOUP, SIGNED_REGISTER_MAX)
