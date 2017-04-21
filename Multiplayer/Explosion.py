#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Explosion.py por:
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

import os
import pygame

from pygame.sprite import Sprite


class Explosion(Sprite):

    def __init__(self, x, y, dir_path):

        Sprite.__init__(self)

        self.contador = 0
        self.valor = 1

        self.imagenes = []
        archivos = sorted(os.listdir(dir_path))
        for arch in archivos:
            path = os.path.join(dir_path, arch)
            imagen = pygame.image.load(path)
            self.imagenes.append(imagen)

        self.image = self.imagenes[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        #self.sonido_explosion = sonido_explosion
        #self.sonido_explosion.play()

    def update(self):
        self.contador += self.valor
        self.image = self.imagenes[self.contador]
        if self.contador == len(self.imagenes) - 1:
            self.valor = -1
        else:
            if self.contador < 1:
                self.kill()
                del(self)
