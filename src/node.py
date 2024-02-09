import numpy as np
# from scipy.sparse import csr_matrix
# from scipy.sparse.csgraph import minimum_spanning_tree

from state import State
from search_algorithms import SearchAlgorithms


class Node:
    def __init__(self, state: State, parent=None, action="no-op", node_type="max"):
        # Supported game types
        self.game_heuristic_types = {
            "Adversarial (zero sum game)": self._adversarial_heuristic,
            "A semi-cooperative game": self._semi_cooperative_heuristic,
            "A fully cooperative game": self._fully_cooperative_heuristic
        }

        # Init Variables
        self.state = state
        self.agent_idx = state.agent_idx
        self.parent = parent
        self.children = list()

        # Game support
        self.game_type = state.game_type
        self.node_type = node_type

        self.action = action
        self.depth = 0
        self.path_cost = 0
        self.heuristic_value = 0
        self.search_adjacency_matrix = None
        self.search_adjacency_matrix_mst = None

        self._calculate_heuristic_value()
        self.total_cost = self.heuristic_value
        self._read_parent_data()

        self.isInOpenList = False
        self.indexInOpenList = -1
        
    def _calculate_action_cost(self):
        parent_location = self.parent.state.agents[self.agent_idx]["location"]
        node_location = self.state.agents[self.agent_idx]["location"]
        action_cost = self.parent.state.edge_cost(parent_location, node_location)
        return action_cost

    def _read_parent_data(self):
        if self.parent is not None:
            self.depth += self.parent.depth
            self.path_cost += self.parent.path_cost + self._calculate_action_cost()
            self.total_cost = self.path_cost + self.heuristic_value

    def _build_search_adjacency_matrix(self, points_of_interest: list):
        total_vertices = self.state.total_vertices
        self.search_adjacency_matrix = np.zeros(shape=(total_vertices, total_vertices), dtype=int)

        # Create a state with the current agent placed in it
        state_without_agent = self.state.clone_state(agent_idx=self.agent_idx)
        state_without_agent.agents[self.agent_idx]["location"] = None
        search_algorithms = SearchAlgorithms(state=state_without_agent)

        # Build the clique from all the points of interest
        for point_1_index in points_of_interest:
            for point_2_index in points_of_interest:
                if point_1_index != point_2_index:
                    step = search_algorithms.dijkstra_step(src=point_1_index, dest=point_2_index, mode="Indices")
                    if step is not None:
                        solution_cost, _, _ = step
                        self.search_adjacency_matrix[point_1_index, point_2_index] = solution_cost

    def _calculate_heuristic_value(self):
        # TODO: Implement the heuristic value calculation
        self.game_heuristic_types[self.game_type]()

        # TODO: To be removed
        agent_data = self.state.agents[self.agent_idx]
        interesting_packages = self.state.packages + self.state.placed_packages + agent_data["packages"]

        # Search for all points of interest
        points_of_interest = set()
        points_of_interest.add(self.state.coordinates_to_vertex_index(coords=agent_data["location"]))
        for package in interesting_packages:
            if package["status"] == "waiting" or package["status"] == "placed":
                points_of_interest.add(self.state.coordinates_to_vertex_index(coords=package["package_at"]))
                points_of_interest.add(self.state.coordinates_to_vertex_index(coords=package["deliver_to"]))
            elif package["status"] == "picked":
                points_of_interest.add(self.state.coordinates_to_vertex_index(coords=package["deliver_to"]))
       
        # Build the adjacency matrix of the points of interest only
        self._build_search_adjacency_matrix(points_of_interest=list(points_of_interest))

        # Finding the minimum spanning tree (using scipy)
        # adj_csr_matrix = csr_matrix(self.search_adjacency_matrix)
        # mst = minimum_spanning_tree(csgraph=adj_csr_matrix)
        # self.search_adjacency_matrix_mst = mst.toarray().astype(int)

        # Finding the minimum spanning tree (using our own implementation)
        self.search_adjacency_matrix_mst = SearchAlgorithms.kruskal(self.search_adjacency_matrix)

        # Calculate the heuristic value as the sum of the minimum spanning tree edges
        self.heuristic_value = int(np.sum(self.search_adjacency_matrix_mst) / 2)

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
                child = Node(
                    state=node_state,
                    parent=self,
                    action=action,
                    node_type="min"
                )

                self.children.append(child)
           
    def h_value(self):
        return self.heuristic_value

    def g_value(self):
        return self.path_cost

    def f_value(self):
        return self.total_cost

    def get_children(self):
        return self.children
    
    def get_action(self):
        return self.action
    
    def get_parent(self):
        return self.parent
    
    def __lt__(self, other):
        return self.f_value() < other.f_value()

    # def __eq__(self, other):
    #     return  (self.state.adjacency_matrix == other.state.adjacency_matrix
    #     and self.state.placed_packages == other.state.placed_packages 
    #     and self.state.picked_packages == other.state.picked_packages 
    #     and self.state.archived_packages == other.state.archived_packages)

    # def __hash__(self):
    #     return hash(str(self.state.adjacency_matrix)+ str(self.state.placed_packages)
    #                 + str(self.state.picked_packages) +str(self.state.archived_packages)
    #                 + str(self.state.special_edges)+ str(self.state.time))

    def _adversarial_heuristic(self):
        """
        Adversarial (zero sum game): each agent aims to maximize its own individual score
        (number of packages delivered on time) minus the opposing agent's score.
        That is, TS1=IS1-IS2 and TS2=IS2-IS1.
        Here you should implement an "optimal" agent, using mini-max, with alpha-beta pruning.
        """
        agent_data = self.state.agents[self.agent_idx]
        rival_agent_data = self.state.agents[(self.agent_idx + 1) % 2]

    def _semi_cooperative_heuristic(self):
        """
        A semi-cooperative game: each agent tries to maximize its own individual score.
        The agent disregards the other agent score, except that ties are broken cooperatively.
        That is, TS1=IS1, breaking ties in favor of greater IS2.
        """
        agent_data = self.state.agents[self.agent_idx]
        rival_agent_data = self.state.agents[(self.agent_idx + 1) % 2]

    def _fully_cooperative_heuristic(self):
        """
        A fully cooperative game: both agents aim to maximize the sum of individual scores, so TS1=TS2=IS1+IS2.
        """
        agent_data = self.state.agents[self.agent_idx]
        rival_agent_data = self.state.agents[(self.agent_idx + 1) % 2]


