"""Module that describes a pawn"""
from client.game.model.pieces.piece import Piece, PieceColor
from client.game.configs import *
import pygame


WHITE_PAWN = pygame.image.load('game/assets/images/white_pawn.png')
BLACK_PAWN = pygame.image.load('game/assets/images/black_pawn.png')

WHITE_PAWN = pygame.transform.scale(WHITE_PAWN, (PIECE_SIZE - 20, PIECE_SIZE - 20))
BLACK_PAWN = pygame.transform.scale(BLACK_PAWN, (PIECE_SIZE - 20, PIECE_SIZE - 20))


class Pawn(Piece):
    """
    Class that describes a pawn

    Args:
        position (tuple): Position of a pawn
        color (PieceColor): Color of a pawn
    """

    def __init__(self, position: tuple, color: PieceColor) -> None:
        image = WHITE_PAWN if color == PieceColor.WHITE else BLACK_PAWN
        super().__init__(position, color, image)
        self.direction = -1 if color == PieceColor.WHITE else 1

    def update_valid_moves(self, board):
        self.valid_moves.clear()

        for i in (-1, 1):
            pos = self._file + i, self._rank + self.direction
            piece = board.get(pos)
            if piece and piece.color == PieceColor(abs(self.color.value - 1)):
                self.valid_moves.append((self._file + i, self._rank + self.direction))

        if board.get((self._file, self._rank + self.direction)):
            return

        self.valid_moves.append((self._file, self._rank + self.direction))
        if self._rank in (1, 6):
            self.valid_moves.append((self._file, self._rank + 2 * self.direction))


