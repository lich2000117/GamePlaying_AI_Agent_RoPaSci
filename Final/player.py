from Final.util import Init_throw_range, add_action_to_play_dict, eliminate_and_update_board

from Final.prediction import *
from Final.learning import temporal_difference_learning
import numpy as np
import collections

class Player:
    
    
    def __init__(self, player):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.
        The parameter player is the string "upper" (if the instance will
        play as Upper), or the string "lower" (if the instance will play
        as Lower).
        """
        self.ITERATION = 50
        self.STEP_LOOK_AHEAD = 0
        self.TEMPORAL_DIFF_LEARNING = False
        self.GREEDY_PREDICT = True
        self.EXCLUDE_THROW_DIST = True
        self.ANALYSIS_MODE = True
        self.AVOID_DRAW = True   # if algorithm break tie automatically
        self.REFINED_THROW = True   # if using advanced random throw strategy
        self.CONFIDENCE_LEVEL = 0.05   #confidence level to exclude outliers into distribution
        self.IGNORE_ROUND = 5  # ignore first 5 rounds when doing probability predicting
        
        self.Our_Eval_Weight = {
            "aggresive":1,
            "defensive":1,
            "prefer_throw":1,
            "other":1
        }
        
        self.Enemy_Eval_Weight = {
            "aggresive":1,
            "defensive":1,
            "prefer_throw":1,    # the enemy's preference of throw elimination or slide elimination
            "other":1
        }
        # Parameters to adjust Enemy Evaluation Function's Weight
        self.STEP_ATK_SCALE = 0.2  # aggresiveness of enemy
        self.STEP_DEF_SCALE = 0.2  # defensiveness of enemy
        self.STEP_THROW_RATE = 0.5  # if enemy prefers throw more
        
        self.enemy_aggresive_action_score = {}
        self.enemy_defensive_action_score = {}

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
        self.opponent_score_array = np.array(0)
        self.enemy_action_dist_dict = {}
        self.predicted_enemy_action = ()
        self.corrected_predict = 0
        self.total_predict = 0
        self.predict_accuracy = 0.0
        
        

        # Store history to Check Draw Game
        self.history = collections.Counter({self._snap(): 1})
        self.cur_snap_used_action_index = {}  # a dictionary that stores previous state to avoid draw
            # {state1: 0,1,2}   at state1 used action at index 0, 1 and 2, so next time starting from 3
        self.states_list = []   # used to store states happen in the past turn, a list of State object



    def action(self):
        
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        # Get Enemy Action's Probability and return the mean index using "Total Score"
        # hard code the first three rounds to lay out my defensive 
        if self.game_round <= 3:
            player_best_action = open_game_stragety(self)
        else:
            ### No1. First Prediction
            predict_next_enemy_action(self)
            
            # No2. predict enemy's prediction based on our next step
            # look how many turns we look ahead
            i = 0
            while ((i<self.STEP_LOOK_AHEAD)):
                # choose best option for us if considering enemy's next action
                player_total_score_list = getScoredActionList(self, "player", self.predicted_enemy_action)
                # Predict Enemy's action based on our next action
                predict_next_enemy_action(self, player_total_score_list[0][1])
                i+=1
                
            # get our action based on predicted enemy's action
            player_total_score_list = getScoredActionList(self, "player", self.predicted_enemy_action)
            
            # Check Repeated State
            # Avoid Draw Situation, take another action without using already used indexes checked by default dict
            cur_snap = self._snap()
            if (self.AVOID_DRAW):
                player_best_action = draw_avoid_best_action(self,player_total_score_list, cur_snap)
            else:
                player_best_action = player_total_score_list[0][1]
            print("\nPLayer's best action")
            print(player_total_score_list[0])
            print("\nEnemy's best action")
            if self.opponent_action_score_list:
                print(self.opponent_action_score_list[0])
            print("\n==================================================================\n")
            
        return player_best_action
            

        
    
    def update(self, opponent_action, player_action):
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """
        # Learning from prev enemy strategy 
        LearnEnemyStrategy(self,opponent_action)
        
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
        if (self.ANALYSIS_MODE):
            if (self.game_round>self.IGNORE_ROUND+1):
                array = self.opponent_score_array
                # dist.agg(['min', 'max', 'mean', 'std']).round(decimals=2)
                print("\n Enemy Index Mean:")
                print(np.mean(array))
                print("\n Enemy Index STD:")
                print(np.std(array))
                print("\nAccuracy of Prediction:")
                if self.total_predict:
                    print(round(self.corrected_predict/self.total_predict,3))
                print("\nEnemy Weight:")
                print(self.Enemy_Eval_Weight)
                print("````````````````````````````````predicted_action````````````````````````````````")
                print(self.predicted_enemy_action)
                print("````````````````````````````````actual _action````````````````````````````````")
                print(opponent_action)
        #input("")
    
    def _snap(self):
        """
        Capture the current play state in a hashable way
        (for repeated-state checking)
        reference: referee/game.py from Melbourne Uni AI Tutor's code
        """
        play_history = []
        enemy_token_num = []  #(2,4,1) represents 2 rocks, 4 paper, 2 scissors
        for key, coor in self.play_dict["opponent"].items():
            enemy_token_num.append(len(coor))
        for i in "rps":
            play_history.append(tuple(sorted(self.play_dict["player"][i])))
            #play_history.append(tuple(sorted(self.play_dict["opponent"][i])))
        return (tuple(enemy_token_num),tuple(play_history),
            # with the same number of throws remaining for each player
            self.throws_left,
            self.enemy_throws_left,
        )




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