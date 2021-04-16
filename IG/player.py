from IG.util import *

class Player:
    
    
    def __init__(self, player):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.
        The parameter player is the string "upper" (if the instance will
        play as Upper), or the string "lower" (if the instance will play
        as Lower).
        """
        board_dict = {}
        self.game_round = 1
        self.throws_left = 9   # reduced by 1 after each throw in util/put_action_board function
        self.throw_row = 3 #available throw row 
        # Determine throw range according to different locations
        if player == "lower":
            self.throw_range = range(-4,-self.throw_row)  # available throw range
            self.enemy_throw_range = range(self.throw_row+1,5)
            self.side = "lower"
        else:
            self.throw_range = range(self.throw_row+1,5)
            self.enemy_throw_range = range(-4,-self.throw_row)
            self.side = "upper"

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
        # put your code here

        #throw at the farest possible grid
        #action = ("THROW","s", (1,0))
        for i in self.throw_range:
            a = 1
        return ("THROW","s", (i,0))
    
    def update(self, opponent_action, player_action):
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """
        # do not calculate elimination now, just add symbols
        # add each player's action to board
        # for the reason of synchronising play
        # if throw, also reduce throws left by 1
        put_action_to_board(self, "opponent", opponent_action, self.play_dict)
        put_action_to_board(self, "player", player_action, self.play_dict)

        # Calculate eliminations and update
        # after token actions, check if eliminate other tokens by following function
        eliminate_and_update_board(self.play_dict, self.target_dict)
        self.game_round += 1

        # if not reached whole board throw, expanding the throw range
        if self.throw_row >= -4:
            self.throw_row -= 1

        if self.side == "lower":
            self.throw_range = range(-4,-self.throw_row)
            self.enemy_throw_range = range(self.throw_row+1,5)
        else:
            self.throw_range = range(self.throw_row+1,5)
            self.enemy_throw_range = range(-4,-self.throw_row)