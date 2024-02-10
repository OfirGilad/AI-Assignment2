import numpy as np

from game_node import GameNode


class GameAlgorithms:
    def __init__(self, agent_idx: int):
        self.agent_idx = agent_idx

    def alpha_beta_decision(self, game_node: GameNode):
        alpha = -np.inf
        beta = np.inf
        # return self.max_value(state=state, alpha=alpha, beta=beta)

        max_value = -np.inf
        max_action = "no-op"

        if game_node.state.is_goal_state():
            max_value = game_node.state.game_mode_score(agent_idx=self.agent_idx)
        else:
            game_node.expand()
            for child in game_node.children:
                action = child.action

                _, min_value = self.min_value(game_node=child, alpha=alpha, beta=beta)
                if max_value < min_value:
                    max_action = action
                    max_value = min_value

        return max_action, max_value

    def max_value(self, game_node: GameNode, alpha, beta):
        max_value = -np.inf
        max_action = "no-op"

        if game_node.state.is_goal_state():
            max_value = game_node.state.game_mode_score(agent_idx=self.agent_idx)
        else:
            game_node.expand()
            for child in game_node.children:
                action = child.action

                _, min_value = self.min_value(game_node=child, alpha=alpha, beta=beta)
                if max_value < min_value:
                    max_action = action
                    max_value = min_value

                    # TODO: Check if this is correct
                    if max_value >= beta:
                        return max_action, max_value
                    alpha = max(alpha, max_value)

        return max_action, max_value

    def min_value(self, game_node: GameNode, alpha, beta):
        min_value = np.inf
        min_action = "no-op"

        if game_node.state.is_goal_state():
            min_value = game_node.state.game_mode_score(agent_idx=self.agent_idx)
        else:
            game_node.expand()
            for child in game_node.children:
                action = child.action

                _, max_value = self.max_value(game_node=game_node, alpha=alpha, beta=beta)
                if min_value > max_value:
                    min_action = action
                    min_value = max_value

                    # TODO: Check if this is correct
                    if min_value <= alpha:
                        return min_action, min_value
                    beta = min(beta, min_value)

        return min_action, min_value
