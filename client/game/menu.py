"""Module for chess game's menu screens"""
from typing import Optional, Dict
from abc import ABC, abstractmethod
import asyncio
import sys

import pygame
import pygame_menu
import pygame_menu.baseimage
import pygame_menu.menu
import pygame_menu.themes
import pygame_menu.font
import pygame_menu.events
import pygame_menu.widgets

from game.model.pieces.piece import PieceColor, CELL_SIZE
from game.chess.local_chess import LocalChess
from game.chess.bot_chess import BotChess
# from game.chess.online_chess import OnlineChess
from utils.get_position import get_classic_fen, get_fisher_fen

WHITE_KING = 'assets\\images\\white_king.png'
BLACK_KING = 'assets\\images\\black_king.png'
SELECT_SIDE_COLOR = (255, 255, 255, 255)


class MenuTheme(pygame_menu.themes.Theme):
    """Class for menu theme object"""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.background_color = (93, 153, 72, 255)
        self.title = False

        self.widget_font = pygame_menu.font.FONT_OPEN_SANS_BOLD
        self.widget_font_size = 30
        self.widget_font_color = (50, 50, 50)
        self.widget_font_shadow_color = (0, 0, 0)
        self.widget_padding = 10


class Menu(ABC):
    """Abstract class for menu object"""

    def __init__(self, screen: pygame.Surface, title: str,
                 prev_menu=None, scale: tuple = (1, 1)) -> None:
        self.clock = pygame.time.Clock()
        self.screen = screen
        self.scale = scale
        self.menu: pygame_menu.Menu = pygame_menu.menu.Menu(
            title, 1, 1, theme=MenuTheme())
        self.prev_menu: Optional[Menu] = prev_menu
        self.running = False
        self.resize()
        self._add_widgets()

    def mainloop(self):
        """Starts menu's main loop"""
        self.running = True

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                elif event.type == pygame.VIDEORESIZE:
                    self.resize()
                self.menu.update([event])

            self.menu.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(60)

    def resize(self) -> None:
        """Adjusts menu size to the screen"""
        size = self.screen.get_size()
        width, height = map(lambda x, y: x * y, size, self.scale)
        self.menu.resize(width, height)

    def back(self) -> None:
        """Stops current menu and goes back to the previous one"""
        self.running = False
        if self.prev_menu:
            self.prev_menu.resize()

    @abstractmethod
    def _add_widgets(self) -> None:
        pass


class MainMenu(Menu):
    """Class for main menu of the chess game"""

    def __init__(self, screen: pygame.Surface,
                 server: Dict[str, str | int], engine: str) -> None:
        super().__init__(screen, 'Chess')
        self.select_mode_menu = SelectMode(self.screen, server, engine, self)

    def select_mode(self) -> None:
        """Goes to the select game mode menu"""
        self.select_mode_menu.resize()
        self.select_mode_menu.mainloop()

    def _add_widgets(self) -> None:
        self.menu.add.label('Chess', font_size=100).translate(0, -100)
        self.menu.add.button('Play', self.select_mode, font_size=50)
        self.menu.add.button('Quit', self.back)


class SelectMode(Menu):
    """Class for select game mode menu of the chess game"""

    def __init__(self, screen: pygame.Surface, server: Dict[str, str | int],
                 engine: str, prev_menu: MainMenu) -> None:
        super().__init__(screen, 'Select mode', prev_menu=prev_menu)
        self.fisher = False
        self.bot_config_menu = BotConfig(self.screen, engine, self)
        self.queue_menu = None

    def set_fisher(self, state: bool) -> None:
        """Sets fisher random mode"""
        self.fisher = state

    def start_local_game(self) -> None:
        """Starts local game"""
        fen = get_fisher_fen() if self.fisher else get_classic_fen()
        chess = LocalChess(self.screen, fen)
        chess.mainloop()
        self.resize()

    def bot_config(self) -> None:
        """Goes to the bot config menu"""
        self.bot_config_menu.set_fisher(self.fisher)
        self.bot_config_menu.resize()
        self.bot_config_menu.mainloop()

    # TODO: online :)
    def queue(self) -> None:
        pass

    def _add_widgets(self) -> None:
        self.menu.add.label('Select mode', font_size=100).translate(0, -100)
        self.menu.add.button('Local', self.start_local_game, font_size=40)
        self.menu.add.button('Computer', self.bot_config, font_size=40)
        self.menu.add.button('Online', self.queue, font_size=40)
        self.menu.add.button('Back', self.back)
        self.menu.add.toggle_switch('Fisher Random', onchange=self.set_fisher)


class BotConfig(Menu):
    """Class for bot config menu of the chess game"""

    def __init__(self, screen: pygame.Surface,
                 engine: str, prev_menu: Menu) -> None:
        self.white: pygame_menu.widgets.Image = None
        self.black: pygame_menu.widgets.Image = None
        self._bot_difficulty = 0
        self.color: PieceColor = None
        super().__init__(screen, 'Bot config', prev_menu=prev_menu)
        self.engine = engine
        self.fisher = False

    @property
    def bot_difficulty(self) -> int:
        """Property that contains bot's difficulty

        Returns:
            int: Bot's difficulty
        """
        return self._bot_difficulty

    @bot_difficulty.setter
    def bot_difficulty(self, difficulty: int) -> None:
        self._bot_difficulty = difficulty

    def set_fisher(self, state: bool) -> None:
        """Sets Fisher random mode"""
        self.fisher = state

    def start_bot_game(self) -> None:
        """Starts bot game"""
        if self.color:
            fen = get_fisher_fen() if self.fisher else get_classic_fen()
            chess = BotChess(self.screen, self.color, fen,
                             self.engine, self.bot_difficulty)
            asyncio.run(chess.mainloop())
            self.resize()

    def set_color_white(self) -> None:
        """Sets color of your pieces to white"""
        if self.white and self.black:
            self.color = PieceColor.WHITE
            self.white.shadow(shadow_type='ellipse', shadow_width=30,
                              color=SELECT_SIDE_COLOR)
            self.black.shadow(shadow_width=0)

    def set_color_black(self) -> None:
        """Sets color of your pieces to black"""
        if self.white and self.black:
            self.color = PieceColor.BLACK
            self.black.shadow(shadow_type='ellipse', shadow_width=30,
                              color=SELECT_SIDE_COLOR)
            self.white.shadow(shadow_width=0)

    def _add_widgets(self) -> None:
        self.menu.add.label('Bot config', font_size=100).translate(0, -100)
        self.white = self.menu.add.image(WHITE_KING,
                                         onselect=self.set_color_white,
                                         selectable=True)\
            .resize(CELL_SIZE, CELL_SIZE).translate(-100, 0)\
            .shadow(shadow_type='ellipse', shadow_width=30,
                    color=SELECT_SIDE_COLOR)
        self.black = self.menu.add.image(BLACK_KING,
                                         onselect=self.set_color_black,
                                         selectable=True)\
            .resize(CELL_SIZE, CELL_SIZE).translate(100, -100)
        self.menu.add.range_slider('Bot difficulty', 0, list(range(21)), 1,
                                   range_text_value_enabled=False,
                                   onchange=self.bot_difficulty)\
            .translate(0, -75)
        self.menu.add.button('Start Game', self.start_bot_game,
                             font_size=40).translate(0, -75)
        self.menu.add.button('Back', self.back).translate(0, -75)
