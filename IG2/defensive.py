# this module is used to implement to defensive strageties 
# self.play_dict = {"player":{"r":[], "p":[], "s":[]},
#                        "opponent":{"r":[], "p":[], "s":[]},
#                        "block":[]}                     
#                        "R":[(1,3),(3,4)]   saying Rock1 at position (1,3) and Rock2 at (3,4)
from IG2.cognitive_ability import analyse_current_situation, get_all_valid_move, get_all_valid_throw
from IG2.path_search import get_six_adj_nodes, Search_Path
from IG2.util import least_distance, get_symbol_by_location, action_slide, action_swing, action_throw
from IG2.util import move_action
from numpy import random


def open_game_stragety(self):
    if self.game_round == 1: 
        if self.side == "upper":
            return ('THROW', 'r', (4, -4))
        if self.side == "lower":
            return ("THROW", "r", (-4, 2))
    if self.game_round == 2: 
        if self.side == "upper":
            return ("THROW", "p", (3, -2))
        if self.side == "lower":
            return ("THROW", "p", (-3, 2))
    if self.game_round == 3: 
        if self.side == "upper":
            return ("THROW", "s", (4, -1))
        if self.side == "lower":
            return ("THROW", "s", (-3, 1))

def inductive_flee(token_under_threat_pos, counter_pos, hostile_token_pos, self):
    print("_______________________inductive flee__________________________")
    # six adjancent nodes around counter token as destination of token under threat
    adj_nodes = get_six_adj_nodes(counter_pos)
    # do two rounds of sort to find the cloest and optmal destination
    # first round sort, nodes that are cloest to token under threat
    cloest_nodes = sorted(adj_nodes, key = lambda x: least_distance(x, hostile_token_pos))
    # second round sort, find node that is further to the hostile token
    optimal_node = sorted(cloest_nodes, key = lambda x: least_distance(x, hostile_token_pos))[0]
    token_under_threat_type = get_symbol_by_location("player", self.play_dict, token_under_threat_pos)
    path = Search_Path(token_under_threat_type, token_under_threat_pos, optimal_node, self.play_dict)
    next_move = path[1]
    return move_action(token_under_threat_pos, next_move)
    



def awiting_target(hostile_token, token_under_threat_pos, counter_pos, self):
    print("_______________________Awiting target__________________________")
    # hostile_token = (hostile_token_pos, hostile_token_type)
    if least_distance(hostile_token[0], token_under_threat_pos) == 2:
        self.hunt_area = contact_grid_finding(hostile_token, token_under_threat_pos, self)
        # if there are only possible contacting grid, eat the incoming token with counter
        if len(self.hunt_area) == 1:
            return move_action(counter_pos, self.hunt_area[0])
        # if there are two possible chosen contacting grid, randomly choose one
        # and record the preference of the opponent
        else:
            die_num = random.rand()
            if die_num <= 0.5:
                contact_grid = self.hunt_area[0]
            else:
                contact_grid = self.hunt_area[1]
            return move_action(counter_pos, contact_grid)
    # if the threatened token has arrived at safe place and hostile token has yet to arrive
    # if there are two possible contact grid, eliminate one possiblility
    elif least_distance(hostile_token[0], token_under_threat_pos) == 3:
         self.hunt_area = contact_grid_finding(hostile_token, token_under_threat_pos, self)
         if len(self.hunt_area) == 2:
             # eliminate one possiblility
             num_die = int(random.randint(0,1))
             occupied = self.hunt_area[num_die]
             self.hunt_area.remove(occupied)
             return move_action(counter_pos, occupied)
        # if there is only one possible contact grid, move the third token
         else:
            return move_the_third_token(hostile_token[1], self)

    elif least_distance(hostile_token[0], token_under_threat_pos) > 3:
        self.hunt_area = contact_grid_finding(hostile_token, token_under_threat_pos, self)
        return move_the_third_token(hostile_token[1], self)
        

def move_the_third_token(hostile_token_type, self):
    if self.play_dict['player'][hostile_token_type]:
        move_token = (self.play_dict['player'][hostile_token_type][0], hostile_token_type)
        valid_move_list = get_all_valid_move(move_token, self)

        # avoid move into hunt area
        for move in valid_move_list:
            if move in self.hunt_area:
                valid_move_list.remove(move)
        if self.side == "upper":
            valid_move_list = sorted(valid_move_list, key=lambda x: x[0], reverse=True)
        else:
            valid_move_list = sorted(valid_move_list, key=lambda x: x[0])
        next_move = valid_move_list[0]
        return move_action(move_token[0], next_move)  
    else:
        valid_throw_list = get_all_valid_throw(self)
        num_die = int(random.randint(0, len(valid_throw_list)-1) )
        return action_throw(hostile_token_type, valid_throw_list[num_die])       



def contact_grid_finding(hostile_token, token_under_threat_pos, self):
    adj_nodes = get_six_adj_nodes(token_under_threat_pos)
    adj_nodes = sorted(adj_nodes, key=lambda x: least_distance(x, hostile_token[0]))
    # if there esists two grids that are both potential contacting grid
    if least_distance(adj_nodes[0], hostile_token[0]) == \
            least_distance(adj_nodes[1], hostile_token[0]):
        contact_grid = [adj_nodes[0], adj_nodes[1]]
        for grid in contact_grid:
            counter_type = self.target_dict[self.target_dict[hostile_token[1]]]
            if grid in self.play_dict['player'][counter_type]:
                contact_grid.remove(grid)
        return contact_grid
    else:
        return [adj_nodes[0]]

