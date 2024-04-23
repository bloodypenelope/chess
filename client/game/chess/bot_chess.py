"""Module that describes bot chess game's instance"""
import asyncio

import pygame

from game.model.pieces.piece import PieceColor
from game.chess.chess import Chess
from bot.uci_protocol import UCIProtocol
from utils.popen_uci import popen_uci


class BotChess(Chess):
    """Class for bot chess game's instance"""

    def __init__(self, screen: pygame.Surface, color: PieceColor,
                 fen: str, engine: str, difficulty: int) -> None:
        super().__init__(screen, color, fen)
        self.engine = engine
        self.transport: asyncio.SubprocessTransport = None
        self.protocol: UCIProtocol = None
        self.difficulty = difficulty

    async def mainloop(self) -> None:
        """Starts game's main loop"""
        self.running = True

        while self.running:
            self._handle_input()
            self._draw()
            await self._game_logic()
            self.clock.tick(60)
        self.transport.close()

    async def _game_logic(self) -> None:
        if not self.transport:
            self.transport, self.protocol = await popen_uci(self.engine)
            self.protocol.limit_strength()
            self.protocol.set_skill_level(self.difficulty)
            fisher = 'K' not in self.board.castle_rights[PieceColor.WHITE]
            if fisher:
                self.protocol.fisher_random()

        self._check_game_over()
        if self.game_over:
            return

        if self.color != self.board.turn:
            fen = str(self.board)
            move = await self.protocol.get_best_move(fen, 0.5)

            promote = None
            if len(move) == 5:
                promote = move[-1]
            cur_pos_file, cur_pos_rank = move[0], move[1]
            new_pos_file, new_pos_rank = move[2], move[3]

            cur_pos_rank = 8 - int(cur_pos_rank)
            new_pos_rank = 8 - int(new_pos_rank)

            cur_pos_file = ord(cur_pos_file) - ord('a')
            new_pos_file = ord(new_pos_file) - ord('a')

            cur_pos = cur_pos_file, cur_pos_rank
            new_pos = new_pos_file, new_pos_rank
            self._make_move(cur_pos, new_pos, promote)
