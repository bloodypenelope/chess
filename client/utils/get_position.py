"""Module with utility functions that generate\
    starting position of a chess game"""
import random


def get_classic_fen() -> str:
    """Generates starting position of a classic chess in FEN notation

    Returns:
        str: FEN string of a starting position
    """
    rank = 'rnbqkbnr'
    pawns = 'p' * 8

    position = f'{rank}/{pawns}/8/8/8/8/{pawns.upper()}/{rank.upper()}'
    game_info = 'w KQkq - 0 1'
    fen = f'{position} {game_info}'

    return fen


def get_fisher_fen() -> str:
    """Generates starting position for Fisher chess in FEN notation

    Returns:
        str: FEN string of a starting position
    """
    light_bishop = random.randint(0, 3) * 2
    dark_bishop = random.randint(0, 3) * 2 + 1

    files = [i for i in range(8) if i not in (light_bishop, dark_bishop)]
    random.shuffle(files)
    first_knight, second_knight, queen = files[:3]
    first_rook, king, second_rook = sorted(files[3:])
    rook_files_chars = f'{chr(ord('A') + first_rook)}' +\
        f'{chr(ord('A') + second_rook)}'

    rank = [""] * 8
    rank[light_bishop], rank[dark_bishop] = 'b', 'b'
    rank[first_knight], rank[second_knight] = 'n', 'n'
    rank[first_rook], rank[second_rook] = 'r', 'r'
    rank[queen], rank[king] = 'q', 'k'

    rank = "".join(rank)
    pawns = 'p' * 8

    position = f'{rank}/{pawns}/8/8/8/8/{pawns.upper()}/{rank.upper()}'
    game_info = f'w {rook_files_chars}{rook_files_chars.lower()} - 0 1'
    fen = f'{position} {game_info}'

    return fen


if __name__ == '__main__':
    print(get_fisher_fen())
