class Parser:
    def __init__(self):
        self.current_package_id = 0
        self.parsed_data = {
            "x": 0,
            "y": 0,
            "packages": list(),
            "special_edges": list(),
            "agents": list()
        }
        self.options_dict = {
            "#X": self._handle_x,
            "#Y": self._handle_y,
            "#P": self._handle_p,
            "#B": self._handle_b,
            "#F": self._handle_f,
            "#A": self._handle_a,
            "#H": self._handle_h,
            "#I": self._handle_i,
            "#A1": self._handle_a1,
            "#A2": self._handle_a2,
            "#A3": self._handle_a3,
        }

    def _handle_x(self, line_data_args):
        self.parsed_data["x"] = int(line_data_args[1])

    def _handle_y(self, line_data_args):
        self.parsed_data["y"] = int(line_data_args[1])

    def _handle_p(self, line_data_args):
        package = {
            "package_at": [int(line_data_args[1]), int(line_data_args[2])],
            "from_time": int(line_data_args[3]),
            "deliver_to": [int(line_data_args[5]), int(line_data_args[6])],
            "before_time": int(line_data_args[7]),
            "package_id": self.current_package_id,
            "status": "waiting",
            "holder_agent_id": -1
        }
        self.parsed_data["packages"].append(package)
        self.current_package_id += 1

    def _handle_b(self, line_data_args):
        edge = {
            "type": "always blocked",
            "from": [int(line_data_args[1]), int(line_data_args[2])],
            "to": [int(line_data_args[3]), int(line_data_args[4])],
        }
        self.parsed_data["special_edges"].append(edge)

    def _handle_f(self, line_data_args):
        edge = {
            "type": "fragile",
            "from": [int(line_data_args[1]), int(line_data_args[2])],
            "to": [int(line_data_args[3]), int(line_data_args[4])],
        }
        self.parsed_data["special_edges"].append(edge)

    def _handle_a(self, line_data_args):
        agent = {
            "type": "Normal",
            "location": [int(line_data_args[1]), int(line_data_args[2])],
            "score": 0,
            "packages": list(),
            "number_of_actions": 0
        }
        self.parsed_data["agents"].append(agent)

    def _handle_h(self, line_data_args):
        agent = {
            "type": "Human",
            "location": [int(line_data_args[1]), int(line_data_args[2])]
        }
        self.parsed_data["agents"].append(agent)

    def _handle_i(self, line_data_args):
        agent = {
            "type": "Interfering",
            "location": [int(line_data_args[1]), int(line_data_args[2])],
            "number_of_actions": 0
        }
        self.parsed_data["agents"].append(agent)

    def _handle_a1(self, line_data_args):
        agent = {
            "type": "Greedy",
            "location": [int(line_data_args[1]), int(line_data_args[2])],
            "score": 0,
            "packages": list(),
            "number_of_actions": 0
        }
        self.parsed_data["agents"].append(agent)

    def _handle_a2(self, line_data_args):
        agent = {
            "type": "A Star",
            "location": [int(line_data_args[1]), int(line_data_args[2])],
            "score": 0,
            "packages": list(),
            "number_of_actions": 0
        }
        self.parsed_data["agents"].append(agent)

    def _handle_a3(self, line_data_args):
        agent = {
            "type": "Real time A Star",
            "location": [int(line_data_args[1]), int(line_data_args[2])],
            "score": 0,
            "packages": list(),
            "number_of_actions": 0
        }
        self.parsed_data["agents"].append(agent)

    def parse_data(self, data_filepath):
        with open(data_filepath) as data_file:
            line_data = data_file.readline()
            while line_data != "":
                line_data_args = line_data.split()
                if len(line_data_args) != 0 and line_data_args[0] in self.options_dict.keys():
                    self.options_dict[line_data_args[0]](line_data_args)
                line_data = data_file.readline()
        return self.parsed_data
