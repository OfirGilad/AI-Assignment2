from typing import List

from state import State


class GameNode:
    def __init__(self, state: State, parent=None, action="no-op", node_type="max"):
        # Game support
        # self.game_heuristic_types = {
        #     "Adversarial (zero sum game)": self._adversarial_heuristic,
        #     "A semi-cooperative game": self._semi_cooperative_heuristic,
        #     "A fully cooperative game": self._fully_cooperative_heuristic
        # }
        # self.game_type = state.game_type
        self.node_type = node_type

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
        # self._calculate_heuristic_value()

        # self.isInOpenList = False
        # self.indexInOpenList = -1

    def _calculate_action_cost(self):
        parent_location = self.parent.state.agents[self.agent_idx]["location"]
        node_location = self.state.agents[self.agent_idx]["location"]
        action_cost = self.parent.state.edge_cost(parent_location, node_location)
        return action_cost

    def _read_parent_data(self):
        if self.parent is not None:
            self.depth = self.parent.depth + 1

    # def _calculate_heuristic_value(self):
    #     # TODO: Implement the heuristic value calculation
    #     if self.state.is_goal_state():
    #         self.heuristic_value = 0
    #     else:
    #         self.game_heuristic_types[self.game_type]()

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
                    action=action,
                    node_type="min" if self.node_type == "max" else "max"
                )

                self.children.append(child)

    def h_value(self):
        return self.heuristic_value

    def g_value(self):
        return self.path_cost

    def f_value(self):
        return self.path_cost + self.heuristic_value

    def get_children(self):
        return self.children

    def get_action(self):
        return self.action

    def get_parent(self):
        return self.parent

    def __lt__(self, other):
        return self.f_value() < other.f_value()

    # def _adversarial_heuristic(self):
    #     """
    #     Adversarial (zero sum game): each agent aims to maximize its own individual score
    #     (number of packages delivered on time) minus the opposing agent's score.
    #     That is, TS1=IS1-IS2 and TS2=IS2-IS1.
    #     Here you should implement an "optimal" agent, using mini-max, with alpha-beta pruning.
    #     """
    #     if len(self.state.agents) != 2:
    #         raise ValueError("Adversarial (zero sum game) heuristic only supports two agents")
    #
    #     agent_data = self.state.agents[self.agent_idx]
    #     rival_agent_data = self.state.agents[(self.agent_idx + 1) % 2]
    #
    #     game_algorithms = GameAlgorithms(agent_idx=self.agent_idx)
    #     alpha_beta_decision_action, alpha_beta_decision_score = game_algorithms.alpha_beta_decision(state=self.state)
    #     print(f"My Prev Action: ({self.action}, {self.depth})")
    #     print(f"What should I do: ({alpha_beta_decision_action}, {alpha_beta_decision_score})")
    #
    #     self.heuristic_value = -1 * alpha_beta_decision_score
    #
    # def _semi_cooperative_heuristic(self):
    #     """
    #     A semi-cooperative game: each agent tries to maximize its own individual score.
    #     The agent disregards the other agent score, except that ties are broken cooperatively.
    #     That is, TS1=IS1, breaking ties in favor of greater IS2.
    #     """
    #     if len(self.state.agents) != 2:
    #         raise ValueError("Semi-cooperative heuristic only supports two agents")
    #
    #     agent_data = self.state.agents[self.agent_idx]
    #     rival_agent_data = self.state.agents[(self.agent_idx + 1) % 2]
    #
    #     # TODO: Find a way to break ties in favor of greater IS2
    #     game_algorithms = GameAlgorithms()
    #     agent_score = game_algorithms.alpha_beta_decision(state=self.state)
    #     print(f"My Prev Action: ({self.action}, {self.depth})")
    #     print(f"What should I do: {agent_score}")
    #
    # def _fully_cooperative_heuristic(self):
    #     """
    #     A fully cooperative game: both agents aim to maximize the sum of individual scores, so TS1=TS2=IS1+IS2.
    #     """
    #     if len(self.state.agents) != 2:
    #         raise ValueError("Fully-cooperative heuristic only supports two agents")
    #
    #     agent_data = self.state.agents[self.agent_idx]
    #     rival_agent_data = self.state.agents[(self.agent_idx + 1) % 2]
    #
    #     game_algorithms = GameAlgorithms()
    #     agent_score = game_algorithms.alpha_beta_decision(state=self.state)
    #     print(f"My Prev Action: ({self.action}, {self.depth})")
    #     print(f"What should I do: {agent_score}")


# def test_node_creation():
#     environment_data = {
#         "x": 2,
#         "y": 2,
#         "special_edges": [
#             {"type": "always blocked", "from": [0, 0], "to": [0, 1]},
#             {"type": "always blocked", "from": [1, 0], "to": [1, 1]},
#             # {"type": "always blocked", "from": [2, 1], "to": [2, 2]},
#             # {"type": "always blocked", "from": [1, 1], "to": [1, 2]},
#             # {"type": "always blocked", "from": [0, 0], "to": [1, 0]}
#         ],
#         "agents": [
#             {
#                 "type": "A Star",
#                 "location": [0, 0],
#                 "score": 0,
#                 "packages": list(),
#                 "number_of_actions": 0
#             }
#         ],
#         "placed_packages": [
#             {
#                 "package_at": [2, 1],
#                 "from_time": 0,
#                 "deliver_to": [2, 0],
#                 "before_time": 10,
#                 "package_id": 0,
#                 "status": "placed",
#                 "holder_agent_id": -1
#             },
#             {
#                 "package_at": [0, 2],
#                 "from_time": 0,
#                 "deliver_to": [1, 0],
#                 "before_time": 10,
#                 "package_id": 0,
#                 "status": "placed",
#                 "holder_agent_id": -1
#             }
#         ],
#         "agent_idx": 0
#     }
#     state = State(environment_data=environment_data)
#     # print(state.adjacency_matrix)
#     node = Node(state=state)
#     print(node.search_adjacency_matrix)
#     print(node.search_adjacency_matrix_mst)
#     print(node.heuristic_value)
#
#
# if __name__ == "__main__":
#     test_node_creation()
