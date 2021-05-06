from IG2.cognitive_ability import analyse_current_situation, isSupportOnTime, get_all_valid_move
from IG2.util import closest_one, least_distance, get_symbol_by_location, move_action
from IG2.defensive import inductive_flee, awiting_target
import random
# self.play_dict = {"player":{"r":[], "p":[], "s":[]},
#                         "opponent":{"r":[], "p":[], "s":[]},
#                         "block":[]}                     
#                         # "R":[(1,3),(3,4)]   saying Rock1 at position (1,3) and Rock2 at (3,4)
        
#         # target_dict is used to store relationship between 2 symbols
#         self.target_dict = {"r":"s", "s":"p", "p":"r"}

def defensive_decision_making(self):
    ''' the central stragety of defense is to unite tokens together and form an triangle
    in the area where enemy can not directly use throw to attack. And hide lethal tokens at the back
    and take incoming hostile token with swing action
    '''

    # num_tokens = [number of my tokens, number of enemy tokens] on the board
    # history_analsis = [type, times that this token was continuously moved, pos]
    # threat_list = [(type, cur_postion, distance to eat my token, my_token_pos),(...)]
    num_tokens, threat_list, history_analysis = analyse_current_situation(self)
    

    # analysing the overall tendency on this game
    if num_tokens[0] + self.throws_left > num_tokens[1] + self.enemy_throws_left:
        self.IsAdvantageous = "Winning"
    elif num_tokens[0] + self.throws_left == num_tokens[1] + self.enemy_throws_left:
        self.IsAdvantageous = "Draw"
    else:
        self.IsAdvantageous = "Losing"
    
    if threat_list and threat_list[0][1]:
        # the token was constantly moved closer and the distance is less than 3 steps
        # assume greedily aggressive stragety
        # prepare to set up traps
        self.status = "Setting up traps"
        token_under_threat_pos = threat_list[0][3]
        hostile_token_pos = threat_list[0][1]
        hostile_token_type = threat_list[0][0]
        counter_type = self.target_dict[self.target_dict[threat_list[0][0]]]
        counter_list = self.play_dict["player"][counter_type]

        # check if we have token that could eliminate incoming hostile token
        if counter_list:
            # find the closest friendly counter
            counter_pos = closest_one(token_under_threat_pos, counter_list)
            if least_distance(counter_pos, token_under_threat_pos) >= 2:
                return inductive_flee(token_under_threat_pos, counter_pos, hostile_token_pos, self)
            else:
                return awiting_target((hostile_token_pos, hostile_token_type),
                                        token_under_threat_pos, counter_pos, self)
        # if there is no counter token
    else:
        player_token_list = [item for sublist in self.play_dict["player"].values() for item in sublist]
        move_token = (player_token_list[0], get_symbol_by_location("player", self.play_dict, player_token_list[0]))
        valid_move_list = get_all_valid_move(move_token, self)
        
        valid_move_list = sorted(valid_move_list, key=lambda x: x[0], reverse=True)
        next_move = valid_move_list[0]
        return move_action(move_token[0], next_move)  
        
 