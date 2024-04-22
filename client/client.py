"""Module with chess game's client implementation"""
from typing import Tuple
import asyncio
import logging
import socket
import json


class ChessClient:
    """Class that describes chess game's client"""

    def __init__(self, address: Tuple[str, int], recv_size: int) -> None:
        self._host, self._port = address
        self._recv_size = recv_size
        self._logger = logging.getLogger('client')
        self._reader, self._writer = None, None
        self._connected = False

    @property
    def address(self) -> Tuple[str, int]:
        """Property that contains server's address

        Returns:
            Tuple[str, int]: Tuple of hostname and port of the server
        """
        return self._host, self._port

    @property
    def connected(self) -> bool:
        """Property that indicates if client is connected or not

        Returns:
            bool: True if client is connected, False otherwise
        """
        return self._connected

    async def connect(self) -> None:
        """Connects client to the server"""
        if self._writer:
            raise ConnectionError('Already connected')

        try:
            self._logger.info('Connecting to the server...')
            self._reader, self._writer = await asyncio.open_connection(
                *self.address)
            self._logger.info('Connected to the server')
            self._connected = True
        except (ConnectionRefusedError, socket.gaierror):
            self._logger.error('Could not connect to the server')

    async def disconnect(self) -> None:
        """Disconnects client from the server"""
        if not self._writer:
            raise ConnectionError('Connection is not establised yet')

        try:
            self._logger.info('Disconnecting from the server...')
            self._writer.close()
            await self._writer.wait_closed()
            self._logger.info('Disconnected from the server')
        except ConnectionError:
            self._logger.error('Connection is already closed')
        finally:
            self._reader, self._writer = None, None
            self._connected = False

    async def fetch(self, query: dict) -> dict:
        """Fetches data from the server by query

        Args:
            query (dict): Query. For more info check README.md

        Returns:
            dict: Response from the server
        """
        if not self._writer:
            raise ConnectionError('Connection is not established yet')

        try:
            self._writer.write(json.dumps(query).encode())
            await self._writer.drain()
            self._logger.info('Sent query to the server')

            response = await self._reader.read(self._recv_size)
            if not response:
                raise ConnectionError('Lost connection')
            self._logger.info('Received response from the server')

            return json.loads(response)
        except (ConnectionError, json.JSONDecodeError) as exc:
            self._logger.exception('Fetch failed: %s', exc)
            return json.loads({"error": exc})
