## This File auto matically play games and compute win rate
import subprocess
import os
import sys

# config --------------------------------------------------------------------------------------
PLAY_TIMES = 1000   # Match Times
UPPER = 'IG'   # upper
LOWER = 'RandomEnemy'    # lower
SHOW_BUG_MATCH = True  # show match detail of a bugged match
SHOW_TIMEOUT_MATCH = True  # show match detail of a timed out match
# config --------------------------------------------------------------------------------------





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
            output = subprocess.check_output(['python3', '-m', 'referee', UPPER, LOWER]).decode(sys.stdout.encoding)
        except:
            output = subprocess.check_output(['python', '-m', 'referee', UPPER, LOWER]).decode(sys.stdout.encoding)

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
                if SHOW_TIMEOUT_MATCH:
                    print(output + " \n\n^^^^^^^^^^^^\nTIMEOUT Match Occurs!, \nMatch Detail above\n^^^^^^^^^^^^")
                    return
                timeout_draws += 1
        else:
            if SHOW_BUG_MATCH:
                print(output + " \n\n^^^^^^^^^^^^\nBUG Occurs!, \nMatch Detail above\n^^^^^^^^^^^^")
            return
        i -= 1
    print("Total Plays: ", PLAY_TIMES)
    print("Upper Win Rate:", round(upper_wins/PLAY_TIMES,2))
    print("Lower Win Rate:", round(lower_wins/PLAY_TIMES,2))
    print("Draw Rate:", round(draws/PLAY_TIMES,2))
    print("Timeout Rate:", round(timeout_draws/PLAY_TIMES,2))


test_program(PLAY_TIMES)


