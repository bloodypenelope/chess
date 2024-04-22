"""Module that describes a pawn"""
from typing import Optional, Tuple, Dict, List

import pygame

from game.model.pieces.piece import Piece, PieceColor, CELL_SIZE

WHITE_PAWN = pygame.image.load('assets\\images\\white_pawn.png')
BLACK_PAWN = pygame.image.load('assets\\images\\black_pawn.png')

WHITE_PAWN = pygame.transform.scale(WHITE_PAWN, (CELL_SIZE, CELL_SIZE))
BLACK_PAWN = pygame.transform.scale(BLACK_PAWN, (CELL_SIZE, CELL_SIZE))


class Pawn(Piece):
    """Class that describes a pawn"""

    def __init__(self, position: tuple, color: PieceColor) -> None:
        image = WHITE_PAWN if color == PieceColor.WHITE else BLACK_PAWN
        super().__init__(position, color, image)
        self.direction = -1 if self.color == PieceColor.WHITE else 1

    def get_moves(self, board: Dict[Tuple[int, int], Piece])\
            -> List[Tuple[int, int]]:
        """Gets all possible pawn's moves (except en passant)

        Args:
            board (Dict[Tuple[int, int], Piece]): Chessboard

        Returns:
            List[Tuple[int, int]]: List of all possible moves
        """
        moves: List[Tuple[int, int]] = []
        for sides in (-1, 1):
            position = self._file + sides, self._rank + self.direction
            if self.off_board(position):
                continue

            piece = board.get(position)
            if piece and piece.color == PieceColor(1 - self.color.value):
                moves.append(position)

        push = self._file, self._rank + self.direction
        piece1 = board.get(push)
        if not (piece1 or self.off_board(push)):
            moves.append(push)

        double_push = self._file, self._rank + (self.direction * 2)
        piece2 = board.get(double_push)
        if not (piece1 or piece2 or self.off_board(double_push) or self.moved):
            moves.append(double_push)
        return moves

    def update_valid_moves(self, board_state: Dict[str, any],
                           king_position: Tuple[int, int]) -> None:
        """Updates pawn's valid moves

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

        en_passant: Optional[Tuple[int, int]] = board_state['en_passant']
        if en_passant in [(self._file - 1, self._rank + self.direction),
                          (self._file + 1, self._rank + self.direction)]:
            self.valid_moves.append(en_passant)

    def __str__(self) -> str:
        return 'P' if self.color == PieceColor.WHITE else 'p'
