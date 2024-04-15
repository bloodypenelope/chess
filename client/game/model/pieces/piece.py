"""Module that describes chess pieces"""
from enum import Enum
from abc import ABC, abstractmethod
from client.game.configs import *
import pygame


class PieceColor(Enum):
    """Enum class for chess piece's color"""
    WHITE = 0
    BLACK = 1


class Piece(ABC, pygame.sprite.Sprite):
    """
    Abstract class that describes a chess piece

    Args:
        position (tuple): Position of a chess piece
        color (PieceColor): Color of a chess piece
        image (pygame.Surface): Image of a chess piece
    """

    def __init__(self, position: tuple, color: PieceColor, image: pygame.Surface) -> None:
        super().__init__()
        self._file, self._rank = position
        self._color = color
        self.image = image
        self.rect = image.get_rect(center=((self._file + 0.5) * SQUARE_SIZE, (self._rank + 0.5) * SQUARE_SIZE))
        self.rect.x = X_OFFSET + position[0] * SQUARE_SIZE + (SQUARE_SIZE - self.rect.width) // 2
        self.rect.y = Y_OFFSET + position[1] * SQUARE_SIZE + (SQUARE_SIZE - self.rect.height) // 2
        self._moved = False
        self._valid_moves = []

    @property
    def position(self) -> tuple:
        return self._file, self._rank

    @position.setter
    def position(self, position: tuple) -> None:
        if not isinstance(position, tuple):
            raise TypeError('Invalid type for a position argument')

        positions = set(range(8))
        file, rank = position
        if file not in positions and rank not in positions:
            raise ValueError('Invalid position')

        self._file, self._rank = file, rank
        self.rect.center = (self._file + 0.5) * SQUARE_SIZE, (self._rank + 0.5) * SQUARE_SIZE
        self.rect.x = X_OFFSET + position[0] * SQUARE_SIZE + (SQUARE_SIZE - self.rect.width) // 2
        self.rect.y = Y_OFFSET + position[1] * SQUARE_SIZE + (SQUARE_SIZE - self.rect.height) // 2

    @property
    def color(self) -> PieceColor:
        """
        Property that contains a color of a chess piece

        Returns:
            PieceColor: Color of a chess piece
        """
        return self._color

    @property
    def moved(self) -> bool:
        """
        Property that tells whether chess piece has moved or not

        Returns:
            bool: True if chess piece has moved, False otherwise
        """
        return self._moved

    @property
    def valid_moves(self) -> list:
        """
        Property that contains a list of chess piece's valid moves

        Returns:
            list: List of chess piece's valid moves
        """
        return self._valid_moves

    def has_moved(self) -> None:
        """Sets moved property of a chess piece to True"""
        self._moved = True

    @abstractmethod
    def update_valid_moves(self, board):
        """
        Updates chess piece's valid moves

        Args:
            board: Chessboard
        """

    @staticmethod
    def is_of_board(file: int, rank: int) -> bool:
        return not (0 <= file <= 7 and 0 <= rank <= 7)
