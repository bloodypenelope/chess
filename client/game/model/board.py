"""Module that describes a chessboard"""
from client.game.model.pieces.piece import PieceColor
from client.game.model.pieces.pawn import Pawn
from client.game.model.pieces.knight import Knight
from client.game.model.pieces.bishop import Bishop
from client.game.model.pieces.rook import Rook
from client.game.model.pieces.queen import Queen
from client.game.model.pieces.king import King
from client.game.model.square import Square
from client.game.configs import *
import pygame


class Board:
    def __init__(self) -> None:
        pygame.init()
        self._squares = self.__create_squares()
        self._pieces_dict = {(0, 0): Rook((0, 0), PieceColor.BLACK), (1, 0): Knight((1, 0), PieceColor.BLACK),
                             (2, 0): Bishop((2, 0), PieceColor.BLACK), (3, 0): Queen((3, 0), PieceColor.BLACK),
                             (4, 0): King((4, 0), PieceColor.BLACK), (5, 0): Bishop((5, 0), PieceColor.BLACK),
                             (6, 0): Knight((6, 0), PieceColor.BLACK), (7, 0): Rook((7, 0), PieceColor.BLACK),
                             (0, 7): Rook((0, 7), PieceColor.WHITE), (1, 7): Knight((1, 7), PieceColor.WHITE),
                             (2, 7): Bishop((2, 7), PieceColor.WHITE), (3, 7): Queen((3, 7), PieceColor.WHITE),
                             (4, 7): King((4, 7), PieceColor.WHITE), (5, 7): Bishop((5, 7), PieceColor.WHITE),
                             (6, 7): Knight((6, 7), PieceColor.WHITE), (7, 7): Rook((7, 7), PieceColor.WHITE)}
        for file in range(8):
            self._pieces_dict[file, 1] = Pawn((file, 1), PieceColor.BLACK)
            self._pieces_dict[file, 6] = Pawn((file, 6), PieceColor.WHITE)

        self._pieces = self.__create_pieces()

        self._dragged_piece = None
        self._picked_piece = None
        self._marked_squares = pygame.sprite.Group()

    def get_pieces(self, color=None) -> list:
        if color is None:
            return list(self._pieces_dict.values())
        return [p for p in self._pieces_dict.values() if color is p.color]

    def draw(self, screen: pygame.Surface) -> None:
        self.__draw_board(screen)

        self._squares.draw(screen)

        self._marked_squares.draw(screen)

        self._pieces.draw(screen)

    def __draw_board(self, screen) -> None:
        board = pygame.Surface((BOARD_SIZE, BOARD_SIZE))
        board.fill(BOARD_COLOR)

        self.__draw_notation(board)

        screen.blit(board, ((WINDOW_SIZE[0] - BOARD_SIZE) // 2,
                            (WINDOW_SIZE[1] - BOARD_SIZE) // 2))

    @staticmethod
    def __draw_notation(board) -> None:
        files = pygame.Surface((PLAY_FIELD_SIZE, FILES_SIZE), pygame.SRCALPHA)
        ranks = pygame.Surface((RANKS_SIZE, PLAY_FIELD_SIZE), pygame.SRCALPHA)
        font = pygame.font.Font(pygame.font.get_default_font(), FONT_SIZE)

        for i in range(8):
            letter = font.render(LETTERS[i], 1, TEXT_COLOR)
            number = font.render(str(8 - i), 1, TEXT_COLOR)

            files.blit(letter, (
                i * SQUARE_SIZE + (SQUARE_SIZE - letter.get_rect().width) // 2,
                (FILES_SIZE - letter.get_rect().height) // 2))
            ranks.blit(number, (
                (RANKS_SIZE - letter.get_rect().width) // 2,
                i * SQUARE_SIZE + (SQUARE_SIZE - number.get_rect().height) // 2))

        board.blit(ranks, (0, files.get_height()))
        board.blit(ranks, (ranks.get_width() + SQUARE_SIZE * 8, files.get_height()))
        board.blit(files, (ranks.get_width(), 0))
        board.blit(files, (ranks.get_width(), ranks.get_width() + SQUARE_SIZE * 8))

    @staticmethod
    def __create_squares():
        squares = pygame.sprite.Group()

        for file in range(8):
            for rank in range(8):
                is_cell_white = not bool((file + rank) % 2)
                position = (file, rank)

                color = LIGHT_SQUARE_COLOR if is_cell_white else DARK_SQUARE_COLOR
                square = Square(color, position)

                squares.add(square)

        return squares

    def __create_pieces(self):
        pieces = pygame.sprite.Group()

        for piece in self._pieces_dict.values():
            pieces.add(piece)

        return pieces

    def button_down(self, pos: tuple) -> None:
        new_pos = self._get_board_position(pos)

        if self._picked_piece is not None:
            cur_pos = self._picked_piece.position
            self._picked_piece.update_valid_moves(self._pieces_dict)
            self.__draw_valid_moves(self._picked_piece)

            if new_pos in self._picked_piece.valid_moves:
                self._make_move(cur_pos, new_pos)
            else:
                self._delete_mark(cur_pos)
            self._picked_piece = None

        if piece := self._pieces_dict.get(new_pos):
            self._dragged_piece = piece
            piece.rect.center = pos

            marked_square = Square(MARKED_COLOR, new_pos, 100)
            self._marked_squares.add(marked_square)

    def drag(self, pos: tuple) -> None:
        if self._dragged_piece is not None:
            if self._is_on_board(pos):
                self._dragged_piece.rect.center = pos
                return
            self._dragged_piece.position = self._dragged_piece.position
            self._delete_mark(self._dragged_piece.position)
            self._dragged_piece = None
            self._picked_piece = None

    @staticmethod
    def _is_on_board(pos: tuple) -> bool:
        x, y = pos
        return X_OFFSET <= x <= X_OFFSET + BOARD_SIZE and Y_OFFSET <= y <= Y_OFFSET + BOARD_SIZE

    def button_up(self, pos: tuple) -> None:
        if self._dragged_piece is not None:
            cur_pos = self._dragged_piece.position
            new_pos = self._get_board_position(pos)

            if cur_pos == new_pos:
                self._picked_piece = self._dragged_piece
                self._marked_squares.add(Square(MARKED_COLOR, new_pos, 100))

            self._dragged_piece.update_valid_moves(self._pieces_dict)
            if new_pos in self._dragged_piece.valid_moves:
                self._make_move(cur_pos, new_pos)
            else:
                self._delete_mark(cur_pos)
                self._dragged_piece.position = cur_pos
            self._dragged_piece = None

    def _delete_mark(self, position: tuple) -> None:
        for s in self._marked_squares:
            if self._get_board_position(s.rect.center) == position:
                s.kill()
                break

    @staticmethod
    def _get_board_position(pos: tuple) -> tuple:
        file = (pos[0] - X_OFFSET) // SQUARE_SIZE
        rank = (pos[1] - Y_OFFSET) // SQUARE_SIZE
        return file, rank

    def _make_move(self, cur_pos: tuple, new_pos: tuple) -> None:
        if self._pieces_dict.get(new_pos):
            captured_piece = self._pieces_dict.pop(new_pos)
            captured_piece.kill()

        piece = self._pieces_dict.pop(cur_pos)
        self._pieces_dict[new_pos] = piece

        piece.position = new_pos

        self._marked_squares.empty()
        self._marked_squares.add(Square(MARKED_COLOR, cur_pos, 100))
        self._marked_squares.add(Square(MARKED_COLOR, new_pos, 100))

        self._dragged_piece = None
        self._picked_piece = None

    def __draw_valid_moves(self, piece):
        pass
