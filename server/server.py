"""Module that describes chess game's server"""
from typing import Tuple, Dict
import asyncio
import logging
import json


# TODO: handler for clients requests
# TODO: implement game queue
class ChessServer:
    """Class that describes chess game's server"""

    def __init__(self, address: Tuple[str, int], recv_size: int):
        self._host, self._port = address
        self._recv_size = recv_size
        self._logger = logging.getLogger('server')
        self._clients: Dict[tuple, asyncio.StreamWriter] = {}
        self._game_queue = asyncio.Queue()
        self._lock = asyncio.Lock()

    @property
    def address(self) -> Tuple[str, int]:
        """Property that contains server's address

        Returns:
            Tuple[str, int]: Server's address
        """
        return self._host, self._port

    async def handle_client(self, reader: asyncio.StreamReader,
                            writer: asyncio.StreamWriter):
        """Coroutine for handing clients

        Args:
            reader (asyncio.StreamReader): Client's StreamReader
            writer (asyncio.StreamWriter): Client's StreamWriter
        """
        client_address: tuple = writer.get_extra_info('peername')
        self._clients[client_address] = writer
        self._logger.info('Client connected: %s', client_address)

        try:
            while True:
                query = await reader.read(self._recv_size)
                if not query:
                    raise ConnectionError(
                        f'Lost connection to client: {client_address}')
                self._logger.info('Received query from %s', client_address)

                response = self.handle_query(query)
                writer.write(response.encode())
                await writer.drain()
        except (ConnectionError, asyncio.CancelledError) as exc:
            self._logger.error('%s', exc)
        finally:
            del self._clients[client_address]
            writer.close()
            await writer.wait_closed()
            self._logger.info('Client disconnected: %s', client_address)

    def handle_query(self, query: bytes) -> str:
        try:
            query: dict = json.loads(query)
            method: str = query['method']
            body = query['body']

            match method:
                case 'ping': return self.handle_ping()
                case 'move': return self.handle_move(body)
                case 'ask': pass
                case _: return json.dumps({'error': 'Invalid method'})
        except (json.JSONDecodeError, KeyError):
            return json.dumps({"error": "Invalid query"})

    def handle_ping(self) -> str:
        return json.dumps({"data": "ping"})

    def handle_move(self, body: dict) -> str:
        pass
        # try:
        #     opponent: str = body['opponent']
        #     move: str = body['move']
        #     response = {"data": "success"}

        #     return json.dumps(response)
        # except KeyError:
        #     return json.dumps({"error": "Invalid body"})

    async def start_server(self):
        """Starts server"""
        server = await asyncio.start_server(self.handle_client, *self.address)

        async with server:
            try:
                self._logger.info('Server started at %s', self.address)
                await server.serve_forever()
            except asyncio.CancelledError:
                self._logger.error('Server was shut down')
