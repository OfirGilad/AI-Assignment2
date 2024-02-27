from state import State
from game_search_algorithms import GameAlgorithms
from game_node import GameNode


class Agent:
    def __init__(self, state: State):
        self.state = state
        self.agent_idx = state.agent_idx
        self.agent_action = {
            "Normal": self.normal_action
        }
        self.game_type_action = {
            "Adversarial (zero sum game)": self._adversarial_game_type_action,
            "A semi-cooperative game": self._semi_cooperative_game_type_action,
            "A fully cooperative game": self._fully_cooperative_game_type_action
        }

    # Game Support
    def _adversarial_game_type_action(self):
        """
        Adversarial (zero sum game): each agent aims to maximize its own individual score
        (number of packages delivered on time) minus the opposing agent's score.
        That is, TS1=IS1-IS2 and TS2=IS2-IS1.
        Here you should implement an "optimal" agent, using mini-max, with alpha-beta pruning.
        """
        game_validation = (
            len(self.state.agents) != 2 or
            self.state.agents[0]["type"] != "Normal" or
            self.state.agents[1]["type"] != "Normal"
        )
        if game_validation:
            raise ValueError("Adversarial (zero sum game) only supports two normal agents")

        # Update state
        self.state.update_agent_packages_status()
        game_node = GameNode(state=self.state)

        game_algorithms = GameAlgorithms(agent_idx=self.agent_idx)
        action = game_algorithms.alpha_beta_decision(game_node=game_node)

        # Handle action
        if action != "no-op":
            agent_location = self.state.agents[self.agent_idx]["location"]
            self.state.perform_agent_action(current_vertex=agent_location, action=action, mode="Coords")
            self.state.update_agent_packages_status()

        return action

    def _semi_cooperative_game_type_action(self):
        """
        A semi-cooperative game: each agent tries to maximize its own individual score.
        The agent disregards the other agent score, except that ties are broken cooperatively.
        That is, TS1=IS1, breaking ties in favor of greater IS2.
        """
        game_validation = (
            len(self.state.agents) != 2 or
            self.state.agents[0]["type"] != "Normal" or
            self.state.agents[1]["type"] != "Normal"
        )
        if game_validation:
            raise ValueError("A semi-cooperative game only supports two normal agents")

        # Update state
        self.state.update_agent_packages_status()
        game_node = GameNode(state=self.state)

        game_algorithms = GameAlgorithms(agent_idx=self.agent_idx)
        action = game_algorithms.semi_cooperative_decision(game_node=game_node)

        # Handle action
        if action != "no-op":
            agent_location = self.state.agents[self.agent_idx]["location"]
            self.state.perform_agent_action(current_vertex=agent_location, action=action, mode="Coords")
            self.state.update_agent_packages_status()

        return action

    def _fully_cooperative_game_type_action(self):
        """
        A fully cooperative game: both agents aim to maximize the sum of individual scores, so TS1=TS2=IS1+IS2.
        """
        game_validation = (
            len(self.state.agents) != 2 or
            self.state.agents[0]["type"] != "Normal" or
            self.state.agents[1]["type"] != "Normal"
        )
        if game_validation:
            raise ValueError("A fully cooperative game only supports two normal agents")

        # Update state
        self.state.update_agent_packages_status()
        game_node = GameNode(state=self.state)

        game_algorithms = GameAlgorithms(agent_idx=self.agent_idx)
        action = game_algorithms.fully_cooperative_decision(game_node=game_node)

        # Handle action
        if action != "no-op":
            agent_location = self.state.agents[self.agent_idx]["location"]
            self.state.perform_agent_action(current_vertex=agent_location, action=action, mode="Coords")
            self.state.update_agent_packages_status()

        return action

    def normal_action(self):
        action = self.game_type_action[self.state.game_type]()
        return self.state, action

    def perform_action(self):
        agent_type = self.state.agents[self.agent_idx]["type"]
        state, action = self.agent_action[agent_type]()
        return state, action


# def test_agents():
#     environment_data = {
#         "x": 2,
#         "y": 2,
#         "special_edges": [
#             # {"type": "always blocked", "from": [0, 0], "to": [0, 1]},
#             # {"type": "always blocked", "from": [1, 0], "to": [1, 1]},
#             # {"type": "always blocked", "from": [2, 1], "to": [2, 2]},
#             # {"type": "always blocked", "from": [1, 1], "to": [1, 2]},
#             # {"type": "always blocked", "from": [0, 0], "to": [1, 0]}
#         ],
#         "agents": [
#             {
#                 # "type": "Greedy",
#                 # "type": "A Star",
#                 # "type": "Real time A Star",
#                 "location": [2, 2],
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
#     # node = Node(state=state)
#     # print(node.search_adjacency_matrix)
#     # print(node.search_adjacency_matrix_mst)
#     # print(node.heuristic_value)
#     a = Agent(state)
#     state, action = a.perform_action()
#     print(state, action)
#
#
# if __name__ == "__main__":
#     test_agents()
