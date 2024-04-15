"""Module that describes a pawn"""
from client.game.model.pieces.piece import Piece, PieceColor
from client.game.configs import *
import pygame


WHITE_QUEEN = pygame.image.load('game/assets/images/white_queen.png')
BLACK_QUEEN = pygame.image.load('game/assets/images/black_queen.png')

WHITE_QUEEN = pygame.transform.scale(WHITE_QUEEN, (PIECE_SIZE, PIECE_SIZE))
BLACK_QUEEN = pygame.transform.scale(BLACK_QUEEN, (PIECE_SIZE, PIECE_SIZE))


class Queen(Piece):
    """
    Class that describes a pawn

    Args:
        position (tuple): Position of a queen
        color (PieceColor): Color of a queen
    """

    def __init__(self, position: tuple, color: PieceColor) -> None:
        image = WHITE_QUEEN if color == PieceColor.WHITE else BLACK_QUEEN
        super().__init__(position, color, image)

    def update_valid_moves(self, board):
        self.valid_moves.clear()
        offsets = [(-1, 0), (0, 1), (1, 0), (0, -1), (-1, 1), (1, 1), (1, -1), (-1, -1)]

        for file_offset, rank_offset in offsets:
            mul = 0
            while True:
                mul += 1
                file = self._file + mul * file_offset
                rank = self._rank + mul * rank_offset
                if self.is_of_board(file, rank):
                    break
                piece = board.get((file, rank))
                if piece is not None:
                    if piece.color == PieceColor(abs(self.color.value - 1)):
                        self.valid_moves.append((file, rank))
                    break

                self._valid_moves.append((file, rank))
