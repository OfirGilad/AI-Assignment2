from state import State
from node import Node 
from search_manager import SearchManager


LIMIT = 10000


class InformedSearchAlgorithms:
    def __init__(self, initial_node: Node, is_limited: bool = False, L: int = -1, T: float = 0):
        self.initial_node = initial_node
        self.SearchManager = SearchManager(initial_node)
        self.NumOfExpansions = 0
        self.IsLimited = is_limited
        self.L = L
        self.T = T

    def A_star(self):
        while self.SearchManager.numOfNodesInOpenList > 0:
            # Node with the lowest f in the open list -  remove and expand it.
            current_node = self.SearchManager.GetCurrentNode()

            # Assume a global constant of LIMIT expansions (default 10000).
            # If more than LIMIT expansions are done we just return "fail", and the agent does just the "no-op" action.
            if self.NumOfExpansions > LIMIT and self.IsLimited:
                return "fail"
            
            # A* = > Check if goal state = current node's state
            # Realtime A* => The above or check if L expansions were done.
            if current_node.state.is_goal_state() or self.NumOfExpansions == self.L:
                # One of the condition is met => return move decision
                if current_node.get_parent() is None:
                    # If the last node is the root node
                    return current_node.get_action()
                temp_node = current_node
                action = current_node.get_action()
                while temp_node.get_parent().get_parent() is not None:
                    temp_node = temp_node.get_parent()
                    action = temp_node.get_action()

                return action

            # Limit not reached => performing expand
            current_node.expand()
            self.NumOfExpansions += 1
          
            # Node does not contain a goal state - handle its children prior to next expansion.
            children = current_node.get_children()
            for child in children:
                self.SearchManager.ChildrenHandler(child)
           
        return "fail"

    def get_total_time(self):
        return self.NumOfExpansions * self.T
