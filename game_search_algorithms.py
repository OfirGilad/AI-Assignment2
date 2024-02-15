import numpy as np

from game_node import GameNode


class GameAlgorithms:
    def __init__(self, agent_idx: int):
        self.agent_idx = agent_idx
        self.rival_agent_idx = (self.agent_idx + 1) % 2
        self.semi_cooperative = False

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
            # TODO: Check if this is correct
            if max_value >= beta :
                return max_value
            alpha = max(alpha, max_value)

        return max_value

    def min_value(self, game_node: GameNode, alpha, beta) -> int:
        if game_node.state.is_goal_state():
            min_value = game_node.state.game_mode_score(agent_idx=self.agent_idx)
            return min_value

        min_value = np.inf
        game_node.expand()
        
        for child in game_node.children:
            max_value = self.max_value(game_node=child, alpha=alpha, beta=beta)
            if self.semi_cooperative == False:
                min_value = min(min_value, max_value)
            # TODO: Check if this is correct
            if min_value <= alpha :
                return min_value
            beta = min(beta, min_value)

        return min_value


    def semi_cooperative_decision(self, game_node: GameNode) -> str:
       
        max_dict = {self.agent_idx:-np.inf, self.rival_agent_idx: -np.inf}
        max_action = "no-op"
        game_node.expand()
        
        for child in game_node.children:
            action = child.action
            min_dict = self.min_value_semi_cooperative(game_node=child)
            if min_dict[self.agent_idx] > max_dict[self.agent_idx]:
                max_action = action
                max_dict = min_dict
            elif min_dict[self.agent_idx] == max_dict[self.agent_idx] and max_dict[self.rival_agent_idx]<min_dict[self.rival_agent_idx] :
                #Tie breaker
                max_action = action
                max_dict[self.rival_agent_idx] = min_dict[self.rival_agent_idx]
                
                
                
        return max_action
    
    
#{agent_idx:agent_score, (self.game_agent_idx + 1) % 2 :rival_agent_score}
    def max_value_semi_cooperative(self, game_node: GameNode) -> int:
        if game_node.state.is_goal_state():
            max_dict = game_node.state.game_mode_score(agent_idx=self.agent_idx)
            return max_dict

        max_dict = {self.agent_idx:-np.inf, self.rival_agent_idx: -np.inf}
        game_node.expand()
        for child in game_node.children:
            min_dict = self.min_value_semi_cooperative(game_node=child)
            if min_dict[self.agent_idx] > max_dict[self.agent_idx]:
                max_dict = min_dict
            elif min_dict[self.agent_idx] == max_dict[self.agent_idx] :
                #Tie breaker
                max_dict[self.rival_agent_idx] = max(max_dict[self.rival_agent_idx],min_dict[self.rival_agent_idx])

        return max_dict

    def min_value_semi_cooperative(self, game_node: GameNode) -> int:
        if game_node.state.is_goal_state():
            min_dict = game_node.state.game_mode_score(agent_idx=self.agent_idx)
            return min_dict

        min_dict = {self.agent_idx:-np.inf, self.rival_agent_idx: -np.inf}
        game_node.expand()
        
        for child in game_node.children:
            max_dict = self.max_value_semi_cooperative(game_node=child)
            if min_dict[self.agent_idx] < max_dict[self.agent_idx]:
                min_dict = max_dict  
            elif min_dict[self.agent_idx] == max_dict[self.agent_idx] :
                #Tie breaker
                min_dict[self.rival_agent_idx] = max(max_dict[self.rival_agent_idx],min_dict[self.rival_agent_idx])


        return min_dict
