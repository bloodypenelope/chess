from client.game.configs import WINDOW_SIZE
from game.game import Chess
import pygame


def main():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)

    chess = Chess(screen)
    chess.main_loop()


if __name__ == '__main__':
    main()
