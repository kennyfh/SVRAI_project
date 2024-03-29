from collections import defaultdict
from qfunction import QFunction

"""
Clase que crea la Q-tabla
"""

class QTable(QFunction):
    def __init__(self, default=0.0) -> None:
        self.qtable = defaultdict(lambda: default)

    def update(self, state, action, delta) -> None:
        self.qtable[(state, action)] = self.qtable[(state, action)] + delta

    def get_q_value(self, state, action):
        return self.qtable[(state, action)]

    



