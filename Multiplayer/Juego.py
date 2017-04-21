#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Juego.py por:
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
import random
import platform
import gobject
import gtk

from Jugador import Jugador
from Bala import Bala
from Explosion import Explosion

from Globales import get_ip
from Globales import MAKELOG
from Globales import APPEND_LOG

RESOLUCION_INICIAL = (800, 600)
BASE_PATH = os.path.dirname(__file__)
OLPC = 'olpc' in platform.platform()


def get_model():
    return {
        'nick': '',
        'tanque': '',
        'puntos': 0,
        'explosion': '-,-,-',
        }


class Juego(gobject.GObject):

    __gsignals__ = {
    "update": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, )),
    "end": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))}

    def __init__(self, _dict, client):

        gobject.GObject.__init__(self)

        self.GAME = {}
        self.GAME['mapa'] = str(_dict['mapa'].strip())

        self.sound_disparo = False
        self.sound_juego = False
        self.sound_explosion = False

        self.ip = get_ip()
        self.JUGADORES = {}
        self.JUGADORES[self.ip] = get_model()
        self.JUGADORES[self.ip]['nick'] = str(_dict['nick'].strip())
        self.JUGADORES[self.ip]['tanque'] = str(_dict['tanque'].strip())

        self.BALAS = {}

        self.client = client

        self.resolucionreal = RESOLUCION_INICIAL
        self.escenario = False
        self.ventana = False
        self.reloj = False
        self.estado = False
        self.jugador = False
        self.bala = False
        self.disparo = False

        self.jugadores = pygame.sprite.RenderUpdates()
        self.balas = pygame.sprite.RenderUpdates()
        self.explosiones = pygame.sprite.RenderUpdates()

    def __enviar_datos(self):
        a, x, y = ("-", "-", "-")
        if self.jugador:
            self.jugador.update()
            a, x, y = self.jugador.get_datos()

        datos = "UPDATE,%s,%s,%s" % (a, x, y)
        if self.disparo:
            datos = "%s,%s,%s,%s" % (datos, a, x, y)
            self.disparo = False
        elif self.bala:
            self.bala.update()
            a, x, y = self.bala.get_datos()
            datos = "%s,%s,%s,%s" % (datos, a, x, y)
        else:
            datos = "%s,-,-,-" % datos

        datos = "%s,%s" % (datos, self.JUGADORES[self.ip]["explosion"])
        self.JUGADORES[self.ip]["explosion"] = '-,-,-'

        self.client.enviar(datos)

    def __recibir_datos(self):
        datos = self.client.recibir()

        if not datos:
            print "Se recibió datos vacíos en el Juego"
            return

        if datos == "END":
            self.__end()
            return

        for client in datos.split("||"):
            if not client:
                self.__checkear_colisiones()
                return

            valores = client.split(",")

            # TANQUE
            ip, nick, tanque, a, x, y = valores[0:6]
            if a == '-' and x == '-' and y == '-':
                for j in self.jugadores.sprites():
                    if ip == j.ip:
                        self.__eliminar_jugador(j, ip)
                        break
            else:
                a = int(a)
                x = int(x)
                y = int(y)
                if a == 0 and x == 0 and y == 0:
                    random.seed()
                    a = random.randrange(-360, 360, 1)
                    x = RESOLUCION_INICIAL[0] / 2
                    y = RESOLUCION_INICIAL[1] / 2
                self.__actualizar_tanque(ip, nick, tanque, a, x, y)

            # PUNTAJES
            vidas, energia, puntos = valores[6:9]
            vidas = int(vidas)
            energia = int(energia)
            puntos = int(puntos)
            self.JUGADORES[ip]['vidas'] = vidas
            self.JUGADORES[ip]['energia'] = energia
            self.JUGADORES[ip]['puntos'] = puntos

            # BALA
            aa, xx, yy = valores[9:12]
            if aa == '-' and xx == '-' and yy == '-':
                for bala in self.balas.sprites():
                    if ip == bala.ip:
                        self.__eliminar_bala(bala, ip)
                        break
            else:
                aa = int(aa)
                xx = int(xx)
                yy = int(yy)
                self.__actualizar_bala(ip, aa, xx, yy)

            # EXPLOSIONES
            explosiones = valores[12:]
            if explosiones:
                dirpath = os.path.dirname(os.path.dirname(self.GAME['mapa']))
                dir_path = os.path.join(dirpath, "Explosion")
                for d in range(0, len(explosiones), 2):
                    channel = pygame.mixer.find_channel()
                    if channel:
                        channel.play(self.sound_explosion)
                    self.explosiones.add(Explosion(int(explosiones[d]),
                        int(explosiones[d + 1]), dir_path))

    def __checkear_colisiones(self):
        """
        Checkea colisiones de mi bala con tanques enemigos.
        """
        if self.bala:
            a, x, y = self.bala.get_datos()
            for jugador in self.jugadores.sprites():
                if jugador.ip == self.ip:
                    continue
                if jugador.rect.collidepoint((x, y)):
                    self.__eliminar_bala(self.bala, self.ip)
                    self.JUGADORES[self.ip]["explosion"] = "%s,%s,%s" % (
                        jugador.ip, x, y)
                    break

    def __actualizar_tanque(self, ip, nick, tanque, a, x, y):
        tanque = os.path.join(os.path.dirname(BASE_PATH), "Tanques", tanque)

        if not ip in self.JUGADORES.keys():
            self.JUGADORES[ip] = get_model()

        ips = []
        for j in self.jugadores.sprites():
            if not j.ip in ips:
                ips.append(j.ip)
        if not ip in ips:
            j = Jugador(tanque, RESOLUCION_INICIAL, ip)
            if j.ip == self.ip:
                self.jugador = j
            self.jugadores.add(j)

        for j in self.jugadores.sprites():
            if ip == j.ip:
                self.JUGADORES[ip]['nick'] = nick
                self.JUGADORES[ip]['tanque'] = tanque
                j.update_data(tanque, a, x, y)
                break

    def __actualizar_bala(self, ip, aa, xx, yy):
        if not ip in self.BALAS.keys():
            self.__evento_disparar(ip, aa, xx, yy)
        else:
            for bala in self.balas.sprites():
                if ip == bala.ip:
                    valor = bala.set_posicion(centerx=xx, centery=yy)
                    # FIXME: Verificar si esto es necesario, quizas pueda hacerse en update de bala local
                    if not valor:
                        self.__eliminar_bala(bala, ip)
                    break

    def __evento_disparar(self, ip, aa, xx, yy):
        channel = pygame.mixer.find_channel()
        if channel:
            channel.play(self.sound_disparo)
        self.BALAS[ip] = True
        image_path = os.path.join(os.path.dirname(
            os.path.dirname(self.GAME['mapa'])), 'Iconos', 'bala.png')
        bala = Bala(aa, xx, yy, image_path, RESOLUCION_INICIAL, ip)
        self.balas.add(bala)
        if ip == self.ip:
            self.bala = bala

    def __eliminar_bala(self, bala, ip):
        bala.kill()
        del(bala)
        bala = False
        if self.BALAS.get(ip, False):
            del(self.BALAS[ip])
        if ip == self.ip:
            self.bala.kill()
            del(self.bala)
            self.bala = False

    def __eliminar_jugador(self, j, ip):
        j.kill()
        del(j)
        j = False
        # Los jugadores nunca deben eliminarse del diccionario.
        #if self.JUGADORES.get(ip, False):
        #    del(self.JUGADORES[ip])
        if ip == self.ip:
            self.jugador.kill()
            del(self.jugador)
            self.jugador = False

    def __emit_update(self):
        if bool(self.estado):
            self.emit("update", dict(self.JUGADORES))
            gobject.timeout_add(1500, self.__emit_update)
        return False

    def __end(self):
        self.estado = False
        pygame.quit()
        if self.client:
            self.client.desconectarse()
            del(self.client)
            self.client = False
        self.emit("end", dict(self.JUGADORES))

    def run(self):
        self.estado = "En Juego"
        self.ventana.blit(self.escenario, (0, 0))
        pygame.display.update()
        pygame.time.wait(3)
        gobject.timeout_add(1500, self.__emit_update)
        while self.estado == "En Juego":
            try:
                if not OLPC:
                    self.reloj.tick(35)
                while gtk.events_pending():
                    gtk.main_iteration()
                self.jugadores.clear(self.ventana, self.escenario)
                self.balas.clear(self.ventana, self.escenario)
                self.explosiones.clear(self.ventana, self.escenario)

                self.__enviar_datos()
                self.__recibir_datos()

                self.explosiones.update()

                self.jugadores.draw(self.ventana)
                self.balas.draw(self.ventana)
                self.explosiones.draw(self.ventana)

                self.ventana_real.blit(pygame.transform.scale(self.ventana,
                    self.resolucionreal), (0, 0))

                pygame.display.update()
                pygame.event.pump()
                pygame.event.clear()
                #pygame.time.wait(1)

            except:
                self.estado = False

    def escalar(self, resolucion):
        self.resolucionreal = resolucion

    def update_events(self, eventos):
        if "space" in eventos:
            if not self.bala:
                self.disparo = True
            eventos.remove("space")
        if self.jugador:
            self.jugador.update_events(eventos)

    def salir(self, valor):
        """
        La Interfaz gtk manda salir del juego.
        """
        self.estado = False
        pygame.quit()
        if self.client:
            self.client.enviar(valor)
            datos = self.client.recibir()
            self.client.desconectarse()
            del(self.client)
            self.client = False
            if datos == "END":
                self.__end()

    def config(self):
        pygame.init()
        self.reloj = pygame.time.Clock()

        from pygame.locals import MOUSEMOTION
        from pygame.locals import MOUSEBUTTONUP
        from pygame.locals import MOUSEBUTTONDOWN
        from pygame.locals import JOYAXISMOTION
        from pygame.locals import JOYBALLMOTION
        from pygame.locals import JOYHATMOTION
        from pygame.locals import JOYBUTTONUP
        from pygame.locals import JOYBUTTONDOWN
        from pygame.locals import VIDEORESIZE
        from pygame.locals import VIDEOEXPOSE
        from pygame.locals import USEREVENT
        from pygame.locals import QUIT
        from pygame.locals import ACTIVEEVENT
        from pygame.locals import KEYDOWN
        from pygame.locals import KEYUP

        pygame.event.set_blocked([MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN,
            JOYAXISMOTION, JOYBALLMOTION, JOYHATMOTION, JOYBUTTONUP,
            JOYBUTTONDOWN, ACTIVEEVENT, USEREVENT, KEYDOWN, KEYUP])
        pygame.event.set_allowed([QUIT, VIDEORESIZE, VIDEOEXPOSE])

        pygame.display.set_mode(
            (0, 0), pygame.DOUBLEBUF | pygame.FULLSCREEN, 0)

        pygame.display.set_caption("JAMtank")
        imagen = pygame.image.load(self.GAME['mapa'])
        self.escenario = pygame.transform.scale(imagen,
            RESOLUCION_INICIAL).convert_alpha()

        self.ventana = pygame.Surface((RESOLUCION_INICIAL[0],
            RESOLUCION_INICIAL[1]))
        self.ventana_real = pygame.display.get_surface()

        pygame.mixer.init(44100, -16, 2, 2048)
        pygame.mixer.music.set_volume(1.0)
        path = os.path.dirname(BASE_PATH)
        sound = os.path.join(path, "Audio", "Juego.ogg")
        self.sound_juego = pygame.mixer.Sound(sound)
        self.sound_juego.play(-1)

        disparo = os.path.join(path, "Audio", "disparo.ogg")
        self.sound_disparo = pygame.mixer.Sound(disparo)

        explosion = os.path.join(path, "Audio", "explosion.ogg")
        self.sound_explosion = pygame.mixer.Sound(explosion)

        self.jugador = Jugador(self.JUGADORES[self.ip]['tanque'],
            RESOLUCION_INICIAL, self.ip)
        self.jugadores.add(self.jugador)

        if MAKELOG:
            APPEND_LOG({"Jugador Local": self.ip})


#if __name__ == "__main__":
#    juego = Juego()
#    juego.config()
#    juego.run()
