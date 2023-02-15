#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Module: GRIDWORLD
# Created By  : KENNY JESÚS FLORES HUAMÁN
# version ='1.0'
# ---------------------------------------------------------------------------
# EL PROBLEMA DEL MUNDO MALLA
#
# El ejemplo de mundo malla es una idealización del movimiento de un robot en un entorno.
# En cada momento, el robot se encuentra en una ubicación y puede desplazarse a las ubicaciones vecinas,
#  recogiendo recompensas y castigos. Supongamos que las acciones son estocásticas, de modo que existe una
#  distribución de probabilidad sobre los estados resultantes dada la acción y el estado.

# En la figura adjunta se muestra un mundo cuadriculado de 10×10, en el que el robot puede elegir
#  una de cuatro acciones: arriba, abajo, izquierda o derecha. Si el agente lleva a cabo una de estas acciones,
#  tiene una probabilidad de 0.7 de dar un paso en la dirección deseada y una probabilidad de 0.1 de dar un paso
#  en cualquiera de las otras tres direcciones. Si choca contra la pared exterior (es decir, la ubicación calculada
# está fuera de la malla), tiene una penalización de 1 (es decir, una recompensa de −1) y el agente no se mueve.
# Hay cuatro estados con recompensa (aparte de las paredes): +10 (en la posición (9,8)), +3 (en (8,3)), −5 (en (4,5))
#  y −10 (en (4,8)). En cada uno de estos estados, el agente obtiene la recompensa después de realizar una acción
# en ese estado, no cuando entra en él. Cuando el agente alcanza uno de los estados con recompensa positiva
# (ya sea +3 o +10), independientemente de la acción que realice, en el siguiente paso es lanzado, al azar, a
#  una de las cuatro esquinas del mundo cuadriculado.
# ---------------------------------------------------------------------------


from collections import defaultdict
from mdp import *
from policy_iteration import PolicyIteration
from tabular_policy import TabularPolicy
from qtable import QTable
from qlearning import QLearning
from multi_armed_bandit import EpsilonGreedy

