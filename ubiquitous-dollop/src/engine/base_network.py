import numpy as np

from . import NetworkTypes

class PetriNetwork:
    def __init__(self):
        self._aminus = np.Array()
        self._aplus = np.Array()
        self._mark = np.Array()

    @property
    def aminus(self):
        return self._aminus.copy()

    @property
    def aplus(self):
        return self._aplus.copy()

    @property
    def a(self):
        a = self._aminus + self._aplus
        return a

    @property
    def m(self):
        return self._mark.copy()

    def set_aminus(self, aminus):
        pass

    def set_aplus(self, aplus):
        pass

    def set_a_keep_aminus(self, a):
        pass

    def set_a_keep_aplus(self, a):
        pass

    def get_enabled_transitions(self):
        pass

    def trigger_transition(self, t):
        pass










 