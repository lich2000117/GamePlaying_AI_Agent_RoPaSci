## This File auto matically play games and compute win rate
import subprocess
import os
import sys
import argparse

PLAY_TIMES = 200
PLAYER1 = 'IG'
PLAYER2 = 'Enemy'



# A testing program
def test_program(PLAY_TIMES):
    upper_wins = 0
    lower_wins = 0
    draws = 0
    timeout_draws = 0
    i = PLAY_TIMES
    while (i):
        #Call commandline argument without getting its output
        #with open(os.devnull, "w") as f:
            #convert output to string
        output = ""
        try:
            output = subprocess.check_output(['python3', '-m', 'referee', PLAYER1, PLAYER2]).decode(sys.stdout.encoding)
        except:
            output = subprocess.check_output(['python', '-m', 'referee', PLAYER1, PLAYER2]).decode(sys.stdout.encoding)

        # get only last line of output
        result = output.splitlines()[-1]

        # count wining times
        if "upper" in result:
            upper_wins += 1
        elif "lower" in result:
            lower_wins += 1
        elif "draw" in result:
            # if draw because of both side has invincible symbol
            if "both" in result:
                draws += 1
            else:
                timeout_draws += 1
        else:
            print(output + " \n\n^^^^^^^^^^^^\nBUG Occurs!, \nMatch Detail above\n^^^^^^^^^^^^")
            return
        i -= 1
    print("Total Plays: ", PLAY_TIMES)
    print("Upper Win Rate:", round(upper_wins/PLAY_TIMES,2))
    print("Lower Win Rate:", round(lower_wins/PLAY_TIMES,2))
    print("Draw Rate:", round(draws/PLAY_TIMES,2))
    print("Timeout Rate:", round(timeout_draws/PLAY_TIMES,2))


test_program(PLAY_TIMES)


