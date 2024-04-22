"""Module that describes chess game's instance"""
from typing import Optional, Tuple, List
from abc import ABC, abstractmethod
import sys

import pygame

from game.model.board import Board
from game.model.pointer import Pointer
from game.model.pieces.piece import Piece, PieceColor, CELL_SIZE
from game.model.pieces.pawn import Pawn
from game.model.pieces.bishop import Bishop, WHITE_BISHOP, BLACK_BISHOP
from game.model.pieces.knight import Knight, WHITE_KNIGHT, BLACK_KNIGHT
from game.model.pieces.rook import Rook, WHITE_ROOK, BLACK_ROOK
from game.model.pieces.queen import Queen, WHITE_QUEEN, BLACK_QUEEN
from game.model.pieces.king import King


pygame.mixer.init()
GAME_START = pygame.mixer.Sound('assets\\sounds\\game_start.mp3')
GAME_END = pygame.mixer.Sound('assets\\sounds\\game_end.mp3')
MOVE = pygame.mixer.Sound('assets\\sounds\\move_self.mp3')
MOVE_OPPONENT = pygame.mixer.Sound('assets\\sounds\\move_opponent.mp3')
ILLEGAL_MOVE = pygame.mixer.Sound('assets\\sounds\\illegal.mp3')
CAPTURE = pygame.mixer.Sound('assets\\sounds\\capture.mp3')
CHECK = pygame.mixer.Sound('assets\\sounds\\move_check.mp3')
CASTLE = pygame.mixer.Sound('assets\\sounds\\castle.mp3')
PROMOTE = pygame.mixer.Sound('assets\\sounds\\promote.mp3')

SCREEN_COLOR = 'gray'
BOARD_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)
FONT_SIZE = 18
GAME_OVER_FONT_SIZE = 36
GAME_OVER_BOX_COLOR = (154, 205, 50, 200)
PLAY_FIELD_SIZE = CELL_SIZE * 8
FILES_SIZE = RANKS_SIZE = CELL_SIZE // 3
BOARD_SIZE = FILES_SIZE * 2 + PLAY_FIELD_SIZE
INACTIVE_BOARD_COLOR = (100, 100, 100, 75)
PROMOTE_BOX_COLOR = (154, 205, 50, 150)
MOVE_DOT_COLOR = (0, 0, 0, 50)


