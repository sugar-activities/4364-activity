#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   ServerGameWidget.py por:
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
import time
import threading
import gtk
import gobject

from Network.Server import Server
from Network.Server import RequestHandler
from Network.Client import Client
from Juego import Juego
from Widgets import Derecha
from DialogoEndGame import DialogoEndGame

from Globales import MAKELOG
from Globales import APPEND_LOG
from Globales import get_ip

if MAKELOG:
    from Globales import reset_log
    reset_log()


def terminate_thread(thread):
    """
    Termina un hilo python desde otro hilo.
    thread debe ser una instancia threading.Thread
    """
    if not thread.isAlive():
        return
    import ctypes
    exc = ctypes.py_object(SystemExit)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread.ident), exc)
    if res == 0:
        raise ValueError("No Existe el id de este hilo")
    elif res > 1:
        """
        si devuelve un número mayor que uno, estás en problemas, entonces
        llamas de nuevo con exc = NULL para revertir el efecto.
        """
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


class GameWidget(gtk.Paned):

    __gsignals__ = {
    "salir": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, [])}

    def __init__(self):

        gtk.Paned.__init__(self, orientation=gtk.ORIENTATION_HORIZONTAL)

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        self.drawing = DrawingWidget()
        self.derecha = Derecha()

        self.pack1(self.drawing, resize=True, shrink=False)
        self.pack2(self.derecha, resize=False, shrink=False)

        self.show_all()

        self.drawing.connect("update", self.__update_players)
        self.drawing.connect('salir', self.__re_emit_salir)

        # FIXME: Necesario
        self.set_sensitive(False)

    def __update_players(self, widget, _dict):
        self.derecha.update(_dict)

    def __re_emit_salir(self, widget):
        self.emit('salir')

    def setup_init(self, _dict):
        ip = get_ip()
        server = str(_dict['server'])
        tanque = str(_dict['tanque'])
        self.derecha.set_data(ip, server, tanque)
        self.drawing.setup_init(_dict)

    def update_events(self, eventos):
        self.drawing.update_events(eventos)

    def salir(self):
        self.drawing.salir()


class DrawingWidget(gtk.DrawingArea):

    __gsignals__ = {
    "update": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, )),
    "salir": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, [])}

    def __init__(self):

        gtk.DrawingArea.__init__(self)

        self.server_thread = False
        self.client = False
        self.server = False
        self.juego = False

        self.connect("expose-event", self.__do_draw)
        self.show_all()
        self.set_size_request(640, 480)

    def __run_client(self, _dict):
        """
        El Cliente Host, se encarga de configurar el Server con:
            mapa, vidas, enemigos,
                tanque y nick (propios)
        """
        server = str(_dict['server'])
        mapa = os.path.basename(str(_dict['mapa']))
        tanque = os.path.basename(str(_dict['tanque']))
        enemigos = str(_dict['enemigos'])
        vidas = str(_dict['vidas'])
        nick = str(_dict['nick'])
        self.client = Client(server)
        connected = self.client.conectarse()
        if connected:
            _buffer = "Config,%s,%s,%s,%s,%s" % (mapa, enemigos,
                vidas, tanque, nick)
            self.client.enviar(_buffer)
            retorno = self.client.recibir()
            if retorno == "OK":
                tanque = str(_dict['tanque'])
                mapa = str(_dict['mapa'])
                new_dict = {
                    'tanque': tanque,
                    'nick': nick,
                    'mapa': mapa,
                    }
                if MAKELOG:
                    APPEND_LOG({'client': new_dict})
                time.sleep(0.5)
                self.__run_game(new_dict)
            else:
                dialog = Dialogo(parent=self.get_toplevel(),
                    text="Algo salió mal al Configurar el Servidor.")
                dialog.run()
                self.salir()
        else:
            dialog = Dialogo(parent=self.get_toplevel(),
                text="EL Cliente no pudo Conectarse con el Servidor.")
            dialog.run()
            self.salir()

    def __end_game(self, juego, _dict):
        """
        El juego recibe salir desde el server.
        """
        dialog = DialogoEndGame(parent=self.get_toplevel(), _dict=_dict)
        self.emit('salir')
        dialog.run()
        dialog.destroy()

    def __run_game(self, _dict):
        """
        Comienza a correr el Juego.
        """
        try:
            # FIXME: Agregar Dialogo con explicacion sobre teclas
            xid = self.get_property('window').xid
            os.putenv('SDL_WINDOWID', str(xid))
            self.juego = Juego(dict(_dict), self.client)
            self.juego.connect("end", self.__end_game)
            self.juego.connect("update", self.__update_players)
            self.juego.config()
            time.sleep(0.5)
            self.juego.run()
        except:
            dialog = Dialogo(parent=self.get_toplevel(),
                text="EL Juego no pudo Iniciar.")
            dialog.run()
            self.salir()

    def __update_players(self, juego, _dict):
        self.emit("update", _dict)

    def __do_draw(self, widget=None, event=None):
        """
        Reescalado en gtk, reescala en pygame.
        """
        rect = self.get_allocation()
        if self.juego:
            self.juego.escalar((rect.width, rect.height))

    def setup_init(self, _dict):
        """
        Comienza a correr el Server.
        """
        try:
            self.server = Server(host=str(_dict['server']),
                port=5000, handler=RequestHandler)
            self.server_thread = threading.Thread(
                target=self.server.serve_forever)
            self.server_thread.setDaemon(True)
            self.server_thread.start()
            time.sleep(0.5)
            if MAKELOG:
                APPEND_LOG({'server': _dict})
            self.__run_client(dict(_dict))
        except:
            dialog = Dialogo(parent=self.get_toplevel(),
                text="EL Servidor no pudo Iniciar.")
            dialog.run()
            self.salir()
        return False

    def update_events(self, eventos):
        """
        Eventos gtk, se pasan a pygame
        """
        if "Escape" in eventos:
            self.salir()
        else:
            if self.juego:
                self.juego.update_events(eventos)
        if "space" in eventos:
            eventos.remove("space")

    def salir(self):
        if self.juego:
            self.juego.salir("END,")
            del(self.juego)
            self.juego = False
        if self.client:
            self.client.desconectarse()
            del(self.client)
            self.client = False
        if self.server:
            self.server.server_close()
            self.server.shutdown()
            self.server.socket.close()
            del(self.server)
            self.server = False
        if self.server_thread:
            terminate_thread(self.server_thread)
            del(self.server_thread)
            self.server_thread = False
        self.emit('salir')


class Dialogo(gtk.Dialog):

    def __init__(self, parent=None, text=""):

        gtk.Dialog.__init__(self,
            parent=parent,
            flags=gtk.DIALOG_MODAL)

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        self.set_decorated(False)
        self.set_border_width(15)
        label = gtk.Label(text)
        label.show()
        self.vbox.pack_start(label, True, True, 5)
        self.connect("realize", self.__do_realize)

    def __do_realize(self, widget):
        gobject.timeout_add(2000, self.__destroy)

    def __destroy(self):
        self.destroy()
        return False
