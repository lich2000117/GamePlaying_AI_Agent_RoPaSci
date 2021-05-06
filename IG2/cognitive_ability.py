# this module is used to implement to defensive strageties 
# self.play_dict = {"player":{"r":[], "p":[], "s":[]},
#                        "opponent":{"r":[], "p":[], "s":[]},
#                        "block":[]}                     
#                        "R":[(1,3),(3,4)]   saying Rock1 at position (1,3) and Rock2 at (3,4)
#
#
# self.target_dict = {"r":"s", "s":"p", "p":"r"}

from IG2.util import least_distance, get_symbol_by_location
from IG2.path_search import get_six_adj_nodes, Search_Path, is_point_valid, check_counter_node


def analyse_current_situation(self):
    '''Do various kinds of analysis of the situation on the board and send the recognized info to the 
        brain in order to make decision based on gathered info
    '''
    # num_tokens = [number of my tokens, number of enemy tokens] on the board
    num_tokens = [len(self.play_dict["player"]["r"] + self.play_dict["player"]["p"] + \
        self.play_dict["player"]["s"]), 
        len(self.play_dict["opponent"]["r"] + self.play_dict["opponent"]["p"] + \
            self.play_dict["opponent"]["s"])]
    threat_list = hostile_tokens(self)
    history_analysis = analyse_history(self)
    return [num_tokens, threat_list, history_analysis]

def analyse_history(self):
    # it returns a list containing [type, times that this token was continuously moved, pos]
    same_token_move_count= 0
    if self.game_round > 1:
        current_move = self.enemy_move_history[0]
        previous_move = self.enemy_move_history[1]
        if current_move[1] == previous_move[2]:
            same_token_move_count += 1
        else:
            self.log_history.append(same_token_move_count)
            same_token_move_count = 0
    token_type = get_symbol_by_location("opponent", self.play_dict, current_move[2])
    return [token_type, same_token_move_count, current_move[2]]

def hostile_tokens(self):

    # return list of tuples, each tuple contains (type, cur_postion, distance to eat my token, my_token_pos)
    # 
    hostile_tokens = []  
    for enemy, my_token in self.target_dict.items():
        my_token_pos = self.play_dict["player"][my_token]
        enemy_token_pos = self.play_dict["opponent"][enemy]
        if my_token_pos and enemy_token_pos:
            for token in my_token_pos:
                for enemy_token in enemy_token_pos:
                    hostile_tokens.append((enemy, enemy_token, least_distance(enemy_token, token), token))

    hostile_tokens = sorted(hostile_tokens, key=lambda x: x[2])
    return hostile_tokens


def get_all_valid_throw(self):
    """This function is used to generate all the possible throw"""
    have_thrown = 9 - self.throws_left
    throw_list = []
    if self.side == "upper" and self.throws_left > 0:
        for row in range(4, 3 - have_thrown, -1):
            for col in range(-4, 5):
                if abs(row + col) <= 4:
                    throw_list.append((row, col))
    elif self.side == "lower" and self.throws_left > 0:
        for row in range(-4, -3 + have_thrown):
            for col in range(-4, 5):
                if abs(row + col) <= 4:
                    throw_list.append((row, col))
    return throw_list

def get_all_valid_move(move_token, self):
    # move token should be in the format (pos, type)
    adj_nodes = get_six_adj_nodes(move_token[0])
    player_token_list = [item for sublist in self.play_dict["player"].values() for item in sublist]
    valid_move_list = []
    move_list = []
    move_list += adj_nodes
    for node in adj_nodes:
        if node in player_token_list:
            swing_nodes = []
            for swing_node in get_six_adj_nodes(node):
                if least_distance(swing_node, move_token[0]) == 2:
                    swing_nodes.append(swing_node)
            move_list += swing_nodes
    
    # check all the move node whether they are off the grid or will be eaten or eat friendly
    for move in move_list:
        if is_point_valid(move) and check_counter_node(self.play_dict, move_token[1], move):
            valid_move_list.append(move)
    return valid_move_list


def isSupportOnTime(self, token_under_threat_pos, counter_pos, hostile_token_pos):
    intercept_points = get_six_adj_nodes(token_under_threat_pos)
    intercept_points.sort(key=lambda x: least_distance(x, hostile_tokens))
    intercept_points = [intercept_points[0], intercept_points[1]]

    counter_type = get_symbol_by_location("player", self.play_dict, counter_pos)
    hostile_token_type = get_symbol_by_location("opponent", self.play_dict, hostile_token_pos)

    for point in intercept_points:
        counter_path = Search_Path(counter_type, counter_pos, point, self.play_dict)
        hostile_path = Search_Path(hostile_token_type, hostile_token_pos, point, self.play_dict)
        if len(counter_path) > len(hostile_path):
            return False
    return True




