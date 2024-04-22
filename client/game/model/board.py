"""Module that describes chessboard"""
from typing import Optional, Tuple, Dict, List
from enum import Enum

import pygame

from game.model.pieces.piece import Piece, PieceColor, CELL_SIZE
from game.model.pieces.bishop import Bishop
from game.model.pieces.king import King
from game.model.pieces.knight import Knight
from game.model.pieces.pawn import Pawn
from game.model.pieces.queen import Queen
from game.model.pieces.rook import Rook


class InvalidFENError(Exception):
    """Error that raises when invalid FEN string was passed"""


class CellColor(Enum):
    """Enum class for chessboard's cell color"""
    LIGHT = (235, 236, 208)
    DARK = (119, 149, 86)
    MARKED = (255, 242, 0)


class Cell(pygame.sprite.Sprite):
    """Class for chessboard's cell"""

    def __init__(self, position: Tuple[int, int],
                 color: CellColor) -> None:
        super().__init__()
        self.position = position
        self.color = color
        self.marked = False
        self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill(color.value)
        self.rect = self.image.get_rect()

    def mark(self, opacity: int = 255):
        """Marks a cell

        Args:
            opacity (int, optional): Opacity value for a marked color.\
                Defaults to 255
        """
        if not self.marked:
            self.marked = True
            marked_color = CellColor.MARKED.value + (opacity,)
            marked_surface = pygame.Surface((CELL_SIZE, CELL_SIZE),
                                            pygame.SRCALPHA)
            marked_surface.fill(marked_color)
            self.image.blit(marked_surface, (0, 0))

    def unmark(self):
        """Deletes mark from a cell"""
        if self.marked:
            self.marked = False
            self.image.fill(self.color.value)


