"""Module with UCI protocol implementation"""
from typing import Optional
import asyncio
import logging


class InvalidUCIEngineError(Exception):
    """Error that raises when invalid or\
        incompatible with UCI protocol engine was passed"""


class UCIProtocol(asyncio.SubprocessProtocol):
    """Cheap implementation of UCI protocol"""

    def __init__(self) -> None:
        self._transport: Optional[asyncio.SubprocessTransport] = None
        self._response = asyncio.Queue()
        self._logger = logging.getLogger('uci')
        self._buffer = {
            1: bytearray(),
            2: bytearray()
        }

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        self._transport = transport

    def pipe_data_received(self, fd: int, data: bytes) -> None:
        self._buffer[fd].extend(data)
        while b'\n' in self._buffer[fd]:
            line_bytes, self._buffer[fd] = self._buffer[fd].split(b'\n', 1)
            if line_bytes.endswith(b'\r'):
                line_bytes = line_bytes[:-1]
            line = line_bytes.decode()

            if fd == 1:
                self._line_received(line)
            else:
                self._error_line_received(line)

    def _line_received(self, line: str) -> None:
        self._logger.info('stdout >> %s', line)
        if line in ('uciok', 'readyok'):
            self._response.put_nowait(line)
        if line.startswith('bestmove'):
            self._response.put_nowait(line.split(' ')[1])

    def _error_line_received(self, line: str) -> None:
        self._logger.error('stderr >> %s', line)

    def _send_line(self, line: str) -> None:
        stdin = self._transport.get_pipe_transport(0)
        stdin.write((line + '\n').encode())
        self._logger.info('stdin << %s', line)

    async def _get_response(self, timeout: int = 1) -> str:
        try:
            response = await asyncio.wait_for(self._response.get(),
                                              timeout=timeout)
            return response
        except TimeoutError:
            return "error: time limit exceeded"

    async def uci(self) -> None:
        """Tells engine to work in UCI mode"""
        self._send_line('uci')
        response = await self._get_response()
        assert response == 'uciok'

    async def ping(self) -> None:
        """Pings chess engine"""
        self._send_line('isready')
        response = await self._get_response()
        assert response == 'readyok'

    def limit_strength(self) -> None:
        """Allows engine to limit its strength"""
        self._send_line('setoption name UCI_LimitStrength value true')

    def fisher_random(self) -> None:
        """Tells engine to play in Fisher random mode"""
        self._send_line('setoption name UCI_Chess960 value true')

    def set_skill_level(self, difficulty: int = 20) -> None:
        """Sets skill level of an engine. Ranges from 0 to 20

        Args:
            difficulty (int): Skill level. Defaults to 20
        """
        self._send_line(f'setoption name Skill Level value {difficulty}')

    async def get_best_move(self, fen: str, limit: int = 1) -> str:
        """Gets engine's best move in the position

        Args:
            fen (str): Current position in FEN notation
            limit (int): Limit of search time in seconds. Defaults to 1

        Returns:
            str: Best move in a long algebraic notation
        """
        self._send_line(f'position fen {fen}')
        self._send_line(f'go movetime {int(limit * 1000)}')
        return await self._get_response(timeout=limit + 1)
