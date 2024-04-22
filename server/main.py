from typing import Tuple, Dict
import logging
import asyncio
import json

from server import ChessServer


async def main():
    with open('config.json', mode='rb') as file:
        data: Dict[str, Dict] = json.load(file)

        server: Dict[str, str | int] = data['server']
        server_address: Tuple[str, int] = server['host'], server['port']
        recv_size: int = server['recv_size']

        log_config: Dict[str, str] = data['log_config']
        log_file: str = log_config['log_file']
        log_format: str = log_config['log_format']
        log_datefmt: str = log_config['log_datefmt']

    logging.basicConfig(filename=log_file,
                        filemode='a',
                        format=log_format,
                        datefmt=log_datefmt,
                        level=logging.DEBUG)

    chess_server = ChessServer(server_address, recv_size)
    await chess_server.start_server()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
