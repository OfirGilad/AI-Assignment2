import numpy as np

from state import State


class GameAlgorithms:
    def alpha_beta_decision(self, state: State):
        alpha = -np.inf
        beta = np.inf
        # return self.max_value(state=state, alpha=alpha, beta=beta)

        max_value = -np.inf
        max_action = "no-op"

        if state.is_goal_state():
            max_value = state.game_mode_score()
        else:
            possible_moves = [[1, 0], [-1, 0], [0, 1], [0, -1]]
            action_location = state.agents[state.agent_idx]["location"]

            for move in possible_moves:
                new_location = [action_location[0] + move[0], action_location[1] + move[1]]

                # Validate if the new location is a vertex on the graph
                try:
                    state.coordinates_to_vertex_index(coords=new_location)
                except:
                    continue

                if state.is_path_available(current_vertex=action_location, next_vertex=new_location, mode="Coords"):
                    # Create new node with time passed by 1
                    action_state = state.clone_state(agent_idx=state.agent_idx, time_factor=1)

                    action = action_state.perform_agent_step(
                        current_vertex=action_location,
                        next_vertex=new_location,
                        mode="Coords"
                    )
                    action_state.update_agent_packages_status()
                    action_state.agent_idx = (action_state.agent_idx + 1) % 2

                    _, min_value = self.min_value(state=action_state, alpha=alpha, beta=beta)
                    if max_value < min_value:
                        max_action = action
                        max_value = min_value

        return max_action, max_value

    def max_value(self, state: State, alpha, beta):
        max_value = -np.inf
        max_action = "no-op"

        if state.is_goal_state():
            max_value = state.game_mode_score()
        else:
            possible_moves = [[1, 0], [-1, 0], [0, 1], [0, -1]]
            action_location = state.agents[state.agent_idx]["location"]

            for move in possible_moves:
                new_location = [action_location[0] + move[0], action_location[1] + move[1]]

                # Validate if the new location is a vertex on the graph
                try:
                    state.coordinates_to_vertex_index(coords=new_location)
                except:
                    continue

                if state.is_path_available(current_vertex=action_location, next_vertex=new_location, mode="Coords"):
                    # Create new node with time passed by 1
                    action_state = state.clone_state(agent_idx=state.agent_idx, time_factor=1)

                    action = action_state.perform_agent_step(
                        current_vertex=action_location,
                        next_vertex=new_location,
                        mode="Coords"
                    )
                    action_state.update_agent_packages_status()
                    action_state.agent_idx = (action_state.agent_idx + 1) % 2

                    _, min_value = self.min_value(state=action_state, alpha=alpha, beta=beta)
                    if max_value < min_value:
                        max_action = action
                        max_value = min_value

                        # TODO: Check if this is correct
                        if max_value >= beta:
                            return max_action, max_value
                        alpha = max(alpha, max_value)

        return max_action, max_value

    def min_value(self, state: State, alpha, beta):
        min_value = np.inf
        min_action = "no-op"

        if state.is_goal_state():
            min_value = state.game_mode_score()
        else:
            possible_moves = [[1, 0], [-1, 0], [0, 1], [0, -1]]
            action_location = state.agents[state.agent_idx]["location"]

            for move in possible_moves:
                new_location = [action_location[0] + move[0], action_location[1] + move[1]]

                # Validate if the new location is a vertex on the graph
                try:
                    state.coordinates_to_vertex_index(coords=new_location)
                except:
                    continue

                if state.is_path_available(current_vertex=action_location, next_vertex=new_location, mode="Coords"):
                    # Create new node with time passed by 1
                    action_state = state.clone_state(agent_idx=state.agent_idx, time_factor=1)

                    action = action_state.perform_agent_step(
                        current_vertex=action_location,
                        next_vertex=new_location,
                        mode="Coords"
                    )
                    action_state.update_agent_packages_status()
                    action_state.agent_idx = (action_state.agent_idx + 1) % 2

                    _, max_value = self.max_value(state=action_state, alpha=alpha, beta=beta)
                    if min_value > max_value:
                        min_action = action
                        min_value = max_value

                        # TODO: Check if this is correct
                        if min_value <= alpha:
                            return min_action, min_value
                        beta = min(beta, min_value)

        return min_action, min_value
