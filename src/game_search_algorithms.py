import numpy as np

from game_node import GameNode


class GameAlgorithms:
    def __init__(self, agent_idx: int):
        self.agent_idx = agent_idx

    def alpha_beta_decision(self, game_node: GameNode) -> str:
        alpha = -np.inf
        beta = np.inf

        max_value = -np.inf
        max_action = "no-op"
        game_node.expand()
        for child in game_node.children:
            action = child.action

            min_value = self.min_value(game_node=child, alpha=alpha, beta=beta)
            if max_value < min_value:
                max_action = action
                max_value = min_value

        return max_action

    def max_value(self, game_node: GameNode, alpha, beta) -> int:
        if game_node.state.is_goal_state():
            max_value = game_node.state.game_mode_score(agent_idx=self.agent_idx)
            return max_value

        max_value = -np.inf
        game_node.expand()
        for child in game_node.children:
            min_value = self.min_value(game_node=child, alpha=alpha, beta=beta)
            max_value = max(max_value, min_value)

            # TODO: Check if this is correct
            if max_value >= beta:
                return max_value
            alpha = max(alpha, max_value)

        return max_value

    def min_value(self, game_node: GameNode, alpha, beta) -> int:
        if game_node.state.is_goal_state():
            min_value = game_node.state.game_mode_score(agent_idx=self.agent_idx)
            return min_value

        min_value = np.inf
        game_node.expand()
        for child in game_node.children:
            max_value = self.max_value(game_node=child, alpha=alpha, beta=beta)
            min_value = min(min_value, max_value)

            # TODO: Check if this is correct
            if min_value <= alpha:
                return min_value
            beta = min(beta, min_value)

        return min_value

    # TODO: check if needs to be different then fully
    def semi_cooperative_decision(self, game_node: GameNode) -> str:
        global_max_value = -np.inf
        global_max_action = "no-op"
        game_node.expand()
        for child in game_node.children:
            action = child.action

            max_value = self.max_max_value(game_node=child)
            if global_max_value < max_value:
                global_max_action = action
                global_max_value = max_value

        return global_max_action

    # TODO: check if needs to be different then semi
    def fully_cooperative_decision(self, game_node: GameNode) -> str:
        global_max_value = -np.inf
        global_max_action = "no-op"
        game_node.expand()
        for child in game_node.children:
            action = child.action

            max_value = self.max_max_value(game_node=child)
            if global_max_value < max_value:
                global_max_action = action
                global_max_value = max_value

        return global_max_action

    def max_max_value(self, game_node: GameNode) -> int:
        if game_node.state.is_goal_state():
            max_max_value = game_node.state.game_mode_score(agent_idx=game_node.state.agent_idx)
            return max_max_value

        max_max_value = -np.inf
        game_node.expand()
        for child in game_node.children:
            max_value = self.max_max_value(game_node=child)
            max_max_value = max(max_max_value, max_value)

        return max_max_value
