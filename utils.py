from color import Color
from game_config import *
import pygame

# util functions are implemented here

def load_puzzle(file):
    res = []
    try:
        with open(file, "r") as f:
            for line in f:
                col_str = line.rstrip("\n").replace(" ", "").split(',')
                res.append([Color[col].value for col in col_str][::-1])
    except Exception as e:
        print(e)

    col_flat = [col for tube in res for col in tube]
    for col in col_flat:
        if col_flat.count(col) != 4:
            print("Puzzle invalid!")
            return None
    return res


# check if a position (pos: (pos_x, pos_y)) is in a object (Tube()/Button())
def inside(pos, obj):
    if pos[0] < obj.rect[0] or pos[0] > obj.rect[0]+obj.rect[2]:
        return False
    if pos[1] < obj.rect[1] or pos[1] > obj.rect[1]+obj.rect[3]:
        return False
    return True

def draw_tube(tube, window):
    # draw the tube
    pygame.draw.rect(window, Color.GREY.value, tube.rect, TUBE_THICKNESS)

    # draw the colors in the tube
    for idx, col in enumerate(tube.contains):
        col_rect = (tube.rect[0]+TUBE_THICKNESS,
                    tube.rect[1]+TUBE_MARGIN+TUBE_THICKNESS+(3-idx)*COLOR_HEIGHT,
                    TUBE_WIDTH-2*TUBE_THICKNESS,
                    COLOR_HEIGHT)
        pygame.draw.rect(window, col, col_rect, 0)

def draw_window(game):
    game.window.fill(Color.BLACK.value)
    for button in game.buttons:
        game.window.blit(button.image, (button.rect[0], button.rect[1]))
    for tube in game.tubes:
        draw_tube(tube, game.window)
    pygame.display.flip()

def move_tube(tube, dir):
    tube.rect = (tube.rect[0], tube.rect[1]+dir, tube.rect[2], tube.rect[3])

def add_anime_down(idx, tube_anime):
    if not NO_ANIME:
        if tube_anime[idx][0] > 0:
            tube_anime[idx] = (TUBE_ANIME_TIME-tube_anime[idx][0], 1)
        else:
            tube_anime[idx] = (TUBE_ANIME_TIME, 1)

def add_anime_up(idx, tube_anime):
    if not NO_ANIME:
        if tube_anime[idx][0] > 0:
            tube_anime[idx] = (TUBE_ANIME_TIME-tube_anime[idx][0], -1)
        else:
            tube_anime[idx] = (TUBE_ANIME_TIME, -1)

# play num_frame frames of anime for tube
def tube_play_anime(tube, idx, tube_anime, num_frame):
    if (not NO_ANIME) and tube_anime[idx][0] > 0:
        move_tube(tube, tube_anime[idx][1]*num_frame)
        tube_anime[idx] = (tube_anime[idx][0]-num_frame, tube_anime[idx][1])

def play_anime(tubes, tube_anime):
    if not NO_ANIME:
        for idx, tube in enumerate(tubes):
            tube_play_anime(tube, idx, tube_anime, 0.1)
        for idx, tube in enumerate(tubes):
            if tube_anime[idx][0] > 0:
                return True
        return False
    else:
        return False

def check_pour(tube1, tube2):
    if tube1 == tube2:
        return False
    if tube2.full() or tube1.empty():
        return False
    if tube2.empty():
        return True
    if tube1.contains[-1] == tube2.contains[-1]:
        return True
    return False

def pour(tube1, tube2):
    volumn = 0
    for t in range(4):
        if tube2.empty():
            if tube1.empty():
                break
            else:
                tube2.contains.append(tube1.contains[-1])
                tube1.contains.pop(-1)
                volumn += 1
        else:
            if tube1.empty():
                break
            if tube2.contains[-1] == tube1.contains[-1] and len(tube2.contains) < 4:
                tube2.contains.append(tube1.contains[-1])
                tube1.contains.pop(-1)
                volumn += 1
    return volumn

def force_pour(t1, t2, volumn, tubes):
    # print("force pouring from tube:", t1, "to tube:", t2, "with volumn", volumn)
    try:
        for i in range(volumn):
            tubes[t2].contains.append(tubes[t1].contains[-1])
            tubes[t1].contains.pop(-1)
    except:
        print("Force pour error!")

def check_end(tubes):
    for tube in tubes:
        if not (tube.full() or tube.empty()):
            return False
        for col_idx in range(len(tube.contains)-1):
            if tube.contains[col_idx] != tube.contains[col_idx+1]:
                return False
    return True

def revoke(game):
    if len(game.record) == 0:
        print("Cannot revoke!")
        return None
    print("rovoking from tube:", game.record[-1][1], "to tube:", game.record[-1][0])
    force_pour(game.record[-1][1], game.record[-1][0], game.record[-1][2], game.tubes)
    game.record.pop(-1)

def win_prompt(game):
    font_obj = pygame.font.Font('freesansbold.ttf', 32)
    text_surf = font_obj.render('You win!!!', True, Color.RED.value, Color.GREY.value)
    text_rect_obj = text_surf.get_rect()
    text_rect_obj.center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2)
    game.window.blit(text_surf, text_rect_obj)
    pygame.display.update()
