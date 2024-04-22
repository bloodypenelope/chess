"""Module that describes a knight"""
from typing import Tuple, Dict, List

import pygame

from game.model.pieces.piece import Piece, PieceColor, CELL_SIZE

WHITE_KNIGHT = pygame.image.load('assets\\images\\white_knight.png')
BLACK_KNIGHT = pygame.image.load('assets\\images\\black_knight.png')

WHITE_KNIGHT = pygame.transform.smoothscale(
    WHITE_KNIGHT, (CELL_SIZE, CELL_SIZE))
BLACK_KNIGHT = pygame.transform.smoothscale(
    BLACK_KNIGHT, (CELL_SIZE, CELL_SIZE))


class Knight(Piece):
    """Class that describes a knight"""

    def __init__(self, position: tuple, color: PieceColor) -> None:
        image = WHITE_KNIGHT if color == PieceColor.WHITE else BLACK_KNIGHT
        super().__init__(position, color, image)
        self.offsets: List[Tuple[int, int]] = [(-2, 1), (-1, 2),
                                               (1, 2), (2, 1),
                                               (2, -1), (1, -2),
                                               (-1, -2), (-2, -1)]

    def get_moves(self, board: Dict[Tuple[int, int], Piece])\
            -> List[Tuple[int, int]]:
        """Gets all possible knight's moves

        Args:
            board (Dict[Tuple[int, int], Piece]): Chessboard

        Returns:
            List[Tuple[int, int]]: List of all possible moves
        """
        moves: List[Tuple[int, int]] = []
        for file_offset, rank_offset in self.offsets:
            file = self._file + file_offset
            rank = self._rank + rank_offset
            position = file, rank

            if self.off_board(position):
                continue

            piece = board.get(position)
            if not piece or piece.color == PieceColor(1 - self.color.value):
                moves.append(position)
        return moves

    def update_valid_moves(self, board_state: Dict[str, any],
                           king_position: Tuple[int, int]) -> None:
        """Updates knight's valid moves

        Args:
            board_state: Dict[str, any]: Chessboard's state
        """
        self.valid_moves.clear()
        board: Dict[Tuple[int, int], Piece] = board_state['board']
        moves = self.get_moves(board)
        opponent_pieces: List[Piece] = []

        for piece in board.values():
            if self.color != piece.color:
                opponent_pieces.append(piece)

        for move in moves.copy():
            virtual_board = board.copy()
            virtual_board[move] = self
            virtual_board.pop(self.position)

            for opponent_piece in opponent_pieces:
                if opponent_piece.position != move and move in moves and\
                        opponent_piece.can_attack(virtual_board,
                                                  king_position):
                    moves.remove(move)
        self.valid_moves.extend(moves)

    def __str__(self) -> str:
        return 'N' if self.color == PieceColor.WHITE else 'n'
