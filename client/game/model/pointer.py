"""Module that describes pointers"""
from typing import Tuple

import pygame

from game.model.pieces.piece import CELL_SIZE

POINTER_COLOR = (181, 101, 29, 125)


class Pointer(pygame.sprite.Sprite):
    """Class that describes a pointer on a chessboard"""

    def __init__(self, start: Tuple[int, int], end: Tuple[int, int]) -> None:
        super().__init__()
        self._start = start
        self._end = end

        self.image = pygame.Surface((CELL_SIZE * 8, CELL_SIZE * 8),
                                    pygame.SRCALPHA)
        self.rect = self.image.get_rect()

    @property
    def position(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Property that contains position of a pointer

        Returns:
            Tuple[Tuple[int, int]]: Starting and ending square of a pointer
        """
        return self._start, self._end

    @position.setter
    def position(self, pos: Tuple[Tuple[int, int], Tuple[int, int]]) -> None:
        self._start, self._end = pos

    def update(self) -> None:
        """Updates pointer's sprite"""
        self.image.fill((0, 0, 0, 0))

        if self._start == self._end:
            x_coord = CELL_SIZE * self._start[0] + CELL_SIZE // 2
            y_coord = CELL_SIZE * self._start[1] + CELL_SIZE // 2
            pygame.draw.circle(self.image, POINTER_COLOR,
                               (x_coord, y_coord),
                               CELL_SIZE // 2, 8)
        else:
            start_coord = (CELL_SIZE * self._start[0] + CELL_SIZE // 2,
                           CELL_SIZE * self._start[1] + CELL_SIZE // 2)
            end_coord = (CELL_SIZE * self._end[0] + CELL_SIZE // 2,
                         CELL_SIZE * self._end[1] + CELL_SIZE // 2)

            start = pygame.Vector2(start_coord)
            end = pygame.Vector2(end_coord)
            arrow = start - end
            angle = arrow.angle_to(pygame.Vector2(0, -1))
            head_width, head_height = CELL_SIZE // 3, CELL_SIZE // 3
            body_width, body_length = (CELL_SIZE // 8,
                                       arrow.length() - head_height)

            head_verts = [
                pygame.Vector2(0, head_height / 2),
                pygame.Vector2(head_width / 2, -head_height / 2),
                pygame.Vector2(-head_width / 2, -head_height / 2),
            ]
            translation = pygame.Vector2(0, arrow.length() -
                                         (head_height / 2)).rotate(-angle)
            for i, head_vert in enumerate(head_verts):
                head_vert.rotate_ip(-angle)
                head_verts[i] += translation
                head_verts[i] += start
            pygame.draw.polygon(self.image, POINTER_COLOR, head_verts)

            body_verts = [
                pygame.Vector2(-body_width / 2, body_length / 2),
                pygame.Vector2(body_width / 2, body_length / 2),
                pygame.Vector2(body_width / 2, -body_length / 2),
                pygame.Vector2(-body_width / 2, -body_length / 2)
            ]
            translation = pygame.Vector2(0, body_length / 2).rotate(-angle)
            for i, body_vert in enumerate(body_verts):
                body_vert.rotate_ip(-angle)
                body_verts[i] += translation
                body_verts[i] += start
            pygame.draw.polygon(self.image, POINTER_COLOR, body_verts)
        self.rect = self.image.get_rect(topleft=self.rect.topleft)
