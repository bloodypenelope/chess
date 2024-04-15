import pygame
from client.game.configs import *


class Square(pygame.sprite.Sprite):
    def __init__(self, color: tuple, position: tuple, opacity=255) -> None:
        super().__init__()
        file, rank = position
        self.position = position
        self.image = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        self.image.fill(color)
        self.image.set_alpha(opacity)
        self.rect = pygame.Rect(file * SQUARE_SIZE, rank * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        self.rect.x = X_OFFSET + file * SQUARE_SIZE
        self.rect.y = Y_OFFSET + rank * SQUARE_SIZE


