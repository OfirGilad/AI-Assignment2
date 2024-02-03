from ascii_parser import Parser
from state import State
from simulator import Simulator


def run(data_filepath: str):
    parser = Parser()
    environment_data = parser.parse_data(data_filepath=data_filepath)
    # print(environment_data)
    initial_state = State(environment_data=environment_data)
    # print(initial_state.adjacency_matrix)
    simulator = Simulator(initial_state=initial_state)
    simulator.run()


def main():
    # TODO: Fill the data_filepath parameter
    data_filepath = "../input/input.txt"
    run(data_filepath=data_filepath)


if __name__ == '__main__':
    main()
