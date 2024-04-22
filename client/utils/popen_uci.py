"""Module with utility function that starts chess engine"""
from typing import Tuple
import asyncio

from bot.uci_protocol import UCIProtocol, InvalidUCIEngineError


async def popen_uci(engine_path: str) -> Tuple[asyncio.SubprocessTransport,
                                               UCIProtocol]:
    """Starts UCI compatible chess engine as a background process

    Args:
        engine_path (str): Path to the UCI compatible engine

    Raises:
        InvalidUCIEngineError: Raises when function was given invalid engine

    Returns:
        Tuple[asyncio.SubprocessTransport, UCIProtocol]:\
            Transport and protocol instances\
                for communication with chess engine
    """
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.subprocess_exec(UCIProtocol, engine_path)

    try:
        await protocol.uci()
        await protocol.ping()
    except AssertionError as exc:
        raise InvalidUCIEngineError('Invalid UCI engine') from exc

    return transport, protocol
