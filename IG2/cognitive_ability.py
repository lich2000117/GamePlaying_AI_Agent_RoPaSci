# this module is used to implement to defensive strageties 
# self.play_dict = {"player":{"r":[], "p":[], "s":[]},
#                        "opponent":{"r":[], "p":[], "s":[]},
#                        "block":[]}                     
#                        "R":[(1,3),(3,4)]   saying Rock1 at position (1,3) and Rock2 at (3,4)
#
#
# self.target_dict = {"r":"s", "s":"p", "p":"r"}

from IG2.util import least_distance, get_symbol_by_location

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
    history_analysis = analyse_current_situation(self)
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
        # a list of 
        my_token_pos = self.play_dict["player"][my_token]
        enemy_token_pos = self.play_dict["opponent"][enemy]
        if my_token_pos and enemy_token_pos:
            for token in my_token_pos:
                for enemy_token in enemy_token_pos:
                    hostile_tokens.append((enemy, enemy_token, least_distance(enemy_token, token), token))
    hostile_tokens = sorted(hostile_tokens, key=lambda x: x[2])
    return hostile_tokens
