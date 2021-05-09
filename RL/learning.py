from RL.state_evaluation import board_count, hostile_token_in_throw_range, token_in_enemy_throw_range
from RL.state_evaluation import state_evaluation
from math import tanh, cosh, sinh

def temporal_difference_learning(states_list, w):
    beta = 0.01
    function_list = [board_count, hostile_token_in_throw_range, token_in_enemy_throw_range]
    update_w = []
    print("Enter TD lambda learning")
    for i in range(0, len(w)):
        error_term = 0
        # w[i] is the parameter we want to learn
        for j in range(0, len(states_list)-1):
            current_state = states_list[j]
            next_state = states_list[j+1]

            cur_value = state_evaluation(current_state)
            next_value = state_evaluation(next_state)

            diff = tanh(cur_value) - tanh(next_value)
            derivatives = ( cosh(cur_value)**2 - sinh(cur_value)**2 ) / cosh(cur_value)**2 
            derivatives *= function_list[i](current_state)
            error_term += derivatives * diff
            print("Error term for weight", i, " is ", error_term)
        
        # update error to w[i]
        update_w_i = w[i] + beta*error_term
        update_w.append(update_w_i)

    return update_w

