"""Module that describes a king"""
from typing import Tuple, Dict, List

import pygame

from game.model.pieces.piece import Piece, PieceColor, CELL_SIZE

WHITE_KING = pygame.image.load('assets\\images\\white_king.png')
BLACK_KING = pygame.image.load('assets\\images\\black_king.png')

WHITE_KING = pygame.transform.scale(WHITE_KING, (CELL_SIZE, CELL_SIZE))
BLACK_KING = pygame.transform.scale(BLACK_KING, (CELL_SIZE, CELL_SIZE))


class King(Piece):
    """Class that describes a king"""

    def __init__(self, position: tuple, color: PieceColor) -> None:
        image = WHITE_KING if color == PieceColor.WHITE else BLACK_KING
        super().__init__(position, color, image)
        self.offsets: List[Tuple[int, int]] = [(-1, 0), (0, 1),
                                               (1, 0), (0, -1),
                                               (-1, 1), (1, 1),
                                               (1, -1), (-1, -1)]

    def is_checked(self, board: Dict[Tuple[int, int], Piece]):
        pass

    def get_moves(self, board: Dict[Tuple[int, int], Piece])\
            -> List[Tuple[int, int]]:
        """Gets all possible king's moves (except castle)

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
        """Updates king's valid moves

        Args:
            board_state: Dict[str, any]: Chessboard's state
        """
        # pylint: disable=unused-argument
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
                        opponent_piece.can_attack(virtual_board, move):
                    moves.remove(move)
        self.valid_moves.extend(moves)

        castle_rights: List[str] = board_state['castle_rights'][self.color]
        for file_char in castle_rights:
            fisher = False
            match file_char:
                case 'K': castle_file = 6
                case 'Q': castle_file = 2
                case char:
                    castle_file = ord(char) - ord('A')
                    fisher = True
            castle_move = (castle_file, self._rank)
            king_dest = 6 if castle_file > self._file else 2
            castle = True

            start = min(self._file, king_dest)
            end = max(self._file, king_dest)
            for file in range(start, end + 1):
                for opponent_piece in opponent_pieces:
                    if opponent_piece.can_attack(board, (file, self._rank)):
                        castle = False
                if file == self._file or (file == castle_file and fisher):
                    continue
                if board.get((file, self._rank)):
                    castle = False
            if castle:
                self.valid_moves.append(castle_move)

    def __str__(self) -> str:
        return 'K' if self.color == PieceColor.WHITE else 'k'
