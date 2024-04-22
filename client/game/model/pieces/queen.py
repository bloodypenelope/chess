"""Module that describes a queen"""
from typing import Tuple, Dict, List

import pygame

from game.model.pieces.piece import Piece, PieceColor, CELL_SIZE

WHITE_QUEEN = pygame.image.load('assets\\images\\white_queen.png')
BLACK_QUEEN = pygame.image.load('assets\\images\\black_queen.png')

WHITE_QUEEN = pygame.transform.scale(WHITE_QUEEN, (CELL_SIZE, CELL_SIZE))
BLACK_QUEEN = pygame.transform.scale(BLACK_QUEEN, (CELL_SIZE, CELL_SIZE))


class Queen(Piece):
    """Class that describes a queen"""

    def __init__(self, position: tuple, color: PieceColor) -> None:
        image = WHITE_QUEEN if color == PieceColor.WHITE else BLACK_QUEEN
        super().__init__(position, color, image)
        self.offsets: List[Tuple[int, int]] = [(-1, 0), (0, 1),
                                               (1, 0), (0, -1),
                                               (-1, 1), (1, 1),
                                               (1, -1), (-1, -1)]

    def get_moves(self, board: Dict[Tuple[int, int], Piece])\
            -> List[Tuple[int, int]]:
        """Gets all possible queen's moves

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
        """Updates queen's valid moves

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
        return 'Q' if self.color == PieceColor.WHITE else 'q'
