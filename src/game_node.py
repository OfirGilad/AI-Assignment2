from typing import List

from state import State


class GameNode:
    def __init__(self, state: State, parent=None, action="no-op"):
        # Init Variables
        self.state = state
        self.agent_idx = state.agent_idx
        self.parent = parent
        self.children: List[GameNode] = list()

        self.action = action
        self.depth = 0
        self.path_cost = 0
        self.heuristic_value = 0

        self._read_parent_data()

    def _calculate_action_cost(self):
        parent_location = self.parent.state.agents[self.agent_idx]["location"]
        node_location = self.state.agents[self.agent_idx]["location"]
        action_cost = self.parent.state.edge_cost(parent_location, node_location)
        return action_cost

    def _read_parent_data(self):
        if self.parent is not None:
            self.depth = self.parent.depth + 1

    def expand(self):
        possible_moves = [[1, 0], [-1, 0], [0, 1], [0, -1]]
        node_location = self.state.agents[self.agent_idx]["location"]
        for move in possible_moves:
            new_location = [node_location[0] + move[0], node_location[1] + move[1]]

            # Validate if the new location is a vertex on the graph
            try:
                self.state.coordinates_to_vertex_index(coords=new_location)
            except:
                continue

            if self.state.is_path_available(current_vertex=node_location, next_vertex=new_location, mode="Coords"):
                # Create new node with time passed by 1
                node_state = self.state.clone_state(agent_idx=self.agent_idx, time_factor=1)

                action = node_state.perform_agent_step(
                    current_vertex=node_location,
                    next_vertex=new_location,
                    mode="Coords"
                )
                node_state.update_agent_packages_status()
                node_state.agent_idx = (node_state.agent_idx + 1) % 2
                child = GameNode(
                    state=node_state,
                    parent=self,
                    action=action
                )

                self.children.append(child)
