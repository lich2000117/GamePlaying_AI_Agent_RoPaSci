def getScoredActionList(self, whichPlayer, Enemy_Next_Action=None):
        """
        Get Sorted List Based on Scoring Function,
        Can Use to get Opponent's score list,
        return one list: Total_score_list
        """

        # Check if using on ourside or predicting enemy
        if (whichPlayer == "player"):
            side = self.side
            prev_state = State(copy(self.play_dict), copy(self.throws_left),
                                copy(self.enemy_throws_left), copy(side))
        else:
            if self.side == "upper":
                #Reverse throws_left and enemy_throws_left for enemy evaluation
                prev_state = State(copy(self.play_dict), copy(self.enemy_throws_left),
                                copy(self.throws_left), "lower")
            else:
                #Reverse throws_left and enemy_throws_left for enemy evaluation
                prev_state = State(copy(self.play_dict), copy(self.enemy_throws_left),
                                copy(self.throws_left), "upper")
            

        action_list = get_all_valid_action(whichPlayer, prev_state)
        next_state = prev_state
        # add enemy next action into state, but do not calculate elimination
        if Enemy_Next_Action:
            next_state = add_next_action_to_play_dict(prev_state, "opponent", Enemy_Next_Action)
            #eliminate_and_update_board(next_state, prev_state.target_dict)
            
        if ((self.ANALYSIS_MODE) and (whichPlayer == "player")):
            print("````````````````````````````````Enemy_Next_Action````````````````````````````````")
            print(Enemy_Next_Action)
        # Get Score List
        Total_score_list = []
        for action in action_list:
            scoring_dict = action_evaluation(whichPlayer, next_state, action)
            total_score = scoring_dict["total_score"]
            reward = scoring_dict["reward_list"]#reWard_list
            Total_score_list.append( (total_score, action, reward) )
        # Sort to choose highest score
        Total_score_list = sorted(Total_score_list, reverse=True)

        Total_score_list_with_prob = []
        for i in range(0,len(Total_score_list)):
            prob = calculate_normal_probability(i, self.opponent_score_array)
            Total_score_list_with_prob.append(tuple((Total_score_list[i][0], Total_score_list[i][1], prob, Total_score_list[i][2]))) 
            
        return Total_score_list_with_prob


    def update_accuracy_of_prediction(self, opponent_action):
        """ Get the accuracy of our prediction"""
        if self.predicted_enemy_action:
            self.total_predict += 1
            if (self.predicted_enemy_action == opponent_action):
                self.corrected_predict += 1
                # Keep Track of prediction accuracy
        if (self.total_predict):
            self.predict_accuracy = round(self.corrected_predict/self.total_predict,3)

    def update_next_enemy_action(self, predict_index):
        """update enemy's next action into player class"""
        # always greedy predict enemy
        if (self.GREEDY_PREDICT):
            self.predicted_enemy_action = self.opponent_action_score_list[0][1]  
        else:
            # hard coding, get Next Enemy Action without using probability
            if (len(self.opponent_action_score_list) > predict_index):
                predicted_enemy_action = self.opponent_action_score_list[predict_index][1]
            else:
                predicted_enemy_action = self.opponent_action_score_list[0][1]
        return predicted_enemy_action

    def draw_avoid_best_action(self, player_total_score_list, cur_snap):
        """Avoid Draw Situation, take another action without using already used indexes checked by default dict"""
        self.cur_snap_used_action_index[cur_snap] += 1
        next_index = self.cur_snap_used_action_index[cur_snap]
        if next_index<len(player_total_score_list):
            return player_total_score_list[next_index][1]
        return player_total_score_list[random.randint(0,12)][1]
        

    

    def select_enemy_next_index(self):
        """select most likely enemy's action"""
        selected_index = 0
        array = self.opponent_score_array
        # Select The Score we want to use to evaluate enemy's action
        # Selecting Least Standard Deviation one
        if np.size(array)==1:
            selected_index = 0
        else:
            selected_mean = np.mean(array)
            selected_index = int(round(selected_mean))
        if (self.ANALYSIS_MODE):
            print("``````````````````````````````````````````")
            print("selected_enemy_index")
            print(selected_index)
            print("``````````````````````````````````````````")
        return selected_index


   
    
    # count enemy's choices index based on our function into dataframe
    def record_enemy_action_index(self, opponent_action):
        #iterate through all types of score
        score_array = self.opponent_score_array
        index_to_add = 0
        score_list = self.opponent_action_score_list
        
        for index in range(0, len(score_list)):
            cur_pair = self.opponent_action_score_list[index]
            if cur_pair[1] == opponent_action:
                # exclude potation random throw outlier, using mean value
                if self.EXCLUDE_THROW_DIST == True:
                    if cur_pair[1][0] in "THROW":
                        index = self.opponent_score_array.mean()
                        break
                break
        # not enough data, add mean value
        if (np.size(score_array)<30):
            index_to_add = index
        else:
            #Excluding Potential Outlier and add mean value
            if calculate_normal_probability(index, score_array) > (1-self.CONFIDENCE_LEVEL*5):
                index_to_add = index
            else:
                index_to_add = score_array.mean()
        # add to action array
        self.opponent_score_array = np.append(score_array, index)

