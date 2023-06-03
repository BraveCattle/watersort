import pygame
import argparse
from utils import *
from game_config import *
from color import Color
import time

class Tube(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, contains):
        super().__init__()
        self.rect = (pos_x, pos_y, TUBE_WIDTH, TUBE_HEIGHT)
        self.contains = contains

    def full(self):
        if len(self.contains) == 4:
            return True
        return False
    
    def empty(self):
        if len(self.contains) == 0:
            return True
        return False

class Button(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, source, func):
        super().__init__()
        self.rect = (pos_x, pos_y, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.image = pygame.image.load(source).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (self.rect[2], self.rect[3]))
        self.func = func

class Game():
    def __init__(self, puzzle_file = 'puzzle_state.txt'):
        pygame.init()
        pygame.display.set_caption('water sort')
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        self.colors = load_puzzle(puzzle_file)
        # print(self.colors)

        self.tubes = [Tube(90, 30, self.colors[0]), Tube(200, 30, self.colors[1]), 
                      Tube(310, 30, self.colors[2]), Tube(420, 30, self.colors[3]),
                      Tube(530, 30, self.colors[4]), Tube(640, 30, self.colors[5]),
                      Tube(750, 30, self.colors[6]),
                      Tube(90, 330, self.colors[7]), Tube(200, 330, self.colors[8]), 
                      Tube(310, 330, self.colors[9]), Tube(420, 330, self.colors[10]),
                      Tube(530, 330, self.colors[11]), Tube(640, 330, []),
                      Tube(750, 330, [])]
        self.num_tubes = len(self.tubes)
        self.record = []

        self.buttons = [Button(880, 60, "./sources/revoke.png", revoke)]
        
        # tube_anime: index -> (remaining frames, move direction/distance)
        self.tube_anime = {i:(0, 0) for i in range(len(self.tubes))}
        self.holding_tube = None
        self.holding_tube_idx = -1
        self.click_tube = None
        self.click_tube_idx = -1
        self.click_button = None
        self.game_end = False

    def run(self):
        running = True
        while running:
            # play the remaining animes
            play_anime(self.tubes, self.tube_anime)

            # if game ends
            if check_end(self.tubes):
                self.game_end = True
                win_prompt(self)

            # get the events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if self.game_end:
                    continue

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.click_tube = None
                    self.click_tube_idx = -1
                    self.click_button = None
                    for idx, tube in enumerate(self.tubes):
                        if inside(event.pos, tube):
                            self.click_tube, self.click_tube_idx = tube, idx
                    for button in self.buttons:
                        if inside(event.pos, button):
                            self.click_button = button

                if event.type == pygame.MOUSEBUTTONUP:
                    # run the button command if clicked the button
                    if self.click_button and inside(event.pos, self.click_button):
                        self.click_button.func(self)

                    # run tube interactions if clicked the tubes
                    if self.click_tube and inside(event.pos, self.click_tube):
                        # print("clicked tube", click_tube_idx+1)

                        # cannot move if the tube is playing anime
                        if self.tube_anime[idx][0] > 0:
                            continue

                        # move the tube downward if it is held
                        if self.click_tube == self.holding_tube:
                            self.holding_tube = None
                            self.holding_tube_idx = -1
                            add_anime_down(self.click_tube_idx, self.tube_anime)

                        else:
                            if self.holding_tube:
                                volumn = pour(self.holding_tube, self.click_tube)
                                if volumn > 0:
                                    self.record.append((self.holding_tube_idx, self.click_tube_idx, volumn))
                                add_anime_down(self.holding_tube_idx, self.tube_anime)
                                self.holding_tube = None
                                self.holding_tube_idx = -1
                            else:
                                self.holding_tube = self.click_tube
                                self.holding_tube_idx = self.click_tube_idx
                                add_anime_up(self.click_tube_idx, self.tube_anime)

            if self.game_end:
                continue

            # draw the new window
            draw_window(self)
    
    def play_solution(self, solution_file):
        sol = []
        try:
            with open(solution_file, "r") as f:
                for line in f:
                    src, dst = line.rstrip('\n').split(' ')
                    sol.append((int(src), int(dst)))
        except Exception as e:
            print("File error!")
        
        start_time = time.time()
        round = 0
        interval = 0.8

        move_up, move_pour, move_down = False, False, False
        anime_ongoing = False
        running = True

        frame = 0

        while running:
            # frame += 1
            # print(frame)

            cur_time = time.time()

            if check_end(self.tubes):
                self.game_end = True
                win_prompt(self)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if self.game_end:
                continue

            if round < len(sol) and cur_time-start_time > interval*round:
                # print("round:", round)
                if not (move_up or move_pour or move_down):
                    add_anime_up(sol[round][0], self.tube_anime)
                    anime_ongoing = True
                    move_up = True

                if move_up and (not anime_ongoing) and (not move_down):
                    pour(self.tubes[sol[round][0]], self.tubes[sol[round][1]])
                    move_pour = True

                if move_up and move_pour and (not move_down):
                    add_anime_down(sol[round][0], self.tube_anime)
                    anime_ongoing = True
                    move_down = True

            anime_ongoing = play_anime(self.tubes, self.tube_anime)
            if (not anime_ongoing) and move_up and move_pour and move_down:                
                move_up, move_pour, move_down = False, False, False
                round += 1
            draw_window(self)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Play the water sort game.')
    parser.add_argument('-p', '--puzzle',
                        help='Specify the puzzle state file')
    parser.add_argument('-a', '--auto',
                        help='Play the solution automatically')
    
    args = parser.parse_args()

    if args.puzzle:
        print(args.puzzle)
        myGame = Game(args.puzzle)
    else:
        myGame = Game()
    
    if args.auto:
        myGame.play_solution(args.auto)
    else:
        myGame.run()