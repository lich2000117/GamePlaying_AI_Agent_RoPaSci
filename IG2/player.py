from IG2.util import Init_throw_range, add_action_to_play_dict, eliminate_and_update_board
from IG2.defensive import open_game_stragety
from IG2.aggressive import aggressive_action
from IG2.brain import defensive_decision_making

class Player:
    
    
    def __init__(self, player):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.
        The parameter player is the string "upper" (if the instance will
        play as Upper), or the string "lower" (if the instance will play
        as Lower).
        """

        # used to determine the strategy for several turns
        self.mod = "defensive"  
        # a flag used to determine the next immediate move
        self.status = "defensive"  #can be "awaiting prey", "check kill", "kill confirm"
        self.IsAdvantageous = "draw"

        self.game_round = 1
        self.throws_left = 9   # reduced by 1 after each throw in util/add_action_board function
        self.enemy_throws_left = 9
        self.side = player

        # Determine throw range according to different locations
        self.throw_range = tuple()
        self.enemy_throws_range = tuple()
        Init_throw_range(self)

        # list used to record the history of enemy movement
        self.enemy_move_history = []
        self.log_history = []  # used to output for further analysis after the game
        self.history_limit = 5
        self.hunt_area = []  # used to mark the area where I eliminate opponnet's token
        
        # play_dict is used to store symbols for each player
        self.play_dict = {"player":{"r":[], "p":[], "s":[]},
                        "opponent":{"r":[], "p":[], "s":[]},
                        "block":[]}                     
                        # "R":[(1,3),(3,4)]   saying Rock1 at position (1,3) and Rock2 at (3,4)
        
        # target_dict is used to store relationship between 2 symbols
        self.target_dict = {"r":"s", "s":"p", "p":"r"}


    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        # hard code the first three rounds to lay out my defensive 
       

        if self.game_round <= 3:
            return open_game_stragety(self)
        else:      
            #isContinue = input("Do you want to continue the game? Y/N \n")
            isContinue = True
            if isContinue == 'N' or isContinue == 'n':
                print(isContinue, isContinue == 'N' or isContinue == 'n')
            else:
                if self.mod == "defensive":
                    return defensive_decision_making(self)
                if self.mod == "aggressive":
                    return defensive_decision_making(self) 

        
    
    def update(self, opponent_action, player_action):
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """
        #Check Repeated Game State, get previous game state:
        # do not calculate elimination now, just update symbols to play_dict
        # add each player's action to board for the reason of synchronising play.
        # if throw, also reduce throws left by 1
        if len(self.enemy_move_history) < self.history_limit:
            self.enemy_move_history.insert(0, opponent_action)
        else:
            self.enemy_move_history.pop(4)
            self.enemy_move_history.insert(0, opponent_action)

        add_action_to_play_dict(self, "opponent", opponent_action)
        add_action_to_play_dict(self, "player", player_action)

        # update self representation of the game
        # Calculate eliminations and update
        # after token actions, check if eliminate other tokens by following function
        eliminate_and_update_board(self,self.target_dict)
        self.game_round += 1
