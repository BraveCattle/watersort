import pygame

class Tube(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        # This could also be an image loaded from the disk.
        self.image = pygame.image.load("./sources/tube.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.pos = (pos_x, pos_y)
        self.image = pygame.transform.smoothscale(self.image,(self.rect[2]//2,self.rect[3]//2))
        self.contains = []

def main():
    pygame.init()
    pygame.display.set_caption('water sort')
    window = pygame.display.set_mode((1000, 600))
    # objects added later are on top of layers of objects added earlier
    tubes = [Tube(200, 30), Tube(400, 30), Tube(600, 30), Tube(300, 330), Tube(500, 330)]
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        for tube in tubes:
            window.blit(tube.image, tube.pos)
        pygame.display.flip()


if __name__ == '__main__':
    main()