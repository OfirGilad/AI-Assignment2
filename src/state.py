import numpy as np
from copy import deepcopy


class State:
    def __init__(self, environment_data: dict):
        # Game support
        self.game_score_types = {
            "Normal": self._normal_score,
            "Adversarial (zero sum game)": self._adversarial_score,
            "A semi-cooperative game": self._semi_cooperative_score,
            "A fully cooperative game": self._fully_cooperative_score
        }
        self.game_type_to_idx = {
            "Normal": 0,
            "Adversarial (zero sum game)": 1,
            "A semi-cooperative game": 2,
            "A fully cooperative game": 3
        }
        self.game_type = environment_data.get("game_type", "Normal")

        # Parse state initial parameters
        self.X = environment_data["x"] + 1
        self.Y = environment_data["y"] + 1
        self.packages = environment_data.get("packages", list())
        self.special_edges = environment_data.get("special_edges", list())
        self.agents = environment_data.get("agents", list())

        # Build state graph
        self.total_vertices = self.X * self.Y
        self.adjacency_matrix = None
        self._build_adjacency_matrix()

        # Parse state additional parameters
        self.agent_idx = environment_data.get("agent_idx", 0)
        self.time = environment_data.get("time", 0.0)
        self.placed_packages = environment_data.get("placed_packages", list())
        self.picked_packages = environment_data.get("picked_packages", list())
        self.archived_packages = environment_data.get("archived_packages", list())
        self.update_packages_info()

    def coordinates_to_vertex_index(self, coords: list) -> int:
        row, col = coords
        if row < 0 or row >= self.X or col < 0 or col >= self.Y:
            raise ValueError("Coordinates out of bounds")

        return row * self.Y + col

    def vertex_index_to_coordinates(self, idx: int) -> list:
        if idx < 0 or idx > self.total_vertices:
            raise ValueError("Vertex index out of bounds")

        row = idx // self.Y
        col = idx % self.Y
        coords = [row, col]
        return coords

    def _apply_special_edges(self):
        for special_edge in self.special_edges:
            if special_edge["type"] == "always blocked":
                first_node = self.coordinates_to_vertex_index(coords=special_edge["from"])
                second_node = self.coordinates_to_vertex_index(coords=special_edge["to"])

                self.adjacency_matrix[first_node, second_node] = 0
                self.adjacency_matrix[second_node, first_node] = 0

    def _build_adjacency_matrix(self):
        self.adjacency_matrix = np.zeros(shape=(self.total_vertices, self.total_vertices), dtype=int)

        for i in range(self.X):
            for j in range(self.Y):
                current_node = self.coordinates_to_vertex_index(coords=[i, j])

                # Connect with the right neighbor (if exists)
                if j + 1 < self.Y:
                    right_neighbor = self.coordinates_to_vertex_index(coords=[i, j + 1])
                    self.adjacency_matrix[current_node, right_neighbor] = 1
                    self.adjacency_matrix[right_neighbor, current_node] = 1

                # Connect with the bottom neighbor (if exists)
                if i + 1 < self.X:
                    bottom_neighbor = self.coordinates_to_vertex_index(coords=[i + 1, j])
                    self.adjacency_matrix[current_node, bottom_neighbor] = 1
                    self.adjacency_matrix[bottom_neighbor, current_node] = 1

        self._apply_special_edges()

    def update_packages_info(self):
        current_packages = deepcopy(self.packages)
        for package in current_packages:
            if package["from_time"] <= self.time:
                self.packages.remove(package)

                package["status"] = "placed"

                self.placed_packages.append(package)

        current_placed_packages = deepcopy(self.placed_packages)
        for package in current_placed_packages:
            if package["before_time"] <= self.time:
                self.placed_packages.remove(package)

                package["status"] = "disappeared"

                self.archived_packages.append(package)

        current_picked_packages = deepcopy(self.picked_packages)
        for package in current_picked_packages:
            if package["before_time"] <= self.time:
                self.picked_packages.remove(package)

                package["status"] = "disappeared"
                package["holder_agent_id"] = -1

                self.archived_packages.append(package)

                for agent_idx, agent in enumerate(self.agents):
                    for agent_package in agent.get("packages", list()):
                        if package["package_id"] == agent_package["package_id"]:
                            self.agents[agent_idx]["packages"].remove(agent_package)

    def update_agent_packages_status(self):
        agent_data = self.agents[self.agent_idx]
        current_placed_packages = deepcopy(self.placed_packages)
        for package in current_placed_packages:
            if package["package_at"] == agent_data["location"]:
                self.placed_packages.remove(package)

                package["status"] = "picked"
                package["holder_agent_id"] = self.agent_idx

                agent_data["packages"].append(package)
                self.picked_packages.append(package)

        current_pickup_packages = deepcopy(self.picked_packages)
        for package in current_pickup_packages:
            # Skip packages not picked by this agent
            if package["holder_agent_id"] != self.agent_idx:
                continue

            if package["deliver_to"] == agent_data["location"]:
                agent_data["packages"].remove(package)
                self.picked_packages.remove(package)

                package["status"] = "delivered"
                agent_data["score"] += 1

                self.archived_packages.append(package)

        self.agents[self.agent_idx] = agent_data

    def convert_to_node_indices(self, current_vertex, next_vertex, mode: str):
        # The input vertices are list of coordinates
        if mode == "Coords":
            current_vertex_index = self.coordinates_to_vertex_index(coords=current_vertex)
            next_vertex_index = self.coordinates_to_vertex_index(coords=next_vertex)

        # The input vertices are indices of the vertices on the graph
        elif mode == "Indices":
            current_vertex_index = current_vertex
            next_vertex_index = next_vertex
        # Encountered invalid mode
        else:
            raise ValueError(f"Invalid mode: {mode}. Current available modes are: Coords, Indices")

        return current_vertex_index, next_vertex_index

    def convert_to_node_coords(self, current_vertex, next_vertex, mode: str):
        # The input vertices are list of coordinates
        if mode == "Coords":
            current_vertex_coords = current_vertex
            next_vertex_coords = next_vertex
        # The input vertices are indices of the vertices on the graph
        elif mode == "Indices":
            current_vertex_coords = self.vertex_index_to_coordinates(idx=current_vertex)
            next_vertex_coords = self.vertex_index_to_coordinates(idx=next_vertex)
        # Encountered invalid mode
        else:
            raise ValueError(f"Invalid mode: {mode}")

        return current_vertex_coords, next_vertex_coords

    def is_path_available(self, current_vertex, next_vertex, mode):
        current_vertex_index, next_vertex_index = self.convert_to_node_indices(
            current_vertex=current_vertex,
            next_vertex=next_vertex,
            mode=mode
        )

        # Check if next vertex is occupied
        for agent in self.agents:
            agent_location = agent.get("location", None)
            if agent_location is not None:
                agent_vertex_index = self.coordinates_to_vertex_index(coords=agent_location)
                if agent_vertex_index == next_vertex_index:
                    return False

        # Check if the edge is missing
        edge_missing_validation = (
            self.adjacency_matrix[current_vertex_index, next_vertex_index] == 0 or
            self.adjacency_matrix[current_vertex_index, next_vertex_index] == 0
        )
        if edge_missing_validation:
            return False

        # All validation passed
        return True

    def edge_cost(self, current_vertex, next_vertex, mode="Coords"):
        current_vertex_index, next_vertex_index = self.convert_to_node_indices(
            current_vertex=current_vertex,
            next_vertex=next_vertex,
            mode=mode
        )

        return self.adjacency_matrix[current_vertex_index, next_vertex_index]

    def perform_agent_step(self, current_vertex, next_vertex, mode):
        current_vertex, next_vertex = self.convert_to_node_coords(
            current_vertex=current_vertex,
            next_vertex=next_vertex,
            mode=mode
        )
        if self.is_path_available(current_vertex=current_vertex, next_vertex=next_vertex, mode="Coords"):
            # Break fragile edges
            for edge_idx, edge in enumerate(self.special_edges):
                fragile_edge_step_validation = (
                    edge["type"] == "fragile" and (
                        (edge["from"] == current_vertex and edge["to"] == next_vertex) or
                        (edge["from"] == next_vertex and edge["to"] == current_vertex)
                    )
                )
                if fragile_edge_step_validation:
                    self.special_edges[edge_idx]["type"] = "always blocked"
                    self._build_adjacency_matrix()

            # Update agent data
            agent_data = self.agents[self.agent_idx]
            agent_data["location"] = next_vertex
            agent_data["number_of_actions"] += 1
            self.agents[self.agent_idx] = agent_data

            # Return Action Name
            if current_vertex[0] > next_vertex[0] and current_vertex[1] == next_vertex[1]:
                return "Up"
            elif current_vertex[0] < next_vertex[0] and current_vertex[1] == next_vertex[1]:
                return "Down"
            elif current_vertex[0] == next_vertex[0] and current_vertex[1] > next_vertex[1]:
                return "Left"
            else:
                return "Right"
        else:
            raise ValueError("Invalid step was performed")

    def perform_agent_action(self, current_vertex, action: str, mode: str):
        if action == "Up":
            next_vertex = [current_vertex[0] - 1, current_vertex[1]]
        elif action == "Down":
            next_vertex = [current_vertex[0] + 1, current_vertex[1]]
        elif action == "Left":
            next_vertex = [current_vertex[0], current_vertex[1] - 1]
        elif action == "Right":
            next_vertex = [current_vertex[0], current_vertex[1] + 1]
        else:
            raise ValueError(f"Invalid action: {action}")

        self.perform_agent_step(current_vertex, next_vertex, mode=mode)

    def is_goal_state(self):
        return len(self.packages) == 0 and len(self.placed_packages) == 0 and len(self.picked_packages) == 0

    def _normal_score(self, agent_idx: int):
        raise ValueError("Score is not available in this game mode")

    def _adversarial_score(self, agent_idx: int):
        agent_score = self.agents[agent_idx]["score"]
        rival_agent_score = self.agents[(agent_idx + 1) % 2]["score"]
        return agent_score - rival_agent_score

    # TODO: Sean Idea
    # def _semi_cooperative_score(self, agent_idx: int):
    #     agent_score = self.agents[agent_idx]["score"]
    #     rival_agent_score = self.agents[(agent_idx + 1) % 2]["score"]
    #     score_dict = {
    #         agent_idx: agent_score,
    #         (agent_idx + 1) % 2: rival_agent_score
    #     }
    #     return score_dict

    def _semi_cooperative_score(self, agent_idx: int):
        agent_score = self.agents[agent_idx]["score"]
        rival_agent_score = self.agents[(agent_idx + 1) % 2]["score"]
        return agent_score + 0.5 * rival_agent_score

    def _fully_cooperative_score(self, agent_idx: int = 0):
        agent_score = self.agents[agent_idx]["score"]
        rival_agent_score = self.agents[(agent_idx + 1) % 2]["score"]
        return agent_score + rival_agent_score

    def game_mode_score(self, agent_idx: int):
        return self.game_score_types[self.game_type](agent_idx=agent_idx)

    def __str__(self):
        # Coordinates
        print_data = (
            f"#X {self.X - 1} ; Maximum x coordinate: {self.X - 1}\n"
            f"#Y {self.Y - 1} ; Maximum y coordinate: {self.Y - 1}\n"
        )

        # Packages
        all_packages = self.packages + self.placed_packages + self.picked_packages + self.archived_packages
        all_packages.sort(key=lambda p: p["package_id"])
        for package in all_packages:
            package_id = package["package_id"]
            if package["status"] == "waiting":
                p_time = package['from_time']
                print_data += f"#P 0  T {p_time} ; Package {package_id}: waiting to appear, At time: {p_time}\n"
            elif package["status"] == "placed":
                p_x = package["package_at"][0]
                p_y = package["package_at"][1]
                print_data += f"#P 1  L {p_x} {p_y} ; Package {package_id}: placed, On location: ({p_x},{p_y})\n"
            elif package["status"] == "picked":
                p_agent_id = package["holder_agent_id"]
                print_data += f"#P 2  A {p_agent_id} ; Package {package_id}: picked, By agent: {p_agent_id}\n"
            elif package["status"] == "delivered":
                p_agent_id = package["holder_agent_id"]
                print_data += f"#P 3  A {p_agent_id} ; Package {package_id}: delivered, By agent {p_agent_id}\n"
            elif package["status"] == "disappeared":
                p_time = package["before_time"]
                print_data += f"#P 4  T {p_time} ; Package {package_id}: disappeared, At time {p_time}\n"
            else:
                raise ValueError("Invalid package status")

        print_data += "\n"
        for edge_idx, edge in enumerate(self.special_edges):
            if edge["type"] == "always blocked":
                print_data += f"#E 0 ; Edge {edge_idx}: always blocked\n"
            elif edge["type"] == "fragile":
                print_data += f"#E 1 ; Edge {edge_idx}: fragile\n"
            else:
                raise ValueError("Invalid edge type")

        for agent_idx, agent in enumerate(self.agents):
            if agent["type"] == "Human":
                a_location = agent["location"]
                print_data += (
                    f"#A 0  L ({a_location[0]},{a_location[1]}) ; "
                    f"Agent {agent_idx}: Human agent "
                    f"Location: ({a_location[0]} {a_location[1]})\n"
                )
            elif agent["type"] == "Normal":
                a_location = agent["location"]
                a_score = agent["score"]
                a_actions = agent["number_of_actions"]
                print_data += (
                    f"#A 1  L ({a_location[0]},{a_location[1]})  A {a_actions}  S {a_score} ; "
                    f"Agent {agent_idx}: Normal agent, "
                    f"Location: ({a_location[0]} {a_location[1]}), "
                    f"Number of actions: {a_actions}, "
                    f"Score: {a_score}\n"
                )
            elif agent["type"] == "Interfering":
                a_location = agent["location"]
                a_actions = agent["number_of_actions"]
                print_data += (
                    f"#A 2  L ({a_location[0]},{a_location[1]})  A {a_actions} ; "
                    f"Agent {agent_idx}: Interfering Agent, "
                    f"Location: ({a_location[0]},{a_location[1]}), "
                    f"Number of Actions: {a_actions}\n"
                )
            # elif agent["type"] == "Greedy":
            #     a_location = agent["location"]
            #     a_score = agent["score"]
            #     a_actions = agent["number_of_actions"]
            #     print_data += (
            #         f"#A 3  L {a_location[0]} {a_location[1]}  A {a_actions}  S {a_score} ; "
            #         f"Agent {agent_idx}: Greedy agent, "
            #         f"Location: ({a_location[0]},{a_location[1]}), "
            #         f"Number of actions: {a_actions}, "
            #         f"Score: {a_score}\n"
            #     )
            # elif agent["type"] == "A Star":
            #     a_location = agent["location"]
            #     a_score = agent["score"]
            #     a_actions = agent["number_of_actions"]
            #     print_data += (
            #         f"#A 4  L {a_location[0]} {a_location[1]}  A {a_actions}  S {a_score} ; "
            #         f"Agent {agent_idx}: A Star agent, "
            #         f"Location: ({a_location[0]},{a_location[1]}), "
            #         f"Number of actions: {a_actions}, "
            #         f"Score: {a_score}\n"
            #     )
            # elif agent["type"] == "Real time A Star":
            #     a_location = agent["location"]
            #     a_score = agent["score"]
            #     a_actions = agent["number_of_actions"]
            #     print_data += (
            #         f"#A 5  L {a_location[0]} {a_location[1]}  A {a_actions}  S {a_score} ; "
            #         f"Agent {agent_idx}: Real time A Star agent, "
            #         f"Location: ({a_location[0]} {a_location[1]}), "
            #         f"Number of actions: {a_actions}, "
            #         f"Score: {a_score}\n"
            #     )
            else:
                raise ValueError("Invalid agent type")

        print_data += "\n"
        print_data += f"#T {self.time} ; Total Time unit passed: {self.time}\n"
        print_data += f"#G {self.game_type_to_idx[self.game_type]} ; Game Type: {self.game_type}"

        return print_data

    def clone_state(self, agent_idx: int, time_factor: float = 0):
        environment_data = {
            "x": self.X - 1,
            "y": self.Y - 1,
            "packages": deepcopy(self.packages),
            "special_edges": deepcopy(self.special_edges),
            "agents": deepcopy(self.agents),
            "agent_idx": agent_idx,
            "time": self.time + time_factor,
            "placed_packages": deepcopy(self.placed_packages),
            "picked_packages": deepcopy(self.picked_packages),
            "archived_packages": deepcopy(self.archived_packages),
            "game_type": self.game_type
        }
        return State(environment_data=environment_data)
