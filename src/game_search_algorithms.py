import numpy as np

from game_node import GameNode


class GameAlgorithms:
    def __init__(self, agent_idx: int):
        self.agent_idx = agent_idx
        self.rival_agent_idx = (self.agent_idx + 1) % 2
        self.semi_cooperative = False

    ###############
    # Adversarial #
    ###############
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

            if max_value >= beta:
                return max_value
            alpha = max(alpha, max_value)

        if len(game_node.children) == 0:
            node_state = game_node.state.clone_state(agent_idx=self.agent_idx, time_factor=1)
            node_state.update_agent_packages_status()

            node_state.agent_idx = (node_state.agent_idx + 1) % 2
            child = GameNode(
                state=node_state,
                parent=game_node,
                action="no-op"
            )

            min_value = self.min_value(game_node=child, alpha=alpha, beta=beta)
            max_value = max(max_value, min_value)

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

            if min_value <= alpha:
                return min_value
            beta = min(beta, min_value)

        if len(game_node.children) == 0:
            node_state = game_node.state.clone_state(agent_idx=self.agent_idx, time_factor=1)
            node_state.update_agent_packages_status()

            node_state.agent_idx = (node_state.agent_idx + 1) % 2
            child = GameNode(
                state=node_state,
                parent=game_node,
                action="no-op"
            )

            max_value = self.max_value(game_node=child, alpha=alpha, beta=beta)
            min_value = min(min_value, max_value)

        return min_value

    ####################
    # Semi Cooperative #
    ####################
    def semi_cooperative_decision(self, game_node: GameNode) -> str:
        max_dict = {
            self.agent_idx: -np.inf,
            self.rival_agent_idx: -np.inf
        }
        max_action = "no-op"
        game_node.expand()
        for child in game_node.children:
            action = child.action
            min_dict = self.min_value_semi_cooperative(game_node=child)
            if min_dict[self.agent_idx] > max_dict[self.agent_idx]:
                max_action = action
                max_dict = min_dict
            elif min_dict[self.agent_idx] == max_dict[self.agent_idx]:
                # Tie breaker
                max_action = action
                max_dict[self.rival_agent_idx] = min_dict[self.rival_agent_idx]
            else:
                continue

        return max_action

    def max_value_semi_cooperative(self, game_node: GameNode) -> dict:
        if game_node.state.is_goal_state():
            max_dict = game_node.state.game_mode_score(agent_idx=self.agent_idx)
            return max_dict

        max_dict = {
            self.agent_idx: -np.inf,
            self.rival_agent_idx: -np.inf
        }
        game_node.expand()
        for child in game_node.children:
            min_dict = self.min_value_semi_cooperative(game_node=child)
            if min_dict[self.agent_idx] > max_dict[self.agent_idx]:
                max_dict = min_dict
            elif min_dict[self.agent_idx] == max_dict[self.agent_idx]:
                # Tie breaker
                max_dict[self.rival_agent_idx] = max(max_dict[self.rival_agent_idx], min_dict[self.rival_agent_idx])

        if len(game_node.children) == 0:
            node_state = game_node.state.clone_state(agent_idx=self.agent_idx, time_factor=1)
            node_state.update_agent_packages_status()

            node_state.agent_idx = (node_state.agent_idx + 1) % 2
            child = GameNode(
                state=node_state,
                parent=game_node,
                action="no-op"
            )

            min_dict = self.min_value_semi_cooperative(game_node=child)
            if min_dict[self.agent_idx] > max_dict[self.agent_idx]:
                max_dict = min_dict
            elif min_dict[self.agent_idx] == max_dict[self.agent_idx]:
                # Tie breaker
                max_dict[self.rival_agent_idx] = max(max_dict[self.rival_agent_idx], min_dict[self.rival_agent_idx])

        return max_dict

    def min_value_semi_cooperative(self, game_node: GameNode) -> dict:
        if game_node.state.is_goal_state():
            min_dict = game_node.state.game_mode_score(agent_idx=self.agent_idx)
            return min_dict

        min_dict = {
            self.agent_idx: -np.inf,
            self.rival_agent_idx: -np.inf
        }
        game_node.expand()
        for child in game_node.children:
            max_dict = self.max_value_semi_cooperative(game_node=child)
            if min_dict[self.agent_idx] < max_dict[self.agent_idx]:
                min_dict = max_dict
            elif min_dict[self.agent_idx] == max_dict[self.agent_idx]:
                # Tie breaker
                min_dict[self.rival_agent_idx] = max(max_dict[self.rival_agent_idx], min_dict[self.rival_agent_idx])

        if len(game_node.children) == 0:
            node_state = game_node.state.clone_state(agent_idx=self.agent_idx, time_factor=1)
            node_state.update_agent_packages_status()

            node_state.agent_idx = (node_state.agent_idx + 1) % 2
            child = GameNode(
                state=node_state,
                parent=game_node,
                action="no-op"
            )

            max_dict = self.max_value_semi_cooperative(game_node=child)
            if min_dict[self.agent_idx] < max_dict[self.agent_idx]:
                min_dict = max_dict
            elif min_dict[self.agent_idx] == max_dict[self.agent_idx]:
                # Tie breaker
                min_dict[self.rival_agent_idx] = max(max_dict[self.rival_agent_idx], min_dict[self.rival_agent_idx])

        return min_dict

    #####################
    # Fully Cooperative #
    #####################
    def fully_cooperative_decision(self, game_node: GameNode) -> str:
        global_max_value = -np.inf
        global_max_action = "no-op"
        game_node.expand()
        for child in game_node.children:
            action = child.action

            max_value = self.maximax_value(game_node=child)
            if global_max_value < max_value:
                global_max_action = action
                global_max_value = max_value

        return global_max_action

    def maximax_value(self, game_node: GameNode) -> int:
        if game_node.state.is_goal_state():
            max_max_value = game_node.state.game_mode_score(agent_idx=game_node.state.agent_idx)
            return max_max_value

        max_max_value = -np.inf
        game_node.expand()
        for child in game_node.children:
            max_value = self.maximax_value(game_node=child)
            max_max_value = max(max_max_value, max_value)

        if len(game_node.children) == 0:
            node_state = game_node.state.clone_state(agent_idx=self.agent_idx, time_factor=1)
            node_state.update_agent_packages_status()

            node_state.agent_idx = (node_state.agent_idx + 1) % 2
            child = GameNode(
                state=node_state,
                parent=game_node,
                action="no-op"
            )

            max_value = self.maximax_value(game_node=child)
            max_max_value = max(max_max_value, max_value)

        return max_max_value
