"""Module that describes chess pieces"""
from abc import ABC, abstractmethod
from typing import Self, Tuple, Dict, List
from enum import Enum
import pygame

CELL_SIZE = 80


class PieceColor(Enum):
    """Enum class for chess piece's color"""
    WHITE = 0
    BLACK = 1


class Piece(ABC, pygame.sprite.Sprite):
    """Abstract class that describes a chess piece"""

    def __init__(self, position: Tuple[int, int], color: PieceColor,
                 image: pygame.Surface) -> None:
        super().__init__()
        self._file, self._rank = position
        self._color = color
        self._valid_moves: List[Tuple[int, int]] = []
        self._moved = False

        self.image = image
        self.rect = image.get_rect()

    @property
    def position(self) -> Tuple[int, int]:
        """Property that contains piece's position on the board

        Returns:
            Tuple[int, int]: Piece's position
        """
        return self._file, self._rank

    @position.setter
    def position(self, position: Tuple[int, int]) -> None:
        file, rank = position
        self._file, self._rank = file, rank

    @property
    def color(self) -> PieceColor:
        """Property that contains a color of a chess piece

        Returns:
            PieceColor: Color of a chess piece
        """
        return self._color

    @property
    def moved(self) -> bool:
        """Property that tells whether chess piece has moved or not

        Returns:
            bool: True if chess piece has moved, False otherwise
        """
        return self._moved

    @property
    def valid_moves(self) -> List[Tuple[int, int]]:
        """Property that contains a list of chess piece's valid moves

        Returns:
            list: List of chess piece's valid moves
        """
        return self._valid_moves

    def has_moved(self) -> None:
        """Sets moved property of a chess piece to True"""
        self._moved = True

    def off_board(self, position: Tuple[int, int]) -> bool:
        """Tells if the passed position is off board or not

        Args:
            position (Tuple[int, int]): Position

        Returns:
            bool: True if the position is off board, False otherwise
        """
        file, rank = position
        return not (0 <= file <= 7 and 0 <= rank <= 7)

    def can_attack(self, board: Dict[Tuple[int, int], Self],
                   position: Tuple[int, int]) -> bool:
        """Tells if a piece can attack a given square

        Args:
            board (Dict[Tuple[int, int], Self]): Chessboard
            position (Tuple[int, int]): Position of a square

        Returns:
            bool: True if a piece can attack a square, False otherwise
        """
        moves = self.get_moves(board)
        return position in moves

    @abstractmethod
    def get_moves(self, board: Dict[Tuple[int, int], Self])\
            -> List[Tuple[int, int]]:
        """Gets all possible piece's moves

        Args:
            board: Dict[Tuple[int, int], Self]: Chessboard

        Returns:
            List[Tuple[int, int]]: List of all possible moves
        """

    @abstractmethod
    def update_valid_moves(self, board_state: Dict[str, any],
                           king_position: Tuple[int, int]) -> None:
        """Updates chess piece's valid moves

        Args:
            board_state: Dict[str, any]: Chessboard's state
        """

    @abstractmethod
    def __str__(self) -> str:
        pass
