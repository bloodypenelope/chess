from client.game.model.board import Board
from client.game.configs import *
import sys
import pygame

clock = pygame.time.Clock()


class Chess:
    def __init__(self, screen: pygame.Surface) -> None:
        pygame.init()
        pygame.display.set_caption("Chess")
        self.board = Board()
        self.screen = screen

    def main_loop(self) -> None:
        while True:
            self._handle_input()
            self._game_logic()
            self._draw()
            clock.tick(FPS)

    def _handle_input(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            self._handel_move(event)

    def _handel_move(self, event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.board.button_down(event.pos)

        if event.type == pygame.MOUSEMOTION:
            self.board.drag(event.pos)

        if event.type == pygame.MOUSEBUTTONUP:
            self.board.button_up(event.pos)

    def _game_logic(self) -> None:
        pass

    def _draw(self) -> None:
        self.screen.fill(BACKGROUND)
        self.board.draw(self.screen)
        pygame.display.update()
