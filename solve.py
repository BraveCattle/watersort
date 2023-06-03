from game import Game
from utils import *

solution = []

def useless(t1, t2):
    if t1.contains.count(t1.contains[0]) == len(t1.contains) and t2.empty():
        return True
    return False

def solve(myGame, step):
    # print("searching at step:", step)
    # print("current solution:", solution)
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
            if check_pour(tube1, tube2) and (not useless(tube1, tube2)):
                pour(tube1, tube2)
                solution.append((idx1, idx2))
                
                solve(myGame, step+1)
                
                revoke(myGame)
                solution.pop(-1)

myGame = Game()
solve(myGame, 0)