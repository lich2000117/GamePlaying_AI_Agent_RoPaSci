from RL_train.state_evaluation import board_count, enemy_token_in_danger, token_in_danger
from RL_train.state_evaluation import token_on_board, enemy_token_on_board
from RL_train.state_evaluation import mean_distance_to_attack, min_distance_to_attack, mean_distance_to_defense, min_distance_to_defense
from RL_train.state_evaluation import state_evaluation
from math import tanh, cosh, sinh

def temporal_difference_learning(states_list, w, beta):
    function_list = [board_count, enemy_token_in_danger, token_in_danger,
                    token_on_board, enemy_token_on_board, mean_distance_to_attack, min_distance_to_attack,
                    mean_distance_to_defense, min_distance_to_defense]
    update_w = []
    # print("Enter TD lambda learning")
    
    for i in range(0, len(w)):
        error_term = 0
        # w[i] is the parameter we want to learn
        for j in range(0, len(states_list)-1):
            current_state = states_list[j]
            next_state = states_list[j+1]

            cur_value = state_evaluation(current_state)
            next_value = state_evaluation(next_state)
            # print("Current state value: ", cur_value)
            # print("Next state value: ", next_value)

            diff = tanh(cur_value) - tanh(next_value)
            # print("diff: ", diff)
            derivatives = ( cosh(cur_value)**2 - sinh(cur_value)**2 ) / cosh(cur_value)**2 
            # print("first derivatives: ", derivatives)
            derivatives *= function_list[i](current_state)
            # print("Second derivatives: ", derivatives)
            # print("value: ", function_list[i](current_state), end='')
            error_term += derivatives * diff
        # print("Error term for weight", i, " is ", error_term)
        
        # update error to w[i]
        update_w_i = w[i] + beta*error_term
        update_w.append(update_w_i)

    return update_w

