#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   JAMTank.py por:
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
import sys
import gtk
import gobject

from IntroWidget import IntroWidget
from SelectServer import SelectServer
from SelectClient import SelectClient

BASE = os.path.dirname(__file__)

"""
Requiere:
    python-pygame
"""


class JAMTank(gtk.Window):
    """
    Ventana gtk principal del Juego.
    """

    def __init__(self):

        gtk.Window.__init__(self)

        self.set_title("JAMTank")
        self.set_icon_from_file(os.path.join(BASE, "Iconos", "jamtank.svg"))
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))

        #self.set_resizable(True)
        #self.set_size_request(640, 480)
        self.set_border_width(2)
        #self.set_position(gtk.WindowPosition.CENTER)
        self.fullscreen()

        # Fase 1: Introduccion
        self.intro_widget = False
        # Fase 2: Elegir
        self.select_widget = False
        # Fase 3: Jugar Solo
        self.widget_game = False

        self.connect("delete-event", self.__salir)
        self.connect("realize", self.__do_realize)

        self.eventos = []
        self.show_all()

        print os.getpid()

    def __reset(self):
        """
        Quita todos los widgets de la ventana y borra los eventos en la cola.
        """
        for child in self.get_children():
            self.remove(child)
            child.destroy()
        if self.widget_game:
            self.disconnect_by_func(self.__key_press_event)
            self.disconnect_by_func(self.__key_release_event)
            self.widget_game.disconnect_by_func(self.switch)
            del(self.widget_game)
            self.widget_game = False
        self.eventos = []

    def __do_realize(self, widget):
        self.switch(False, 1)

    def __solo_run(self, widget, datos):
        self.__reset()
        from GameWidget import GameWidget
        self.widget_game = GameWidget()
        self.add(self.widget_game)
        gobject.idle_add(self.widget_game.setup_init, datos)

    def __update_events(self):
        if self.widget_game:
            self.widget_game.update_events(self.eventos)

    def __salir(self, widget=None, event=None):
        if self.widget_game:
            self.widget_game.salir()
        sys.exit(0)

    def __intro_switch(self, widget, valor):
        """
        Recibe opción de juego desde IntroWidget
        """
        if valor == "solo":
            self.switch(False, 2)
        elif valor == "red":
            self.switch(False, 3)
        elif valor == "join":
            self.switch(False, 4)
        elif valor == "creditos":
            self.switch(False, 5)
        elif valor == "salir":
            self.__salir()

    def __server_select_accion(self, widget, accion, _dict):
        self.__reset()
        if accion == 'salir':
            self.switch(False, 1)
        else:
            from Multiplayer.ServerGameWidget import GameWidget
            self.widget_game = GameWidget()
            self.add(self.widget_game)
            gobject.idle_add(self.widget_game.setup_init, _dict)
            self.connect('key-press-event', self.__key_press_event)
            self.connect('key-release-event', self.__key_release_event)
            self.widget_game.connect('salir', self.switch, 3)

    def __client_select_accion(self, widget, accion, _dict):
        self.__reset()
        if accion == 'salir':
            self.switch(False, 1)
        else:
            from Multiplayer.ClientGameWidget import GameWidget
            self.widget_game = GameWidget()
            self.add(self.widget_game)
            gobject.idle_add(self.widget_game.setup_init, _dict)
            self.connect('key-press-event', self.__key_press_event)
            self.connect('key-release-event', self.__key_release_event)
            self.widget_game.connect('salir', self.switch, 4)

    def __key_press_event(self, widget, event):
        if not self.widget_game:
            return
        nombre = gtk.gdk.keyval_name(event.keyval)
        teclas = ["w", "s", "d", "a", "space", "Escape"]
        if nombre in teclas and not nombre in self.eventos:
            if nombre == "w" and "s" in self.eventos:
                self.eventos.remove("s")
            elif nombre == "s" and "w" in self.eventos:
                self.eventos.remove("w")
            elif nombre == "d" and "a" in self.eventos:
                self.eventos.remove("a")
            elif nombre == "a" and "d" in self.eventos:
                self.eventos.remove("d")
            self.eventos.append(nombre)
        self.__update_events()
        return False

    def __key_release_event(self, widget, event):
        if not self.widget_game:
            return
        nombre = gtk.gdk.keyval_name(event.keyval)
        teclas = ["w", "s", "d", "a", "space", "Escape"]
        if nombre in teclas and nombre in self.eventos:
            self.eventos.remove(nombre)
        self.__update_events()
        return False

    def switch(self, widget, valor):
        self.__reset()
        if valor == 1:
            # Introduccion, opciones de juego.
            self.intro_widget = IntroWidget()
            self.intro_widget.connect("switch", self.__intro_switch)
            self.add(self.intro_widget)
            gobject.idle_add(self.intro_widget.load, os.path.join(
                BASE, "Iconos", "jamtank.svg"))

        elif valor == 2:
            print "FIXME: Comenzar Guión del Juego"
            '''
            self.select_widget = SelectWidget(tipo='single')
            self.select_widget.connect("salir", self.switch, 1)
            self.select_widget.connect("run", self.__solo_run)
            self.add(self.select_widget)
            '''

        elif valor == 3:
            # Selección nick, mapa, tanque, oponentes y vidas.
            print "Esta PC será Servidor"
            self.select_widget = SelectServer()
            self.add(self.select_widget)
            self.select_widget.connect("accion", self.__server_select_accion)

        elif valor == 4:
            # Selección de nick, ip y tanque para unirse a partida multiplayer.
            print "Esta PC será Cliente"
            self.select_widget = SelectClient()
            self.add(self.select_widget)
            self.select_widget.connect("accion", self.__client_select_accion)

        elif valor == 5:
            print "FIXME: Creditos"

        gobject.idle_add(self.queue_draw)


if __name__ == "__main__":
    JAMTank()
    gtk.main()
