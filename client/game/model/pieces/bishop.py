"""Module that describes a bishop"""
from typing import Tuple, Dict, List

import pygame

from game.model.pieces.piece import Piece, PieceColor, CELL_SIZE

WHITE_BISHOP = pygame.image.load('assets\\images\\white_bishop.png')
BLACK_BISHOP = pygame.image.load('assets\\images\\black_bishop.png')

WHITE_BISHOP = pygame.transform.scale(WHITE_BISHOP, (CELL_SIZE, CELL_SIZE))
BLACK_BISHOP = pygame.transform.scale(BLACK_BISHOP, (CELL_SIZE, CELL_SIZE))


class Bishop(Piece):
    """Class that describes a bishop"""

    def __init__(self, position: tuple, color: PieceColor) -> None:
        image = WHITE_BISHOP if color == PieceColor.WHITE else BLACK_BISHOP
        super().__init__(position, color, image)
        self.offsets: List[Tuple[int, int]] = [(-1, 1), (1, 1),
                                               (1, -1), (-1, -1)]

    def get_moves(self, board: Dict[Tuple[int, int], Piece])\
            -> List[Tuple[int, int]]:
        """Gets all possible bishop's moves

        Args:
            board (Dict[Tuple[int, int], Piece]): Chessboard

        Returns:
            List[Tuple[int, int]]: List of all possible moves
        """
        moves: List[Tuple[int, int]] = []
        for file_offset, rank_offset in self.offsets:
            step = 0
            while True:
                step += 1
                file = self._file + step * file_offset
                rank = self._rank + step * rank_offset
                position = file, rank

                if self.off_board(position):
                    break

                piece = board.get(position)
                if piece and piece.color == PieceColor(1 - self.color.value):
                    moves.append(position)
                if piece:
                    break

                moves.append(position)
        return moves

    def update_valid_moves(self, board_state: Dict[str, any],
                           king_position: Tuple[int, int]) -> None:
        """Updates bishop's valid moves

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
        return 'B' if self.color == PieceColor.WHITE else 'b'
