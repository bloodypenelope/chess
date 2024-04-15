"""Module that describes a pawn"""
from client.game.model.pieces.piece import Piece, PieceColor
from client.game.configs import *
import pygame


WHITE_KING = pygame.image.load('game/assets/images/white_king.png')
BLACK_KING = pygame.image.load('game/assets/images/black_king.png')

WHITE_KING = pygame.transform.scale(WHITE_KING, (PIECE_SIZE, PIECE_SIZE))
BLACK_KING = pygame.transform.scale(BLACK_KING, (PIECE_SIZE, PIECE_SIZE))


class King(Piece):
    """
    Class that describes a pawn

    Args:
        position (tuple): Position of a pawn
        color (PieceColor): Color of a pawn
    """

    def __init__(self, position: tuple, color: PieceColor) -> None:
        image = WHITE_KING if color == PieceColor.WHITE else BLACK_KING
        super().__init__(position, color, image)

    def update_valid_moves(self, board):
        self.valid_moves.clear()
        offsets = [(-1, 0), (0, 1), (1, 0), (0, -1), (-1, 1), (1, 1), (1, -1), (-1, -1)]

        for file_offset, rank_offset in offsets:
            file = self._file + file_offset
            rank = self._rank + rank_offset

            if self.is_of_board(file, rank):
                continue

            piece = board.get((file, rank))
            if piece is not None:
                if piece.color == PieceColor(abs(self.color.value - 1)):
                    self.valid_moves.append((file, rank))
                continue

            self._valid_moves.append((file, rank))
