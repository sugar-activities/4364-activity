#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Jugador.py por:
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

VELOCIDAD = 10
INDICE_ROTACION = 5


class Jugador(Sprite):

    def __init__(self, imagen_path, resolucion, ip):

        Sprite.__init__(self)

        #path = os.path.dirname(os.path.dirname(imagen_path))
        #motor2 = os.path.join(path, "Audio", "motor2.ogg")
        #disparo = pygame.mixer.Sound(motor2)
        #disparo.play(-1)

        self.ip = ip
        self.eventos = []

        self.imagen_original = None
        self.image = None
        self.rect = None

        self.imagen_path = imagen_path
        imagen = pygame.image.load(self.imagen_path)
        imagen_escalada = pygame.transform.scale(imagen, (50, 50))
        self.imagen_original = imagen_escalada.convert_alpha()

        self.image = self.imagen_original.copy()
        self.rect = self.image.get_rect()

        self.ancho_monitor, self.alto_monitor = resolucion
        self.centerx = self.ancho_monitor / 2
        self.centery = self.alto_monitor / 2

        self.angulo = 0
        # distancia en x,y
        self.dx, self.dy = self.__get_vector(self.angulo)

        self.temp_image = None
        self.temp_angulo = 0
        self.temp_x = self.ancho_monitor / 2
        self.temp_y = self.alto_monitor / 2

        self.__set_posicion(angulo=0, centerx=self.temp_x, centery=self.temp_y)

    def __derecha(self):
        self.temp_angulo += int(0.7 * INDICE_ROTACION)

    def __izquierda(self):
        self.temp_angulo -= int(0.7 * INDICE_ROTACION)

    def __arriba(self):
        self.dx, self.dy = self.__get_vector(self.temp_angulo)
        self.__actualizar_posicion()

    def __abajo(self):
        x, y = self.__get_vector(self.temp_angulo)
        self.dx = x * -1
        self.dy = y * -1
        self.__actualizar_posicion()

    def __get_vector(self, angulo):
        """
        Recibe un ángulo que da orientación al tanque.
        Devuelve el incremento de puntos x,y en su desplazamiento.
        """
        radianes = radians(angulo)
        x = int(cos(radianes) * VELOCIDAD)
        y = int(sin(radianes) * VELOCIDAD)
        return x, y

    def __actualizar_posicion(self):
        """
        Cambia la posicion del rectangulo.
        Solo se ejecuta si el tanque se mueve hacia adelante o hacia atras.
        No se ejecuta cuando está girando en un mismo lugar.
        """
        x = self.centerx + self.dx
        y = self.centery + self.dy
        ancho = range(25, self.ancho_monitor - 25)
        alto = range(25, self.alto_monitor - 25)
        if x in ancho and y in alto:
            self.temp_x += self.dx
            self.temp_y += self.dy
            self.temp_x = int(self.temp_x)
            self.temp_y = int(self.temp_y)

    def __set_posicion(self, angulo=0, centerx=0, centery=0):
        """
        Actualiza los datos según lo recibido desde el server.
        """
        self.temp_angulo = angulo
        self.temp_x = centerx
        self.temp_y = centery

        self.angulo = angulo
        self.centerx = centerx
        self.centery = centery

        self.rect.centerx = self.centerx
        self.rect.centery = self.centery

        self.image = pygame.transform.rotate(
            self.imagen_original, -self.angulo)

    def get_datos(self):
        """
        Solo Jugador Local.
        """
        return (int(self.temp_angulo), int(self.temp_x), int(self.temp_y))

    def update_data(self, tanque, angulo=0, centerx=0, centery=0):
        if self.imagen_path != tanque:
            self.imagen_path = tanque
            imagen = pygame.image.load(self.imagen_path)
            imagen_escalada = pygame.transform.scale(imagen, (50, 50))
            self.imagen_original = imagen_escalada.convert_alpha()
            self.image = self.imagen_original.copy()
            self.rect = self.image.get_rect()
        self.__set_posicion(angulo=angulo, centerx=centerx, centery=centery)

    def update_events(self, eventos):
        """
        Solo Jugador Local.
        """
        self.eventos = list(eventos)

    def update(self):
        """
        Solo Jugador Local.
        """
        if not self.eventos:
            return

        # girar en movimiento
        if "w" in self.eventos and "d" in self.eventos:
            self.__arriba()
            self.__derecha()
        elif "w" in self.eventos and "a" in self.eventos:
            self.__arriba()
            self.__izquierda()
        elif "s" in self.eventos and "d" in self.eventos:
            self.__abajo()
            self.__izquierda()
        elif "s" in self.eventos and "a" in self.eventos:
            self.__abajo()
            self.__derecha()

        # moverse sin girar
        elif "w" in self.eventos:
            self.__arriba()
        elif "s" in self.eventos:
            self.__abajo()

        # girar sin moverse
        elif "d" in self.eventos:
            self.__derecha()
        elif "a" in self.eventos:
            self.__izquierda()
