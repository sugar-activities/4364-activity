#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Bala.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   Uruguay

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import pygame
from math import sin
from math import cos
from math import radians

from pygame.sprite import Sprite

VELOCIDAD = 18


class Bala(Sprite):

    def __init__(self, angulo, x, y, image_path, resolucion, ip):

        Sprite.__init__(self)

        self.ip = ip
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()

        self.angulo = angulo
        self.ancho_monitor, self.alto_monitor = resolucion
        self.dx, self.dy = self.__get_vector(angulo)
        self.temp_x = x + self.dx
        self.temp_y = y + self.dy
        self.rect.centerx = self.temp_x
        self.rect.centery = self.temp_y

    def __get_vector(self, angulo):
        dx = int(cos(radians(angulo)) * VELOCIDAD)
        dy = int(sin(radians(angulo)) * VELOCIDAD)
        return dx, dy

    def get_datos(self):
        return (self.angulo, self.temp_x, self.temp_y)

    def set_posicion(self, centerx=0, centery=0):
        self.rect.centerx = centerx
        self.rect.centery = centery
        if centerx > 0 and centerx < self.ancho_monitor and \
            centery > 0 and centery < self.alto_monitor:
                return True
        else:
            self.kill()
            return False

    def update(self):
        x = self.rect.centerx + self.dx
        y = self.rect.centery + self.dy
        self.temp_x = int(x)
        self.temp_y = int(y)
