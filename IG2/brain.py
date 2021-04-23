from IG2.cognitive_ability import analyse_current_situation
from IG2.util import closest_one
# self.play_dict = {"player":{"r":[], "p":[], "s":[]},
#                         "opponent":{"r":[], "p":[], "s":[]},
#                         "block":[]}                     
#                         # "R":[(1,3),(3,4)]   saying Rock1 at position (1,3) and Rock2 at (3,4)
        
#         # target_dict is used to store relationship between 2 symbols
#         self.target_dict = {"r":"s", "s":"p", "p":"r"}

def defensive_decision_making(self):
    # num_tokens = [number of my tokens, number of enemy tokens] on the board
    # history_analsis = [type, times that this token was continuously moved, pos]
    # threat_list = [(type, cur_postion, distance to eat my token, my_token_pos)...]
    num_tokens, threat_list, history_analysis = analyse_current_situation(self)

    # analysing the overall tendency on this game
    if num_tokens[0] + self.throws_left > num_tokens[1] + self.enemy_throws_left:
        self.IsAdvantageous = "Winning"
    elif num_tokens[0] + self.throws_left == num_tokens[1] + self.enemy_throws_left:
        self.IsAdvantageous = "Draw"
    else:
        self.IsAdvantageous = "Losing"
    
    if threat_list[0][1] == history_analysis[2]:
        # the token was constantly moved closer
        # assume greedily aggressive stragety
        # prepare to set up traps
        self.status = "Setting up traps"
        token_under_threat_pos = threat_list[0][3]
        counter_type = self.play_dict[self.play_dict[threat_list[0][0]]]
        counter_list = self.play_dict["player"][counter_type]

        # check if we have token that could eliminate incoming hostile token
        if counter_list:
            counter_pos = closest_one(token_under_threat_pos, counter_list)
            if least_distance(counter_pos, token_under_threat_pos) < least_distance()




    




    return 
 