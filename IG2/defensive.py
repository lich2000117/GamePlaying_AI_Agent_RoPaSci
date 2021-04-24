# this module is used to implement to defensive strageties 
# self.play_dict = {"player":{"r":[], "p":[], "s":[]},
#                        "opponent":{"r":[], "p":[], "s":[]},
#                        "block":[]}                     
#                        "R":[(1,3),(3,4)]   saying Rock1 at position (1,3) and Rock2 at (3,4)
from IG2.cognitive_ability import analyse_current_situation
from IG2.brain import defensive_decision_making


def defensive_action(self):
    ''' the central stragety of defense is to unite tokens together and form an triangle
    in the area where enemy can not directly use throw to attack. And hide lethal tokens at the back
    and take incoming hostile token with swing action
    '''

    situation = []
    situation = defensive_decision_making(self)
    return situation

def open_game_stragety(self):
    if self.game_round == 1: 
        if self.side == "upper":
            return ('THROW', 'r', (4, -2))
        if self.side == "lower":
            return ("THROW", "r", (-4, 2))
    if self.game_round == 2: 
        if self.side == "upper":
            return ("THROW", "p", (3, -2))
        if self.side == "lower":
            return ("THROW", "p", (-3, 2))
    if self.game_round == 3: 
        if self.side == "upper":
            return ("THROW", "s", (3, -1))
        if self.side == "lower":
            return ("THROW", "s", (-3, 1))
    