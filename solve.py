from game import Game
from utils import *
import sys

sys.setrecursionlimit(5000000)

state_dict = {}
solution = []

def get_hash(tubes):
    state = ""
    for tube in tubes:
        cnt = 0
        for col in tube.contains:
            state += Color(col).name
            cnt += 1
        while cnt < 4:
            state += 'AIR'
            cnt += 1
    return hash(state)

def full_pour_to_empty(tube1, tube2):
    if tube1.contains.count(tube1.contains[0]) == len(tube1.contains) and tube2.empty():
        return True
    return False

def solve(myGame, step):
    # print("searching at step:", step)
    # print("current solution:", solution)
    cur_state_hash = get_hash(myGame.tubes)
    if cur_state_hash in state_dict:
        return
    state_dict[cur_state_hash] = 1

    if check_end(myGame.tubes):
        print("Find a solution in", step, "steps!")
        with open("solution.txt", "w") as f:
            result = ""
            for src, dst in solution:
                result += str(src)+" "+str(dst)+"\n"
            f.write(result)
        exit(0)
    
    for idx1, tube1 in enumerate(myGame.tubes):
        if tube1.empty():
            continue
        for idx2, tube2 in enumerate(myGame.tubes):
            # only search valid actions and useful actions
            if check_pour(tube1, tube2) and (not full_pour_to_empty(tube1, tube2)):
                volumn = pour(tube1, tube2)
                myGame.record.append((idx1, idx2, volumn))
                solution.append((idx1, idx2))
                
                solve(myGame, step+1)
                
                revoke(myGame)
                solution.pop(-1)

myGame = Game()
solve(myGame, 0)