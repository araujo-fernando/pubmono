from enum import Enum, auto

class NetworkTypes(Enum):
    NON_TIMED = auto()
    P_TIMED = auto()
    T_TIMED = auto()
    PT_TIMED = auto()

    