class Board:
    """Class for chessboard"""

    def __init__(self, fen: str) -> None:
        self.pieces: Dict[Tuple[int, int], Piece] = None
        self.turn: PieceColor = None
        self.castle_rights: Dict[PieceColor, List[str]] = None
        self.en_passant: Optional[Tuple[int, int]] = None
        self.moves_count: Dict[str, int] = None
        self.cells: Dict[Tuple[int, int], Cell] = None

        board_state = fen.split()
        self._set_board(board_state)

    def make_move(self, current_position: Tuple[int, int],
                  new_position: Tuple[int, int]) -> str:
        piece = self.pieces.pop(current_position)
        captured_piece: Optional[Piece] = None
        castle = False
        en_passant = self.en_passant
        self.en_passant = None

        if isinstance(piece, Pawn) and new_position == en_passant:
            self.moves_count['half'] = 0
            file, rank = en_passant
            captured_piece = self.pieces.pop((file, rank - piece.direction))
            piece.position = en_passant
            self.pieces[en_passant] = piece
        elif isinstance(piece, King):
            self.moves_count['half'] += 1
            file, rank = current_position
            new_file, _ = new_position
            rook = self.pieces.get(new_position)
            castle = abs(new_file - file) == 2 or\
                (isinstance(rook, Rook) and rook.color == piece.color)
            if castle:
                castle_side = 'K' if new_file > file else 'Q'
                if castle_side == 'K':
                    if not rook:
                        rook = self.pieces[(7, rank)]
                        new_position = rook.position
                    self.pieces.pop(rook.position)
                    rook.position = (5, rank)
                    self.pieces[(5, rank)] = rook
                    piece.position = (6, rank)
                    self.pieces[(6, rank)] = piece
                elif castle_side == 'Q':
                    if not rook:
                        rook = self.pieces[(0, rank)]
                        new_position = rook.position
                    self.pieces.pop(rook.position)
                    rook.position = (3, rank)
                    self.pieces[(3, rank)] = rook
                    piece.position = (2, rank)
                    self.pieces[(2, rank)] = piece
            else:
                if self.pieces.get(new_position):
                    captured_piece = self.pieces.pop(new_position)
                piece.position = new_position
                self.pieces[new_position] = piece
            castle_rights = self.castle_rights[piece.color]
            if not piece.moved:
                castle_rights.clear()
        else:
            self.moves_count['half'] += 1
            if self.pieces.get(new_position):
                captured_piece = self.pieces.pop(new_position)
            if isinstance(piece, Rook):
                file, _ = piece.position
                castle_rights = self.castle_rights[piece.color]
                castle_side: str = None
                file_char = chr(ord('A') + file)
                if file_char == 'H':
                    castle_side = 'K'
                elif file_char == 'A':
                    castle_side = 'Q'
                for char in [file_char, castle_side]:
                    if char in castle_rights and not piece.moved:
                        castle_rights.remove(char)
            if isinstance(piece, Pawn):
                self.moves_count['half'] = 0
                file, rank = piece.position
                _, new_rank = new_position
                if abs(new_rank - rank) == 2:
                    self.en_passant = (file, rank + piece.direction)
            piece.position = new_position
            self.pieces[new_position] = piece

        if captured_piece:
            self.moves_count['half'] = 0
            captured_piece.kill()
        if not piece.moved:
            piece.has_moved()
        self.delete_all_marks()
        self.cells[current_position].mark(100)
        self.cells[new_position].mark(100)

        if self.turn == PieceColor.BLACK:
            self.moves_count['full'] += 1

        if castle:
            return 'castle'
        if captured_piece:
            return 'capture'
        return 'regular'

    def update_pieces_moves(self, color: PieceColor) -> None:
        king_position: Tuple[int, int] = None
        board_state = {
            'board': self.pieces,
            'en_passant': self.en_passant,
            'castle_rights': self.castle_rights
        }

        for piece in self.pieces.values():
            if isinstance(piece, King) and piece.color == color:
                king_position = piece.position

        for piece in self.pieces.values():
            if piece.color == color:
                piece.update_valid_moves(board_state, king_position)

    def delete_all_marks(self) -> None:
        for cell in self.cells.values():
            cell.unmark()

    def get_board_cell(self, mouse_position: Tuple[float, float])\
            -> Optional[Tuple[int, int]]:
        for position, cell in self.cells.items():
            collide = cell.rect.collidepoint(mouse_position)
            if collide:
                return position

    def is_king_checked(self, color: PieceColor) -> bool:
        king: Optional[King] = None
        for piece in self.pieces.values():
            if isinstance(piece, King) and piece.color == color:
                king = piece

        for piece in self.pieces.values():
            if king and piece.color != king.color and\
                    piece.can_attack(self.pieces, king.position):
                return True
        return False

    def _set_board(self, board_state: List[str]) -> None:
        self._set_cells()

        pieces = board_state.pop(0)
        if not (pieces.count('K') == 1 and pieces.count('k') == 1):
            raise InvalidFENError("Invalid position")
        pieces = pieces.split('/')
        self._set_pieces(pieces)

        turn = board_state.pop(0)
        if turn not in ('w', 'b'):
            raise InvalidFENError("Invalid turn")
        self.turn = PieceColor.WHITE if turn == 'w' else PieceColor.BLACK

        castle_rights = board_state.pop(0)
        white_castle: List[str] = []
        black_castle: List[str] = []
        if castle_rights != '-':
            for file in castle_rights:
                if file.isupper():
                    white_castle.append(file)
                else:
                    black_castle.append(file)
            if len(white_castle) > 2 or len(black_castle) > 2:
                raise InvalidFENError('Invalid castle rights')
            black_castle = list(map(lambda char: char.upper(), black_castle))
        self.castle_rights = {
            PieceColor.WHITE: white_castle,
            PieceColor.BLACK: black_castle
        }

        en_passant = board_state.pop(0)
        if en_passant != '-':
            if len(en_passant) != 2:
                raise InvalidFENError('Invalid en passant target')

            file = ord(en_passant[0]) - ord('a')
            rank = int(en_passant[1]) - 1
            print(file, rank)
            if not (0 <= file <= 7 and 0 <= rank <= 7):
                raise InvalidFENError('Invalid en passant target')

            self.en_passant = (file, rank)

        half_moves, full_moves = board_state.pop(0), board_state.pop(0)
        self.moves_count = {}
        self.moves_count['half'] = int(half_moves)
        self.moves_count['full'] = int(full_moves)

    def _set_pieces(self, pieces: List[str]) -> None:
        if len(pieces) != 8:
            raise InvalidFENError('Invalid position')

        self.pieces = {}
        for rank, row in enumerate(pieces):
            file = 0

            for char in row:
                if char.isnumeric():
                    file += int(char)
                    continue

                position = file, rank
                is_white = char.isupper()
                color = PieceColor.WHITE if is_white else PieceColor.BLACK

                match char.lower():
                    case 'p': piece = Pawn(position, color)
                    case 'n': piece = Knight(position, color)
                    case 'b': piece = Bishop(position, color)
                    case 'r': piece = Rook(position, color)
                    case 'q': piece = Queen(position, color)
                    case 'k': piece = King(position, color)
                    case _: raise InvalidFENError("Unknown piece")

                self.pieces[position] = piece
                file += 1

            if file != 8:
                raise InvalidFENError('Invalid position')

    def _set_cells(self) -> None:
        self.cells = {}
        for file in range(8):
            for rank in range(8):
                is_light = not bool((file + rank) % 2)
                position = file, rank
                color = CellColor.LIGHT if is_light else CellColor.DARK

                cell = Cell(position, color)
                self.cells[position] = cell

    def __str__(self) -> str:
        fen = []

        board = []
        for rank in range(8):
            counter = 0
            row = ''
            for file in range(8):
                piece = self.pieces.get((file, rank))
                if piece:
                    row += str(counter) if counter else ''
                    counter = 0
                    row += str(piece)
                else:
                    counter += 1
            if counter:
                row += str(counter)
            board.append(row)
        fen.append('/'.join(board))

        turn = 'w' if self.turn == PieceColor.WHITE else 'b'
        fen.append(turn)

        white_castle = self.castle_rights[PieceColor.WHITE]
        black_castle = list(map(lambda char: char.lower(),
                            self.castle_rights[PieceColor.BLACK]))
        castle_rights = ''.join(white_castle + black_castle)
        if not castle_rights:
            castle_rights = '-'
        fen.append(castle_rights)

        en_passant = '-'
        if self.en_passant:
            file, rank = self.en_passant
            file = chr(ord('a') + file)
            rank += 1
            en_passant = f'{file}{rank}'
        fen.append(en_passant)

        half_moves = self.moves_count['half']
        full_moves = self.moves_count['full']
        fen.extend([str(half_moves), str(full_moves)])

        return ' '.join(fen)
