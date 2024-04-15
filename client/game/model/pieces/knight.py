"""Module that describes a pawn"""
from client.game.model.pieces.piece import Piece, PieceColor
from client.game.configs import *
import pygame


WHITE_KNIGHT = pygame.image.load('game/assets/images/white_knight.png')
BLACK_KNIGHT = pygame.image.load('game/assets/images/black_knight.png')

WHITE_KNIGHT = pygame.transform.smoothscale(WHITE_KNIGHT, (PIECE_SIZE, PIECE_SIZE))
BLACK_KNIGHT = pygame.transform.smoothscale(BLACK_KNIGHT, (PIECE_SIZE, PIECE_SIZE))


class Knight(Piece):
    """
    Class that describes a pawn

    Args:
        position (tuple): Position of a knight
        color (PieceColor): Color of a knight
    """

    def __init__(self, position: tuple, color: PieceColor) -> None:
        image = WHITE_KNIGHT if color == PieceColor.WHITE else BLACK_KNIGHT
        super().__init__(position, color, image)

    def update_valid_moves(self, board):
        self.valid_moves.clear()
        offsets = [(-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1)]

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

