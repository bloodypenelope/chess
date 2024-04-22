from typing import Dict
import logging
import json

import pygame

from game.menu import MainMenu


def main():
    with open('config.json', mode='rb') as file:
        data: Dict[str, Dict] = json.load(file)
        server: Dict[str, str | int] = data['server']
        engine: str = data['engine']

        log_config: Dict[str, str] = data['log_config']
        log_file: str = log_config['log_file']
        log_format: str = log_config['log_format']
        log_datefmt: str = log_config['log_datefmt']

    logging.basicConfig(filename=log_file,
                        filemode='a',
                        format=log_format,
                        datefmt=log_datefmt,
                        level=logging.DEBUG)

    pygame.init()
    icon = pygame.image.load('assets\\icon.svg')
    screen = pygame.display.set_mode((800, 800), pygame.RESIZABLE)
    screen.fill('gray')
    pygame.display.set_caption('Chess')
    pygame.display.set_icon(icon)

    menu = MainMenu(screen, server, engine)
    menu.mainloop()


if __name__ == '__main__':
    main()
