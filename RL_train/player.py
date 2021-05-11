from RL_train.util import Init_throw_range, add_action_to_play_dict, eliminate_and_update_board, calculate_normal_probability, get_symbol_by_location
from RL_train.action import get_all_valid_action
from RL_train.state import State
from RL_train.action_evaluation import defensive_action_evaluation, action_evaluation
from copy import copy, deepcopy
import random
import csv
from RL_train.learning import temporal_difference_learning
import math
import os
# python3 -m referee RL_train GreedyEnemy

class Player:
    
    def __init__(self, player):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.
        The parameter player is the string "upper" (if the instance will
        play as Upper), or the string "lower" (if the instance will play
        as Lower).
        """
        self.IGNORE_ROUND = 5  # ignore first 5 rounds when doing probability predicting
        self.beta = 0.2      
        self.episilon = 0

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
        self.states_list = []

    
    def action(self):
        
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        # hard code the first three rounds to lay out my defensive 
        if self.game_round <= 3:
            return open_game_stragety(self)
        else:
            action_evaluation_list = []
            new_state = State(deepcopy(self.play_dict), deepcopy(self.throws_left),
                            deepcopy(self.enemy_throws_left), deepcopy(self.side))
            action_list = get_all_valid_action(new_state, "player")
            for action in action_list:
                action_evaluation_list.append( (action_evaluation(new_state, action), action) )
            action_evaluation_list = sorted(action_evaluation_list, reverse=True)
            # for action in action_evaluation_list:
            #     print(action)
            die_num = 0
            die_num = random.uniform(0,1)
            if die_num < self.episilon:
                random_action = random.choice(action_evaluation_list)
                print("random action: ", random_action)
                # input("Pause")
                return random_action[1]
            else:
                print("greedy action: ", action_evaluation_list[0])
                input("Pause")
                return action_evaluation_list[0][1]
            
           

    
    def update(self, opponent_action, player_action):
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """
        # count enemy's choices index based on our function into array

        # do not calculate elimination now, just update symbols to play_dict
        # add each player's action to board for the reason of synchronising play.
        # if throw, also reduce throws left by 1
        add_action_to_play_dict(self, "opponent", opponent_action)
        add_action_to_play_dict(self, "player", player_action)
        # update self representation of the game
        # Calculate eliminations and update
        # after token actions, check if eliminate other tokens by following function
        eliminate_and_update_board(self,self.target_dict)
        new_state = State(copy(self.play_dict), copy(self.throws_left),
                            copy(self.enemy_throws_left), copy(self.side))
        self.states_list.append(new_state)
        pre_w = []
        if (self.game_round >= 2):
            if os.stat("RL_train/weights.csv").st_size == 0:
                pre_w = [10, 5, -5, 1, -1, 2, 3, -2, -3]
            else:
                with open("RL_train/weights.csv") as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    row = next(csv_reader)
                    pre_w = []
                    for num in row:
                        pre_w.append(float(num))
            # print("Previous weight: ", pre_w)
            update_w = temporal_difference_learning(self.states_list, pre_w, self.beta) 
            # print("Weights after update: ", update_w) 
            # input("___________")   
            # input("Press enter to continue!")                   
            with open('RL_train/weights.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(update_w)

        self.game_round += 1
        


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



