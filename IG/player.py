from IG.util import *
from IG.random_algorithms import *

class Player:
    
    
    def __init__(self, player):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.
        The parameter player is the string "upper" (if the instance will
        play as Upper), or the string "lower" (if the instance will play
        as Lower).
        """
        self.game_round = 1
        self.throws_left = 9   # reduced by 1 after each throw in util/put_action_board function
        self.enemy_throws_left = 9
        self.side = player
        # Determine throw range according to different locations
        Init_throw_range(self)

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
        # Random Action defined in random_algorithms.py
        return random_action(self)
        


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
        # do not calculate elimination now, just update symbols to play_dict
        # add each player's action to board for the reason of synchronising play.
        # if throw, also reduce throws left by 1
        
        add_action_to_play_dict(self, "opponent", opponent_action)
        add_action_to_play_dict(self, "player", player_action)

        # Calculate eliminations and update
        # after token actions, check if eliminate other tokens by following function
        eliminate_and_update_board(self,self.target_dict)
        self.game_round += 1


        # if not reached whole board throw range, expanding the throw range
        update_throw_range(self)
        print("\nafter round, play_dict:", self.play_dict)
        print("\n\nthrows_left", self.throws_left)
        print("\n\nEnemy_throws_left", self.enemy_throws_left)
        print("\n\n")