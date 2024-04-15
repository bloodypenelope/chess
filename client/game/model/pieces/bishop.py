"""Module that describes a pawn"""
from client.game.model.pieces.piece import Piece, PieceColor
from client.game.configs import *
import pygame


WHITE_BISHOP = pygame.image.load('game/assets/images/white_bishop.png')
BLACK_BISHOP = pygame.image.load('game/assets/images/black_bishop.png')

WHITE_BISHOP = pygame.transform.scale(WHITE_BISHOP, (PIECE_SIZE, PIECE_SIZE))
BLACK_BISHOP = pygame.transform.scale(BLACK_BISHOP, (PIECE_SIZE, PIECE_SIZE))


class Bishop(Piece):
    """
    Class that describes a pawn

    Args:
        position (tuple): Position of a bishop
        color (PieceColor): Color of a bishop
    """

    def __init__(self, position: tuple, color: PieceColor) -> None:
        image = WHITE_BISHOP if color == PieceColor.WHITE else BLACK_BISHOP
        super().__init__(position, color, image)

    def update_valid_moves(self, board):
        self.valid_moves.clear()
        offsets = [(-1, 1), (1, 1), (1, -1), (-1, -1)]

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
