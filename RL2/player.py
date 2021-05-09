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
        self.opponent_action_score_list = []
        self.opponent_score_df = pd.DataFrame(columns=["Total_Score_Index", "Aggresive_Index", "Defense_Index", "Punishment_Index", "State_Score_Index"])

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
            total, aggresive, defense, punish, state = self.getScoredActionList("player")
            player_score_list = [total, aggresive, defense, punish, state]
            player_total_score_list = player_score_list[0]

            # Get sorted Action Evaluation List for Enemy's choice
            total, aggresive, defense, punish, state = self.getScoredActionList("opponent")
            self.opponent_action_score_list = [total, aggresive, defense, punish, state]


            # Avoid Draw Situation, take another action without using already used ones checked by default dict
            cur_snap = self._snap()
            if (self.history[cur_snap] >= 2 and self.AVOID_DRAW):
                self.cur_snap_used_action_index[cur_snap] += 1
                next_index = self.cur_snap_used_action_index[cur_snap]
                next_index = random.randint(0,12)
                if next_index<len(player_total_score_list):
                    return player_total_score_list[next_index][1]

            # return best action
            return player_total_score_list[0][1]
            

        
    
    def update(self, opponent_action, player_action):
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """

        # count enemy's choices index based on our function into dataframe
        self.update_enemy_index_count_dataframe(opponent_action)

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
        #input("asd")


        #Analyse Enemy's choice based on our evaluation list 
        if self.ANALYSIS_MODE:
            dist = self.opponent_score_df
            # dist.agg(['min', 'max', 'mean', 'std']).round(decimals=2)
            print("\n Enemy Index Mean:")
            print(dist.mean())
            print("\n Enemy Index STD:")
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
        Can Use to get Opponent's score list,
        return 4 score list:

        Total_score_list;
        Aggresive_Score_list;
        Defense_Score_list;
        Punishment_Score_list;
        State_Score_list

        """

        if (whichPlayer == "player"):
            current_state = State(copy(self.play_dict), copy(self.throws_left),
                                copy(self.enemy_throws_left), copy(self.side))
        else:
            #Reverse throws_left and enemy_throws_left for enemy evaluation
            current_state = State(copy(self.play_dict), copy(self.enemy_throws_left),
                                copy(self.throws_left), copy(self.side))

        action_list = get_all_valid_action(whichPlayer, current_state)
        Total_score_list = []
        Aggresive_Score_list = []
        Defense_Score_list = []
        Punishment_Score_list = []
        State_Score_list = []

        total_score = 0
        for action in action_list:
            #Total:
            total_score = action_evaluation(whichPlayer, current_state, action)["total_score"]
            Total_score_list.append( (total_score, action) )
            #Aggresive:
            agg_score = action_evaluation(whichPlayer, current_state, action)["aggresive_score"]
            Aggresive_Score_list.append( (agg_score, action) )
            #Defensive:
            defense_score = action_evaluation(whichPlayer, current_state, action)["defense_score"]
            Defense_Score_list.append( (defense_score, action) )
            #Punishment:
            punishment_score = action_evaluation(whichPlayer, current_state, action)["punishment_score"]
            Punishment_Score_list.append( (punishment_score, action) )
            #StateScore:
            state_score = action_evaluation(whichPlayer, current_state, action)["state_score"]
            State_Score_list.append( (state_score, action) )

        Total_score_list = sorted(Total_score_list, reverse=True)
        Aggresive_Score_list_list = sorted(Aggresive_Score_list, reverse=True)
        Defense_Score_list = sorted(Defense_Score_list, reverse=True)
        Punishment_Score_list = sorted(Punishment_Score_list, reverse=False)
        State_Score_list = sorted(State_Score_list, reverse=True)

        print(whichPlayer+"Total Score List:")
        print(Total_score_list[0])
        return Total_score_list, Aggresive_Score_list, Defense_Score_list, Punishment_Score_list, State_Score_list


    
    # count enemy's choices index based on our function into dataframe
    def update_enemy_index_count_dataframe(self, opponent_action):
        out_list = []
        for score_list in self.opponent_action_score_list:
            i=0
            for pair in score_list:
                if pair[1] == opponent_action:
                    break
                i+=1
            out_list.append(i)
        if (self.opponent_action_score_list):
            self.opponent_score_df = self.opponent_score_df.append({"Total_Score_Index":out_list[0],
                                            "Aggresive_Index":out_list[1],
                                            "Defense_Index":out_list[2],
                                            "Punishment_Index":out_list[3],
                                            "State_Score_Index":out_list[4]},ignore_index=True) 



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