def test_node_creation():
    environment_data = {
        "x": 2,
        "y": 2,
        "special_edges": [
            {"type": "always blocked", "from": [0, 0], "to": [0, 1]},
            {"type": "always blocked", "from": [1, 0], "to": [1, 1]},
            # {"type": "always blocked", "from": [2, 1], "to": [2, 2]},
            # {"type": "always blocked", "from": [1, 1], "to": [1, 2]},
            # {"type": "always blocked", "from": [0, 0], "to": [1, 0]}
        ],
        "agents": [
            {
                "type": "A Star",
                "location": [0, 0],
                "score": 0,
                "packages": list(),
                "number_of_actions": 0
            }
        ],
        "placed_packages": [
            {
                "package_at": [2, 1],
                "from_time": 0,
                "deliver_to": [2, 0],
                "before_time": 10,
                "package_id": 0,
                "status": "placed",
                "holder_agent_id": -1
            },
            {
                "package_at": [0, 2],
                "from_time": 0,
                "deliver_to": [1, 0],
                "before_time": 10,
                "package_id": 0,
                "status": "placed",
                "holder_agent_id": -1
            }
        ],
        "agent_idx": 0
    }
    state = State(environment_data=environment_data)
    # print(state.adjacency_matrix)
    node = Node(state=state)
    print(node.search_adjacency_matrix)
    print(node.search_adjacency_matrix_mst)
    print(node.heuristic_value)


if __name__ == "__main__":
    test_node_creation()
