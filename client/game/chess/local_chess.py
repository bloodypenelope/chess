"""Module that describes local chess game's instance"""
from typing import override

import pygame

from game.model.pieces.piece import PieceColor
from game.chess.chess import Chess, MOVE, MOVE_OPPONENT, \
    CAPTURE, CHECK, CASTLE, PROMOTE


class LocalChess(Chess):
    """Class for local chess game's instance"""

    def __init__(self, screen: pygame.Surface, fen: str):
        super().__init__(screen, PieceColor.WHITE, fen)

    def mainloop(self) -> None:
        """Starts game's main loop"""
        self.running = True

        while self.running:
            self._handle_input()
            self._draw()
            self._game_logic()
            self.clock.tick(60)

    def _game_logic(self) -> None:
        self._check_game_over()
        if self.game_over:
            return

        if self.color != self.board.turn:
            self.color = self.board.turn

    @override
    def _play_move_sound(self, move: str, check: bool) -> None:
        if check:
            CHECK.play()
        elif move == 'promote':
            PROMOTE.play()
        elif move == 'castle':
            CASTLE.play()
        elif move == 'capture':
            CAPTURE.play()
        elif self.color == PieceColor.BLACK:
            MOVE_OPPONENT.play()
        else:
            MOVE.play()