class GridWorld(MDP):
    TERMINATE = 'terminate'
    TERMINAL = ('terminal', 'terminal')
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"

    """ Initialization"""

    def __init__(
        self,
        noise=0.3,
        width=10,
        height=10,
        discount_factor=0.9,
        blocked_states=[],
        action_cost=0.0,
        initial_state=(0, 0),
        goals=None,
    ) -> None:
        # Ruido:
        self.noise = noise
        # Dimensiones del grid
        self.width = width
        self.height = height
        # Factor de descuento y
        self.discount_factor = discount_factor
        # Estado inicial
        self.initial_state = initial_state
        # Recompensas
        if goals is None:
            # Si no existen recompensas dentro de la malla, pondremos 2 recompensas para testear la prueba
            self.goal_states = dict(
                [((width - 1, height - 1), 1), ((width - 1, height - 2), -1)]
            )
        else:
            self.goal_states = dict(goals)
        
        # Obstáculos: en nuestro problema no tenemos ningún obstáculo, pero podemos añadir algunos por experimentación
        self.blocked_states = blocked_states
        # Coste de accion
        self.action_cost = action_cost
        super().__init__()

    
    def get_states(self):
        """ Los estados son todas las casillas donde no se encuentran
        obstáculos"""
        states = [self.TERMINAL]
        states += [(x, y) for x in range(self.width)
                   for y in range(self.height) if (x,y) not in self.blocked_states]
        return states

    def get_actions(self, state=None):
        actions = [self.UP, self.DOWN,self.LEFT, self.RIGHT, self.TERMINATE]
        if state is None:
            return actions
        valid_actions = []
        for a in actions:
            for (new_state, prob) in self.get_transitions(state,a):
                if prob > 0:
                    valid_actions.append(a)
                    break
        return valid_actions


    """ Return all non-zero probability transitions for this action
        from this state, as a list of (state, probability) pairs
    """
    def valid_add(self, state, new_state, probability):
        # If the next state is blocked, stay in the same state
        if probability == 0.0:
            return ()

        if new_state in self.blocked_states:
            return (state, probability)

        # Move to the next space if it is not off the grid
        (x, y) = new_state
        if x >= 0 and x < self.width and y >= 0 and y < self.height:
            return ((x, y), probability)

        # If off the grid, state in the same state
        return (state, probability)

    def get_transitions(self, state, action):
        transitions = []

        if state == self.TERMINAL:
            if action == self.TERMINATE:
                return [(self.TERMINAL, 1.0)]
            else:
                return []

        # Probability of not slipping left or right
        straight = 1 - (2 * self.noise)

        (x, y) = state
        movements = {
            "UP": [(x, y+1), (x-1, y), (x+1, y)],
            "DOWN": [(x, y-1), (x-1,y), (x+1, y)],
            "LEFT": [(x-1,y), (x, y-1), (x, y+1)],
            "RIGHT": [(x+1, y), (x, y-1), (x, y+1)]
            }
        if state in self.get_goal_states().keys():
            if action == self.TERMINATE:
                transitions += [(self.TERMINAL, 1.0)]
        elif action==self.UP or action ==self.DOWN or action==self.LEFT or action==self.RIGHT:
            mov =  movements[action]
            transitions += [self.valid_add(state, mov[0], straight),
                            self.valid_add(state, mov[1], self.noise),
                            self.valid_add(state, mov[2], self.noise)]

        # # Fusionar algún duplicado
        # merged = defaultdict(lambda: 0.0)
        # for (state, probability) in transitions:
        #     merged[state] = merged[state] + probability

        # transitions = []
        # for outcome in merged.keys():
        #     transitions += [(outcome, merged[outcome])]

        return transitions


    def get_reward(self, state, action, next_state):
        """
        Devuelve una recompensa si el siguiente estado es un terminal y
        y este estado es una que tiene recompensa. Si no, devuelve el coste de acción que hayamos realizado
        """
        reward = 0.
        if state in self.get_goal_states().keys() and next_state == self.TERMINAL:
            reward = self.get_goal_states().get(state)
        else:
            reward = self.action_cost
        return reward

    def is_terminal(self, state) -> bool:
        return True if state==self.TERMINAL else False

    def get_discount_factor(self):
        return self.discount_factor

    def get_initial_state(self):
        return self.initial_state

    def get_goal_states(self):
        return self.goal_states

    def policy_to_string(self, policy:TabularPolicy) -> str:        
        result= "\n "
        mov = {self.UP: "↑", self.DOWN: "↓",
                    self.LEFT: "←", self.RIGHT: "→", self.TERMINATE: " "}
        # policy_dict = policy.policy_table
        for y in range(self.height - 1, -1, -1):
            for x in range(self.width):
                # Si el elemento es un obstáculo
                if (x,y) in self.blocked_states:
                    result += " | ##"
                # Si el elemento es una recompensa
                elif policy.select_action((x, y)) == self.TERMINATE:
                    result += f" | {self.goal_states[(x, y)]} "
                # Si es otro sitio
                else:
                    result += " |  " + mov[policy.select_action((x, y))] + " "
            result += "\n"
        return result

    def execute(self, state, action):
        # If we are in a goal state then terminate automatically execute
        # a terminate action to immediately terminate
        if state in self.goal_states:
            return MDP.execute(self, state=state, action=self.TERMINATE)
        return super().execute(state, action)

if __name__ == "__main__":
    # gridworld = GridWorld(goals=[((9, 8), +10), ((8, 3), +3),
    #                ((4, 5), -5), ((4, 8), -10)])
    # policy = TabularPolicy(default_action=gridworld.UP)
    # PolicyIteration(gridworld, policy).policy_iteration(max_iterations=100)
    # print(gridworld.policy_to_string(policy))
    # gridworld = GridWorld(width=4,height=3,noise=0.1,blocked_states=[(1, 1)])
    # policy = TabularPolicy(default_action=gridworld.LEFT)
    # print(policy.policy_table)
    # PolicyIteration(gridworld, policy).policy_iteration(max_iterations=100)
    # print(gridworld.policy_to_string(policy))

    gridworld = GridWorld(width=4,height=3,noise=0.1,blocked_states=[(1, 1)])
    qfunction = QTable()
    QLearning(gridworld, EpsilonGreedy(), qfunction).execute(episodes=100)
    policy = qfunction.extract_policy(gridworld)
    print(gridworld.policy_to_string(policy))    

