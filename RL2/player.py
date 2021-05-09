from RL.util import *
from RL.action import get_all_valid_action
from RL2.action_evaluation import action_evaluation
from RL.state import State
from RL.random_algorithms import *
from copy import copy
import random

import pandas as pd
import matplotlib.pyplot as plt
import collections
from collections import defaultdict as dd

class Player:
    
    
    def __init__(self, player):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.
        The parameter player is the string "upper" (if the instance will
        play as Upper), or the string "lower" (if the instance will play
        as Lower).
        """
        self.ANALYSIS_MODE = True
        self.AVOID_DRAW = True   # if algorithm break tie automatically
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

        # Store history to Check Draw Game
        self.history = collections.Counter({self._snap(): 1})
        self.cur_snap_used_action_index = dd(int)  # a dictionary that stores used action for every snap to avoid those steps in the future
            # {state1: 0,1,2}   at state1 used action at index 0, 1 and 2, so next time starting from 3



    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        
        # hard code the first three rounds to lay out my defensive 
        if self.game_round <= 3:
            return open_game_stragety(self)
        else:
            # Get sorted Scored Action Evaluation List for us to choose
            action_evaluation_list = self.getScoredActionList("player")

            # Get sorted Action Evaluation List for Enemy's choice
            self.opponent_action_evaluation_list = self.getScoredActionList("opponent")

            # Avoid Draw Situation, take another action without using already used ones checked by default dict
            cur_snap = self._snap()
            if (self.history[cur_snap] >= 2 and self.AVOID_DRAW):
                self.cur_snap_used_action_index[cur_snap] += 1
                next_index = self.cur_snap_used_action_index[cur_snap]
                next_index = random.randint(0,12)
                if next_index<len(action_evaluation_list):
                    return action_evaluation_list[next_index][1]

            # return best action
            return action_evaluation_list[0][1]
            

        
    
    def update(self, opponent_action, player_action):
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """

        # count enemy's choices index based on our function
        i=0
        for pair in self.opponent_action_evaluation_list:
            if pair[1] == opponent_action:
                self.opponent_action_count_list.append(i)
                # print("RL2 Evaluation :  Enemy's Best move:")
                # print("Best move:")
                # print(self.opponent_action_evaluation_list[0])
                # print("Chosen move:")
                # print(i)
                # print(pair)
                break
            i+=1
        
        
        # do not calculate elimination now, just update symbols to play_dict
        # add each player's action to board for the reason of synchronising play.
        # if throw, also reduce throws left by 1

        add_action_to_play_dict(self, "opponent", opponent_action)
        add_action_to_play_dict(self, "player", player_action)

        # update self representation of the game
        # Calculate eliminations and update
        # after token actions, check if eliminate other tokens by following function
        eliminate_and_update_board(self,self.target_dict)

        # Take a snap of current game state and store it
        cur_snap = self._snap()
        self.history[cur_snap] += 1
        

        self.game_round += 1

        

        #Analyse Enemy's choice based on our evaluation list 
        if self.ANALYSIS_MODE:
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

    
    def _snap(self):
        """
        Capture the current play state in a hashable way
        (for repeated-state checking)
        reference: referee/game.py from Melbourne Uni AI Tutor's code
        """
        play_history = []
        for i in "rps":
            play_history.append(tuple(sorted(self.play_dict["player"][i])))
            play_history.append(tuple(sorted(self.play_dict["opponent"][i])))
        return (tuple(play_history),
            # with the same number of throws remaining for each player
            self.throws_left,
            self.enemy_throws_left,
        )



    def getScoredActionList(self, whichPlayer):
        """
        Get Sorted List Based on Scoring Function,
        Can Use to get Opponent's score list
        """
        if (whichPlayer == "player"):
            current_state = State(copy(self.play_dict), copy(self.throws_left),
                                copy(self.enemy_throws_left), copy(self.side))
        else:
            #Reverse throws_left and enemy_throws_left for enemy evaluation
            current_state = State(copy(self.play_dict), copy(self.enemy_throws_left),
                                copy(self.throws_left), copy(self.side))

        action_list = get_all_valid_action(whichPlayer, current_state)
        action_evaluation_list = []
        value = 0
        for action in action_list:
            value = action_evaluation(whichPlayer, current_state, action)
            action_evaluation_list.append( (value, action) )
        action_evaluation_list = sorted(action_evaluation_list, reverse=True)
        print(whichPlayer+"Evaluation List:")
        print(action_evaluation_list[0])
        return action_evaluation_list




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

