from RL.util import Init_throw_range, add_action_to_play_dict, eliminate_and_update_board
from RL.action import get_all_valid_action
from RL.action_evaluation import action_evaluation
from RL.state import State
from RL.random_algorithms import *
from copy import copy

import pandas as pd
import matplotlib.pyplot as plt

class Player:
    
    
    def __init__(self, player):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.
        The parameter player is the string "upper" (if the instance will
        play as Upper), or the string "lower" (if the instance will play
        as Lower).
        """
        self.BREAK_TIE = True   # if algorithm break tie automatically
        self.REFINED_THROW = True   # if using advanced random throw strategy

        self.game_round = 1
        self.throws_left = 9   # reduced by 1 after each throw in util/add_action_board function
        self.enemy_throws_left = 9
        self.side = player
        if self.side == "upper":
            self.enemy_side = "lower"
        else:
            self.enemy_side = "upper"

        # Determine throw range according to different locations
        self.throw_range = tuple()
        self.enemy_throws_range = tuple()
        Init_throw_range(self)
        self.same_state_count = 0  # count of same game state, if reach 3, break the tie to avoid draw

        # play_dict is used to store symbols for each player
        self.play_dict = {"player":{"r":[], "p":[], "s":[]},
                        "opponent":{"r":[], "p":[], "s":[]},
                        "block":[]}                     
                        # "R":[(1,3),(3,4)]   saying Rock1 at position (1,3) and Rock2 at (3,4)
        
        # target_dict is used to store relationship between 2 symbols
        self.target_dict = {"r":"s", "s":"p", "p":"r"}

        # Store Opponent's Action List
        self.opponent_action_evaluation_list = []
        self.opponent_action_count_list = []


    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        
        


        # hard code the first three rounds to lay out my defensive 
        if self.game_round <= 3:
            return open_game_stragety(self)
        else:
            current_state = State(copy(self.play_dict), copy(self.throws_left),
                                 copy(self.enemy_throws_left), copy(self.side))
            action_list = get_all_valid_action("player", current_state)
            action_evaluation_list = []
            value = 0
            for action in action_list:
                # print(action)
                value = action_evaluation("player", current_state, action)
                action_evaluation_list.append( (value, action) )
            
            action_evaluation_list = sorted(action_evaluation_list, reverse=True)
            print(action_evaluation_list[0])
            

            # Get Action Evaluation List for Enemy
            self.opponent_action_evaluation_list = []
            opponent_current_state = State(copy(self.play_dict), copy(self.enemy_throws_left),
                                 copy(self.throws_left), copy(self.enemy_side))
            opponent_action_list = get_all_valid_action("opponent", opponent_current_state)
            
            opponent_value = 0
            for opponent_action in opponent_action_list:
                # print(action)
                opponent_value = action_evaluation("opponent", opponent_current_state, opponent_action)
                self.opponent_action_evaluation_list.append( (opponent_value, opponent_action) )
            
            self.opponent_action_evaluation_list = sorted(self.opponent_action_evaluation_list, reverse=True)



            # if reached same game state three times, break the tie, choosing second best action
            if (self.same_state_count >= 3) and (self.BREAK_TIE):
                return action_evaluation_list[0][1]
            return action_evaluation_list[0][1]
            

        
    
    def update(self, opponent_action, player_action):
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """
        

        i=0
        
        for pair in self.opponent_action_evaluation_list:
            if pair[1] == opponent_action:
                self.opponent_action_count_list.append(i)
                occurred = True
                print("RL2 Evaluation :  Enemy's Best move:")
                print("Best move:")
                print(self.opponent_action_evaluation_list[0])
                print("Chosen move:")
                print(i)
                print(pair)
                break
                #input("Press Enter to continue\n")
            i+=1
        #self.opponent_action_evaluation_list.index(opponent_action)
            #print(self.opponent_action_evaluation_list[0])

        

        #Check Repeated Game State, get previous game state:
        prev_game_state = (get_current_player_nodes_count(self, "player"), get_current_player_nodes_count(self, "opponent"))
        # do not calculate elimination now, just update symbols to play_dict
        # add each player's action to board for the reason of synchronising play.
        # if throw, also reduce throws left by 1

        add_action_to_play_dict(self, "opponent", opponent_action)
        add_action_to_play_dict(self, "player", player_action)

        # update self representation of the game
        # Calculate eliminations and update
        # after token actions, check if eliminate other tokens by following function
        eliminate_and_update_board(self,self.target_dict)
        self.game_round += 1

        #Check Repeated Game State:
        cur_game_state = (get_current_player_nodes_count(self, "player"), get_current_player_nodes_count(self, "opponent"))
        if cur_game_state == prev_game_state:
            self.same_state_count += 1
        else:
            self.same_state_count = 0
        

        #Plot
        if self.throws_left==0 or self.enemy_throws_left==0 or self.same_state_count >= 2:
            if self.opponent_action_count_list:
                dist = pd.DataFrame(self.opponent_action_count_list,columns=["IndexOfEnemyAction"])
                # dist.agg(['min', 'max', 'mean', 'std']).round(decimals=2)
                print("/n/nEnemy Index Mean:")
                print(dist.mean())
                print("/nEnemy Index STD:")
                print(dist.std())
                # fig, ax = plt.subplots()
                # dist.plot.hist(density=True, ax=ax)
                # ax.set_ylabel('Probability')
                # ax.grid(axis='y')
                # ax.set_facecolor('#d8dcd6')
                # plt.savefig("output.png")



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