class Chess(ABC):
    """Abstract class for chess game's instance"""

    def __init__(self, screen: pygame.Surface,
                 color: PieceColor, fen: str) -> None:
        self.color = color
        self.board = Board(fen)
        self.clock = pygame.time.Clock()
        self.screen = screen
        self.running = False
        self.game_over = False
        self.game_over_info: Optional[str] = None
        self.move_to_send: Optional[Tuple[any]] = None

        self.sprites = pygame.sprite.LayeredUpdates()
        self.picked_piece: Optional[Piece] = None
        self.dragged_piece: Optional[Piece] = None

        self.current_pointer: Optional[Pointer] = None
        self.pointers: List[Pointer] = []

        self.promote: Optional[Tuple[Tuple[int, int]]] = None

        self._set_initial_sprites()
        self.board.update_pieces_moves(self.board.turn)
        GAME_START.play()

    @abstractmethod
    def mainloop(self) -> None:
        """Starts game's main loop"""

    @abstractmethod
    def _game_logic(self) -> None:
        pass

    def _handle_input(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_down(event)
            if event.type == pygame.MOUSEBUTTONUP:
                self._handle_mouse_up(event)
            if event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(event)

    def _handle_mouse_down(self, event: pygame.event.Event) -> None:
        mouse_position: Tuple[float, float] = event.pos
        position = self.board.get_board_cell(mouse_position)
        piece = self.board.pieces.get(position)

        if event.button == 1:
            if self.game_over:
                self.running = False
            elif self.promote:
                promote_cells = [(3, 3), (4, 3), (3, 4), (4, 4)]
                if self.color == PieceColor.BLACK:
                    promote_cells = list(reversed(promote_cells))

                promote_piece = None
                if position == promote_cells[0]:
                    promote_piece = 'q'
                elif position == promote_cells[1]:
                    promote_piece = 'r'
                elif position == promote_cells[2]:
                    promote_piece = 'b'
                elif position == promote_cells[3]:
                    promote_piece = 'n'

                if promote_piece:
                    cur_pos, new_pos = self.promote
                    self._make_move(cur_pos, new_pos, promote_piece)
                    self.promote = None
            elif piece and piece.color == self.board.turn == self.color:
                if self.picked_piece:
                    cell = self.board.cells[self.picked_piece.position]
                    cell.unmark()
                self.board.update_pieces_moves(self.board.turn)
                self.board.cells[position].mark()
                self.picked_piece = piece
                self.dragged_piece = piece
                self.sprites.change_layer(piece, 3)
            elif self.picked_piece:
                if position in self.picked_piece.valid_moves:
                    self._handle_move(self.picked_piece.position, position)
                self.board.cells[self.picked_piece.position].unmark()
                self.picked_piece = None
            else:
                self.current_pointer = None
                for pointer in self.pointers:
                    pointer.kill()
                self.pointers.clear()
        elif event.button == 3 and position:
            if self.color == PieceColor.BLACK:
                start = 7 - position[0], 7 - position[1]
            else:
                start = position
            self.current_pointer = Pointer(start, start)
            self.pointers.append(self.current_pointer)
            self.sprites.add(self.current_pointer)
            self.sprites.change_layer(self.current_pointer, 2)

    def _handle_mouse_up(self, event: pygame.event.Event) -> None:
        mouse_position: Tuple[float, float] = event.pos
        position = self.board.get_board_cell(mouse_position)

        if event.button == 1 and self.dragged_piece:
            if position in self.dragged_piece.valid_moves:
                self._handle_move(self.dragged_piece.position, position)
                self.picked_piece = None
            elif position != self.dragged_piece.position:
                ILLEGAL_MOVE.play()
            self.sprites.change_layer(self.dragged_piece, 1)
            self.dragged_piece = None
        elif event.button == 3 and self.current_pointer:
            self.current_pointer = None

    def _handle_mouse_motion(self, event: pygame.event.Event) -> None:
        mouse_position: Tuple[float, float] = event.pos
        position = self.board.get_board_cell(mouse_position)

        if self.dragged_piece:
            self.dragged_piece.rect.center = mouse_position
            if not position:
                ILLEGAL_MOVE.play()
                self.dragged_piece = None
        elif self.current_pointer:
            if not position:
                self.pointers.remove(self.current_pointer)
                self.current_pointer.kill()
                self.current_pointer = None
            else:
                start, _ = self.current_pointer.position
                if self.color == PieceColor.BLACK:
                    end = 7 - position[0], 7 - position[1]
                else:
                    end = position
                self.current_pointer.position = start, end

    def _handle_move(self, current_position: Tuple[int, int],
                     new_position: Tuple[int, int]) -> None:
        if self._check_promote(current_position, new_position):
            self.promote = current_position, new_position
        else:
            self._make_move(current_position, new_position)

    def _check_promote(self, current_position: Tuple[int, int],
                       new_position: Tuple[int, int]) -> bool:
        piece = self.board.pieces.get(current_position)
        _, new_rank = new_position

        return isinstance(piece, Pawn) and new_rank in [0, 7]

    def _make_move(self, current_position: Tuple[int, int],
                   new_position: Tuple[int, int],
                   promote_str: Optional[str] = None) -> None:
        piece = self.board.pieces[current_position]
        match promote_str:
            case 'n': promote_piece = Knight(piece.position, piece.color)
            case 'b': promote_piece = Bishop(piece.position, piece.color)
            case 'r': promote_piece = Rook(piece.position, piece.color)
            case 'q': promote_piece = Queen(piece.position, piece.color)
            case _: promote_piece = None

        if promote_piece:
            piece.kill()
            self.sprites.add(promote_piece)
            self.board.pieces[current_position] = promote_piece

        move = self.board.make_move(current_position, new_position)
        check = self.board.is_king_checked(PieceColor(1 - piece.color.value))

        if piece.color == self.color:
            self.move_to_send = current_position, new_position, promote_str
            self.current_pointer = None
            for pointer in self.pointers:
                pointer.kill()
            self.pointers.clear()

        if promote_piece:
            self._play_move_sound('promote', check)
        else:
            self._play_move_sound(move, check)

        self._change_turn()

    def _play_move_sound(self, move: str, check: bool) -> None:
        if check:
            CHECK.play()
        elif move == 'promote':
            PROMOTE.play()
        elif move == 'castle':
            CASTLE.play()
        elif move == 'capture':
            CAPTURE.play()
        elif self.color != self.board.turn:
            MOVE_OPPONENT.play()
        else:
            MOVE.play()

    def _change_turn(self) -> None:
        self.board.turn = PieceColor(1 - self.board.turn.value)
        self.board.update_pieces_moves(self.board.turn)

    def _check_game_over(self) -> None:
        if self.game_over:
            return

        color = self.board.turn
        moves = []
        for piece in self.board.pieces.values():
            if piece.color == color:
                moves.extend(piece.valid_moves)
        if not moves:
            self.game_over = True
            if self.board.is_king_checked(color):
                winner = 'White' if color == PieceColor.BLACK else 'Black'
                self.game_over_info = f'{winner} wins by checkmate'
            else:
                self.game_over_info = 'Draw by stalemate'
            GAME_END.play()
            return

        if self.board.moves_count['half'] >= 50:
            self.game_over = True
            self.game_over_info = 'Draw by fifty-move rule'
            GAME_END.play()
            return

        white_mate_pieces = 0
        white_knights = 0
        white_light_bishops = 0
        white_dark_bishops = 0
        white_pieces = white_mate_pieces + white_knights +\
            white_light_bishops + white_dark_bishops

        black_mate_pieces = 0
        black_knights = 0
        black_light_bishops = 0
        black_dark_bishops = 0
        black_pieces = black_mate_pieces + black_knights +\
            black_light_bishops + black_dark_bishops

        for piece in self.board.pieces.values():
            if piece.color == PieceColor.WHITE:
                if isinstance(piece, Knight):
                    white_knights += 1
                elif isinstance(piece, Bishop):
                    if sum(piece.position) % 2 == 0:
                        white_light_bishops += 1
                    else:
                        white_dark_bishops += 1
                elif not isinstance(piece, King):
                    white_mate_pieces += 1
            else:
                if isinstance(piece, Knight):
                    black_knights += 1
                elif isinstance(piece, Bishop):
                    if sum(piece.position) % 2 == 0:
                        black_light_bishops += 1
                    else:
                        black_dark_bishops += 1
                elif not isinstance(piece, King):
                    black_mate_pieces += 1

        white_insufficient = white_mate_pieces == 0 and\
            (((white_light_bishops == 0 or white_dark_bishops == 0) and
                white_knights == 0) or
             ((white_light_bishops + white_dark_bishops) == 0 and
                 white_knights == 2 and black_pieces == 0) or
             ((white_light_bishops + white_dark_bishops) == 0 and
              white_knights == 1))
        black_insufficient = black_mate_pieces == 0 and\
            (((black_light_bishops == 0 or black_dark_bishops == 0) and
                black_knights == 0) or
             ((black_light_bishops + black_dark_bishops) == 0 and
                 black_knights == 2 and white_pieces == 0) or
             ((black_light_bishops + black_dark_bishops) == 0 and
              black_knights == 1))

        if white_insufficient and black_insufficient:
            self.game_over = True
            self.game_over_info = 'Draw by insufficient material'
            GAME_END.play()

    def _set_initial_sprites(self) -> None:
        for cell in self.board.cells.values():
            self.sprites.add(cell)
            self.sprites.change_layer(cell, 0)
        for piece in self.board.pieces.values():
            self.sprites.add(piece)
            self.sprites.change_layer(piece, 1)

    def _set_sprites_coordinates(self) -> None:
        self._set_cells_coordinates()
        self._set_pieces_coordinates()
        self._set_pointers_coordinates()

    def _set_pieces_coordinates(self) -> None:
        width, height = self.screen.get_size()
        x_offset = (width - BOARD_SIZE) // 2 + FILES_SIZE
        y_offset = (height - BOARD_SIZE) // 2 + FILES_SIZE

        for position, piece in self.board.pieces.items():
            file, rank = position
            if self.color == PieceColor.BLACK:
                file, rank = 7 - file, 7 - rank

            if piece != self.dragged_piece:
                piece.rect.x = x_offset + file * CELL_SIZE + \
                    (CELL_SIZE - piece.rect.width) // 2
                piece.rect.y = y_offset + rank * CELL_SIZE + \
                    (CELL_SIZE - piece.rect.height) // 2

    def _set_cells_coordinates(self) -> None:
        width, height = self.screen.get_size()
        x_offset = (width - BOARD_SIZE) // 2 + FILES_SIZE
        y_offset = (height - BOARD_SIZE) // 2 + FILES_SIZE

        for position, cell in self.board.cells.items():
            file, rank = position
            if self.color == PieceColor.BLACK:
                file, rank = 7 - file, 7 - rank

            cell.rect.x = x_offset + file * CELL_SIZE
            cell.rect.y = y_offset + rank * CELL_SIZE

    def _set_pointers_coordinates(self) -> None:
        width, height = self.screen.get_size()
        x_offset = (width - BOARD_SIZE) // 2 + FILES_SIZE
        y_offset = (height - BOARD_SIZE) // 2 + FILES_SIZE

        for pointer in self.pointers:
            pointer.rect.x = x_offset
            pointer.rect.y = y_offset

    def _draw(self) -> None:
        self.screen.fill(SCREEN_COLOR)
        self._draw_board()
        self._set_sprites_coordinates()
        self.sprites.update()
        self.sprites.draw(self.screen)
        if self.picked_piece:
            self._draw_moves()
        if self.promote:
            self._draw_promotion()
        if self.game_over:
            self._draw_game_over()
        pygame.display.update()

    def _draw_board(self) -> None:
        board = pygame.Surface((BOARD_SIZE, BOARD_SIZE))
        board.fill(BOARD_COLOR)

        self._draw_notation(board)

        width, height = self.screen.get_size()
        self.screen.blit(board, ((width - BOARD_SIZE) // 2,
                                 (height - BOARD_SIZE) // 2))

    def _draw_notation(self, board: pygame.Surface) -> None:
        files = pygame.Surface((PLAY_FIELD_SIZE, FILES_SIZE), pygame.SRCALPHA)
        ranks = pygame.Surface((RANKS_SIZE, PLAY_FIELD_SIZE), pygame.SRCALPHA)
        font = pygame.font.Font(pygame.font.get_default_font(), FONT_SIZE)

        for i in range(8):
            shift = 7 - i if self.color == PieceColor.BLACK else i
            file, rank = chr(ord('a') + shift), str(8 - shift)
            letter = font.render(file, 1, TEXT_COLOR)
            number = font.render(rank, 1, TEXT_COLOR)

            letter_x = i * CELL_SIZE + \
                (CELL_SIZE - letter.get_rect().width) // 2
            letter_y = (FILES_SIZE - letter.get_rect().height) // 2

            number_x = (RANKS_SIZE - letter.get_rect().width) // 2
            number_y = i * CELL_SIZE + \
                (CELL_SIZE - number.get_rect().height) // 2

            files.blit(letter, (letter_x, letter_y))
            ranks.blit(number, (number_x, number_y))

        board.blit(ranks, (0, files.get_height()))
        board.blit(ranks, (ranks.get_width() +
                   CELL_SIZE * 8, files.get_height()))
        board.blit(files, (ranks.get_width(), 0))
        board.blit(files, (ranks.get_width(),
                   ranks.get_width() + CELL_SIZE * 8))

    def _draw_moves(self) -> None:
        width, height = self.screen.get_size()
        moves = self.picked_piece.valid_moves
        for move in moves:
            cell = self.board.cells[move]
            surface = pygame.Surface((width, height), pygame.SRCALPHA)
            piece = self.board.pieces.get(move)
            if piece:
                pygame.draw.circle(surface, MOVE_DOT_COLOR,
                                   cell.rect.center, CELL_SIZE // 2, 8)
            else:
                pygame.draw.circle(surface, MOVE_DOT_COLOR,
                                   cell.rect.center, CELL_SIZE // 7)
            self.screen.blit(surface, (0, 0))

    def _draw_promotion(self) -> None:
        width, height = self.screen.get_size()
        surface = pygame.Surface((CELL_SIZE * 8, CELL_SIZE * 8),
                                 pygame.SRCALPHA)
        surface.fill(INACTIVE_BOARD_COLOR)
        self.screen.blit(surface, ((width // 2) - CELL_SIZE * 4,
                                   (height // 2) - CELL_SIZE * 4))

        promote_box = pygame.Surface((CELL_SIZE * 2, CELL_SIZE * 2),
                                     pygame.SRCALPHA)
        queen = WHITE_QUEEN if self.color == PieceColor.WHITE else BLACK_QUEEN
        rook = WHITE_ROOK if self.color == PieceColor.WHITE else BLACK_ROOK
        bishop = WHITE_BISHOP if self.color == PieceColor.WHITE\
            else BLACK_BISHOP
        knight = WHITE_KNIGHT if self.color == PieceColor.WHITE\
            else BLACK_KNIGHT

        promote_box.fill(PROMOTE_BOX_COLOR)
        promote_box.blit(queen, (0, 0))
        promote_box.blit(rook, (CELL_SIZE, 0))
        promote_box.blit(bishop, (0, CELL_SIZE))
        promote_box.blit(knight, (CELL_SIZE, CELL_SIZE))

        self.screen.blit(promote_box, ((width // 2) - CELL_SIZE,
                                       (height // 2) - CELL_SIZE))

    def _draw_game_over(self) -> None:
        width, height = self.screen.get_size()
        surface = pygame.Surface((CELL_SIZE * 8, CELL_SIZE * 8),
                                 pygame.SRCALPHA)
        surface.fill(INACTIVE_BOARD_COLOR)
        self.screen.blit(surface, ((width // 2) - CELL_SIZE * 4,
                                   (height // 2) - CELL_SIZE * 4))

        game_over_surface = pygame.Surface((CELL_SIZE * 8, CELL_SIZE * 4),
                                           pygame.SRCALPHA)
        game_over_surface.fill(GAME_OVER_BOX_COLOR)
        game_over_font = pygame.font.Font(pygame.font.get_default_font(),
                                          GAME_OVER_FONT_SIZE)
        font = pygame.font.Font(pygame.font.get_default_font(), FONT_SIZE)

        game_over = game_over_font.render(self.game_over_info, 1, TEXT_COLOR)
        return_info = font.render('Tap anywhere to exit', 1, TEXT_COLOR)

        game_over_rect = game_over.get_rect(center=(CELL_SIZE * 4,
                                                    3 * CELL_SIZE // 2))
        return_info_rect = return_info.get_rect(center=(CELL_SIZE * 4,
                                                        5 * CELL_SIZE // 2))

        game_over_surface.blit(game_over, game_over_rect)
        game_over_surface.blit(return_info, return_info_rect)

        self.screen.blit(game_over_surface, ((width // 2) - CELL_SIZE * 4,
                                             (height // 2) - CELL_SIZE * 2))
