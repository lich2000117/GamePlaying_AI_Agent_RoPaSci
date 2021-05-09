from RL.util import Init_throw_range, add_action_to_play_dict, eliminate_and_update_board
from RL.action import get_all_valid_action
from RL.action_evaluation import action_evaluation
from RL.state import State
from RL.random_algorithms import refined_random_throw, random_throw, random_action, get_current_player_nodes_count
from copy import copy
import csv
from RL.learning import temporal_difference_learning
import os

class Player:
    
    
    def __init__(self, player):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.
        The parameter player is the string "upper" (if the instance will
        play as Upper), or the string "lower" (if the instance will play
        as Lower).
        """
        self.BREAK_TIE = False   # if algorithm break tie automatically
        self.REFINED_THROW = True   # if using advanced random throw strategy

        self.game_round = 1
        self.throws_left = 9   # reduced by 1 after each throw in util/add_action_board function
        self.enemy_throws_left = 9
        self.side = player
        
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
        self.states_list = []   # used to store states happen in the past turn, a list of State object



    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        
        # if reached same game state three times, break the tie
        if (self.same_state_count >= 3) and (self.BREAK_TIE):
            # break tie by random throw
            if (self.throws_left>0):
                print("\n^^^^^^^^^^^^^^BREAKING TIE, THROW^^^^^^^^^^^^^^^\n")
                if (self.REFINED_THROW):
                    return refined_random_throw(self, self.REFINED_THROW)
                else:
                    return random_throw(self)
            else:
                # break tie by random move
                return random_action(self)


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
            #print(action_evaluation_list[0])
            print("RL:")
            print("chosen move for RL:")
            print(action_evaluation_list[0])
            #input("Press Enter to continue\n")
            return action_evaluation_list[0][1]
            

        
    
    def update(self, opponent_action, player_action):
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """
        #Check Repeated Game State, get previous game state:
        prev_game_state = (get_current_player_nodes_count(self, "player"), get_current_player_nodes_count(self, "opponent"))
        # do not calculate elimination now, just update symbols to play_dict
        # add each player's action to board for the reason of synchronising play.
        # if throw, also reduce throws left by 1


        # store state into a file 
        
        
        add_action_to_play_dict(self, "opponent", opponent_action)
        add_action_to_play_dict(self, "player", player_action)

        # update self representation of the game
        # Calculate eliminations and update
        # after token actions, check if eliminate other tokens by following function
        eliminate_and_update_board(self,self.target_dict)
        self.game_round += 1

        new_state = State(copy(self.play_dict), copy(self.throws_left),
                                 copy(self.enemy_throws_left), copy(self.side))
        self.states_list.append(new_state)

        if self.game_round >= 4:
            if os.stat("RL/weights.csv").st_size == 0:
                pre_w = [10, 5, -5]
            else:
                with open("RL/weights.csv") as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    row = next(csv_reader)
                    pre_w = []
                    for num in row:
                        pre_w.append(float(num))
                print("Previous weight: ", pre_w)
                update_w = temporal_difference_learning(self.states_list, pre_w) 
                print("Weights after update: ", update_w)                       
                with open('protagonist.csv', 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(update_w)
        

        input("\nPress enter to continue! ")
        #Check Repeated Game State:
        cur_game_state = (get_current_player_nodes_count(self, "player"), get_current_player_nodes_count(self, "opponent"))
        if cur_game_state == prev_game_state:
            self.same_state_count += 1
        else:
            self.same_state_count = 0


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
