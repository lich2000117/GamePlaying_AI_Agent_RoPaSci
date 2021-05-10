from RL.util import Init_throw_range, add_action_to_play_dict, eliminate_and_update_board, calculate_normal_probability, get_symbol_by_location
from RL.action import get_all_valid_action
from RL.action_evaluation import action_evaluation
from RL.state import State
from copy import copy
from copy import deepcopy
import random
from RL.random_algorithms import refined_random_throw, random_throw, random_action, get_current_player_nodes_count
import csv
from RL.learning import temporal_difference_learning
import os

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
        self.TEMPORAL_DIFF_LEARNING = False
        self.GREEDY_PREDICT = False
        self.EXCLUDE_THROW_DIST = True
        self.ANALYSIS_MODE = True
        self.AVOID_DRAW = True   # if algorithm break tie automatically
        self.REFINED_THROW = True   # if using advanced random throw strategy
        self.CONFIDENCE_LEVEL = 0.05   #confidence level to exclude outliers into distribution
        self.IGNORE_ROUND = 5  # ignore first 5 rounds when doing probability predicting
        self.beta = 0.01
        self.episilon = 0.3

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
        self.score_names = ["Total_Score_Index", "Aggresive_Index", "Defense_Index", "Punishment_Index", "State_Score_Index"]
        self.opponent_score_df = pd.DataFrame(columns=self.score_names)
        self.enemy_action_dist_dict = {}
        self.predicted_enemy_action = ()
        self.corrected_predict = 0
        self.total_predict = 0
        for name in self.score_names:
            self.enemy_action_dist_dict[name] = {"mean":0,"std":200}  #this dict store each score's distribution
        
        

        # Store history to Check Draw Game
        self.history = collections.Counter({self._snap(): 1})
        self.cur_snap_used_action_index = dd(int)  # a dictionary that stores used action for every snap to avoid those steps in the future
            # {state1: 0,1,2}   at state1 used action at index 0, 1 and 2, so next time starting from 3
        self.states_list = []   # used to store states happen in the past turn, a list of State object



    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        
        selected_score = 0
        selected_index = 0
        # Get Enemy Action's Probability and index
        if (self.game_round >= self.IGNORE_ROUND *2):
            df = self.opponent_score_df
            # Select The Score we want to use to evaluate enemy's action
            # Selecting Least Standard Deviation one
            if df.isnull:
                selected_mean = 0
            else:
                min_std = min(df.std())
                # if select 0 std deviation use default total_score mean
                if min_std == 0:
                    selected_mean = df.loc[:,"Total_Score_Index"].mean().astype(int)
                    selected_std = df.loc[:,"Total_Score_Index"].std()
                    selected_score = 0
                else:
                    selected_enemy_score_df = df.loc[:,(df.std()==min_std)]
                    if (len(selected_enemy_score_df.columns)>1):
                        # use first column if multiple column have same std
                        selected_enemy_score_df = selected_enemy_score_df.iloc[:,0]
                    selected_mean = selected_enemy_score_df.mean().astype(int)
                    selected_std = selected_enemy_score_df.std()
                    for name in self.score_names:
                        if df[name].std()==min_std:
                            selected_score = self.score_names.index(name)  # find smallest std score name 
                print(selected_mean)            
                selected_index = int(round(selected_mean))
            if (self.ANALYSIS_MODE):
                print("``````````````````````````````````````````")
                print("selected_score name")
                print(str(selected_score))
                print("selected_enemy_index")
                print(selected_index)
                print("``````````````````````````````````````````")
                #input("asd")


        # hard code the first three rounds to lay out my defensive 
        if self.game_round <= 3:
            return open_game_stragety(self)
        else:
            # Get sorted Action Evaluation List for Enemy's choice
            total, aggresive, defense, punish, state = self.getScoredActionList("opponent")
            self.opponent_action_score_list = [total, aggresive, defense, punish, state]

            #Next Enemy Action
            if (self.opponent_action_score_list):
                if (len(self.opponent_action_score_list[selected_score]) > selected_index):
                    next_enemy_action = self.opponent_action_score_list[selected_score][selected_index][1]
                else:
                    next_enemy_action = self.opponent_action_score_list[0][0][1]
                # always greedy predict enemy
                if (self.GREEDY_PREDICT):
                    next_enemy_action = self.opponent_action_score_list[0][0][1]  

            
            # Get sorted Scored Action Evaluation List for us to choose
            self.predicted_enemy_action = next_enemy_action
            total, aggresive, defense, punish, state = self.getScoredActionList("player", next_enemy_action)
            player_score_list = [total, aggresive, defense, punish, state]
            player_total_score_list = player_score_list[0]

            


            # Avoid Draw Situation, take another action without using already used ones checked by default dict
            cur_snap = self._snap()
            if (self.history[cur_snap] >= 2 and self.AVOID_DRAW):
                self.cur_snap_used_action_index[cur_snap] += 1
                next_index = self.cur_snap_used_action_index[cur_snap]
                next_index = random.randint(0,12)
                if next_index<len(player_total_score_list):
                    return player_total_score_list[next_index][1]
            
            # return best action, if no action, do evaluation without enemy's action
            if len(player_total_score_list) < 1:
                player_total_score_list = self.getScoredActionList("player", next_enemy_action)
            return player_total_score_list[0][1]
            

        
    
    def update(self, opponent_action, player_action):
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """

        # Get the accuracy of our prediction
        if self.predicted_enemy_action:
            self.total_predict += 1
            if (self.predicted_enemy_action == opponent_action):
                self.corrected_predict += 1
                

        # count enemy's choices index based on our function into dataframe
        if (self.game_round > self.IGNORE_ROUND):
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

        # store state into a file 
        new_state = State(copy(self.play_dict), copy(self.throws_left),
                                 copy(self.enemy_throws_left), copy(self.side))
        self.states_list.append(new_state)

        if (self.game_round >= 4) and (self.TEMPORAL_DIFF_LEARNING==True):
            if os.stat("RL/weights.csv").st_size == 0:
                pre_w = [10, 5, -5]
            else:
                with open("RL/weights.csv") as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    row = next(csv_reader)
                    pre_w = []
                    for num in row:
                        pre_w.append(float(num))
                #print("Previous weight: ", pre_w)
                update_w = temporal_difference_learning(self.states_list, pre_w, self.beta) 
                #print("Weights after update: ", update_w)                       
                with open('RL/weights.csv', 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(update_w)


        #input("\nPress enter to continue! ")

        # Take a snap of current game state and store it
        cur_snap = self._snap()
        self.history[cur_snap] += 1
        
        self.game_round += 1


        #Analyse Enemy's choice based on our evaluation list 
        if ((self.game_round>self.IGNORE_ROUND) and (self.ANALYSIS_MODE)):
            dist = self.opponent_score_df
            # dist.agg(['min', 'max', 'mean', 'std']).round(decimals=2)
            print("\n Enemy Index Mean:")
            print(dist.mean())
            print("\n Enemy Index STD:")
            print(dist.std())
            print("\nAccuracy of Prediction:")
            if self.total_predict:
                print(round(self.corrected_predict/self.total_predict,3))
            print("\nMake Prediction Percentage:")
            print(round(self.total_predict/self.game_round,3))
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



    def getScoredActionList(self, whichPlayer, Enemy_Next_Action=None):
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
            side = self.side
            prev_state = State(copy(self.play_dict), copy(self.throws_left),
                                copy(self.enemy_throws_left), copy(side))
        else:
            if self.side == "upper":
                side = "lower"
            else:
                side = "upper"
            #Reverse throws_left and enemy_throws_left for enemy evaluation
            prev_state = State(copy(self.play_dict), copy(self.enemy_throws_left),
                                copy(self.throws_left), copy(side))

        action_list = get_all_valid_action(whichPlayer, prev_state)
        # add enemy next action into state
        if Enemy_Next_Action:
            next_state = add_next_action_to_play_dict(prev_state, "opponent", Enemy_Next_Action)
            #eliminate_and_update_board(next_state, prev_state.target_dict)
        else:
            next_state = prev_state
        if (self.ANALYSIS_MODE):
            print("````````````````````````````````Enemy_Next_Action````````````````````````````````")
            print(Enemy_Next_Action)
            #input("asdasd")
        Total_score_list = []
        Aggresive_Score_list = []
        Defense_Score_list = []
        Punishment_Score_list = []
        State_Score_list = []
        Reward_list = []

        total_score = 0
        
        for action in action_list:
            scoring_dict = action_evaluation(whichPlayer, next_state, action)
            #Total:
            total_score = scoring_dict["total_score"]
            Total_score_list.append( (total_score, action) )
            #Aggresive:
            agg_score = scoring_dict["aggresive_score"]
            Aggresive_Score_list.append( (agg_score, action) )
            #Defensive:
            defense_score = scoring_dict["defense_score"]
            Defense_Score_list.append( (defense_score, action) )
            #Punishment:
            punishment_score = scoring_dict["punishment_score"]
            Punishment_Score_list.append( (punishment_score, action) )
            #StateScore:
            state_score = scoring_dict["state_score"]
            State_Score_list.append( (state_score, action) )
            #reWard_list
            reward = scoring_dict["reward_list"]
            Reward_list.append( (total_score, action, reward) )
            

        Total_score_list = sorted(Total_score_list, reverse=True)
        Aggresive_Score_list_list = sorted(Aggresive_Score_list, reverse=True)
        Defense_Score_list = sorted(Defense_Score_list, reverse=True)
        Punishment_Score_list = sorted(Punishment_Score_list, reverse=False)
        State_Score_list = sorted(State_Score_list, reverse=True)
        Reward_list = sorted(Reward_list, reverse=True)

        print(whichPlayer+" Best Score List:")
        #print(Reward_list[0])

        return Total_score_list, Aggresive_Score_list, Defense_Score_list, Punishment_Score_list, State_Score_list



   
    
    # count enemy's choices index based on our function into dataframe
    def update_enemy_index_count_dataframe(self, opponent_action):
        #iterate through all types of score
        score_index = 0
        if self.game_round < self.IGNORE_ROUND-2:
            return

        score_row =[]
        for score_list in self.opponent_action_score_list:
            cur_score_name = self.score_names[score_index] #store which score are we looking at
            index=0  #Enemy Selection's index
            for pair in score_list:
                # Match an action, get its index
                if pair[1] == opponent_action:
                    # exclude potation random throw outlier
                    if self.EXCLUDE_THROW_DIST == True:
                        if pair[1][0] in "THROW":
                            # if is a throw, impute mean value
                            index = self.opponent_score_df[cur_score_name].mean()
                            break
                    break
                index+=1
            # print(self.enemy_action_dist_dict)
            # print(calculate_normal_probability(index, self.enemy_action_dist_dict[cur_score_name]))
            # input("asdas")

             # not enough data, add directly
            if (len(self.opponent_score_df[cur_score_name])<30):
                score_row.append(index)
            else:
                #Excluding Potential Outlier and add index to dataframe's column
                if calculate_normal_probability(index, self.enemy_action_dist_dict[cur_score_name]) > (1-self.CONFIDENCE_LEVEL*5):
                    score_row.append(index)
                else:
                    score_row.append(self.opponent_score_df[cur_score_name].mean())
            score_index += 1
        
        #updating dataframe
        if (self.opponent_action_score_list):
            self.opponent_score_df = self.opponent_score_df.append({"Total_Score_Index":score_row[0],
                                            "Aggresive_Index":score_row[1],
                                            "Defense_Index":score_row[2],
                                            "Punishment_Index":score_row[3],
                                            "State_Score_Index":score_row[4]},ignore_index=True) 

        # Updating Distribution
        for name in self.score_names:
            self.enemy_action_dist_dict[name]["mean"] = self.opponent_score_df[name].mean()
            if (len(self.opponent_score_df[name]) > self.IGNORE_ROUND):
                self.enemy_action_dist_dict[name]["std"] = self.opponent_score_df[name].std()


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


def add_next_action_to_play_dict(state, player, action):
    """
    This function copy the previous state and add action on the new board and return the new
    state 
    """
    # copy the previous state
    new_state = deepcopy(state)

    if action[0] in "THROW":
        #If throw, add a symbol onto board
        symbol_type = action[1]
        location = action[2]
        new_state.play_dict[player][symbol_type].append(location)
        #reduce available throw times by 1
        if player == "opponent":
            new_state.enemy_throws_left -= 1
        else:
            new_state.throws_left -= 1
    else:
        move_from = action[1]
        symbol_type = get_symbol_by_location(player, new_state.play_dict, move_from)
        move_to = action[2]
        # move token from start to end, simply update play_dict

        # move the token by adding new position and remove old one
        new_state.play_dict[player][symbol_type].remove(move_from)
        new_state.play_dict[player][symbol_type].append(move_to)
    return new_state
