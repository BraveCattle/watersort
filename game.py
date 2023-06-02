import pygame

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600

TUBE_WIDTH = 100
TUBE_HEIGHT = 250
TUBE_THICKNESS = 5
COLOR_HEIGHT = int(2*(TUBE_HEIGHT-TUBE_THICKNESS*2)/9)
TUBE_MARGIN = TUBE_HEIGHT-TUBE_THICKNESS*2-4*COLOR_HEIGHT
TUBE_MOVE = 20

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GREY = (163, 163, 163)
BLACK = (0, 0, 0)

class Tube(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, contains):
        super().__init__()
        self.rect = (pos_x, pos_y, TUBE_WIDTH, TUBE_HEIGHT)
        self.thickness = TUBE_THICKNESS
        self.contains = contains

    def full(self):
        if len(self.contains) == 4:
            return True
        return False
    
    def empty(self):
        if len(self.contains) == 0:
            return True
        return False

# check if a position is in a tube
def inside(pos, tube):
    if pos[0] < tube.rect[0] or pos[0] > tube.rect[0]+tube.rect[2]:
        return False
    if pos[1] < tube.rect[1] or pos[1] > tube.rect[1]+tube.rect[3]:
        return False
    return True

def draw_tube(tube, window):
    # draw the tube
    pygame.draw.rect(window, GREY, tube.rect, tube.thickness)

    # draw the colors in the tube
    for idx, col in enumerate(tube.contains):
        col_rect = (tube.rect[0]+tube.thickness,
                    tube.rect[1]+TUBE_MARGIN+TUBE_THICKNESS+(3-idx)*COLOR_HEIGHT,
                    TUBE_WIDTH-2*TUBE_THICKNESS,
                    COLOR_HEIGHT)
        pygame.draw.rect(window, col, col_rect, 0)

def play_anime_down(idx, tube_anime):
    tube_anime[idx] = (TUBE_MOVE, 1)

def play_anime_up(idx, tube_anime):
    tube_anime[idx] = (TUBE_MOVE, -1)

def move_tube(tube, dir):
    tube.rect = (tube.rect[0], tube.rect[1]+dir, tube.rect[2], tube.rect[3])

def check_pour(tube1, tube2):
    if tube2.full() or tube1.empty():
        return False
    if tube2.empty():
        return True
    if tube1.contains[-1] == tube2.contains[-1]:
        return True
    return False

def pour(tube1, tube2):
    for t in range(4):
        if tube2.empty():
            if tube1.empty():
                break
            else:
                tube2.contains.append(tube1.contains[-1])
                tube1.contains.pop(-1)
        else:
            if tube1.empty():
                break
            if tube2.contains[-1] == tube1.contains[-1] and len(tube2.contains) < 4:
                tube2.contains.append(tube1.contains[-1])
                tube1.contains.pop(-1)

def check_end(tubes):
    for tube in tubes:
        if not (tube.full() or tube.empty()):
            return False
        for col_idx in range(len(tube.contains)-1):
            if tube.contains[col_idx] != tube.contains[col_idx+1]:
                return False
    return True

def main():
    pygame.init()
    pygame.display.set_caption('water sort')
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    colors = [[RED, GREEN, GREEN, BLUE], 
              [BLUE, GREEN, RED, RED],
              [RED, BLUE, GREEN, BLUE]]
    tubes = [Tube(200, 30, colors[0]), Tube(400, 30, colors[1]),
             Tube(600, 30, colors[2]), Tube(300, 330, []), Tube(500, 330, [])]
    
    running = True
    # tube_anime: index -> (remaining frames, move direction)
    tube_anime = {i:(0, 0) for i in range(len(tubes))}
    holding_tube = None
    holding_tube_idx = -1
    click_tube = None
    click_tube_idx = -1
    game_end = False

    while running:
        for idx, tube in enumerate(tubes):
            if tube_anime[idx][0] > 0:
                move_tube(tube, tube_anime[idx][1])
                tube_anime[idx] = (tube_anime[idx][0]-1, tube_anime[idx][1])

        if check_end(tubes):
            game_end = True
            font_obj = pygame.font.Font('freesansbold.ttf', 32)
            text_surf = font_obj.render('You win!!!', True, RED, GREY)
            text_rect_obj = text_surf.get_rect()
            text_rect_obj.center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2)
            window.blit(text_surf, text_rect_obj)
            pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_end:
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                click_tube = None
                for idx, tube in enumerate(tubes):
                    if inside(event.pos, tube):
                        click_tube, click_tube_idx = tube, idx

            if event.type == pygame.MOUSEBUTTONUP:
                if click_tube and inside(event.pos, click_tube):
                    print("clicked tube", click_tube_idx+1)
                    # cannot move if the tube is playing anime
                    if tube_anime[idx][0] > 0:
                        continue

                    # move the tube downward if it is held
                    if click_tube == holding_tube:
                        holding_tube = None
                        holding_tube_idx = -1
                        play_anime_down(click_tube_idx, tube_anime)

                    else:
                        if holding_tube:
                            pour(holding_tube, click_tube)
                            play_anime_down(holding_tube_idx, tube_anime)
                            holding_tube = None
                            holding_tube_idx = -1
                        else:
                            holding_tube = click_tube
                            holding_tube_idx = click_tube_idx
                            play_anime_up(click_tube_idx, tube_anime)

        if game_end:
            continue

        window.fill(BLACK)
        for tube in tubes:
            draw_tube(tube, window)
        pygame.display.flip()


if __name__ == '__main__':
    main()