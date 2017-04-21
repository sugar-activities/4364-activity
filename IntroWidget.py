#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   IntroWidget.py por:
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
import gobject
import gtk

"""
Contiene Opciones:
    Jugar Solo                  emit("switch", "solo")
    Crear Juego en Red          emit("switch", "red")
    Unirse a Juego Existente    emit("switch", "join")
    Creditos                    emit("switch", "creditos")
    Salir                       emit("switch", "salir")
"""


class IntroWidget(gtk.Table):

    __gsignals__ = {
        "switch": (gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE, (gobject.TYPE_STRING, ))}

    def __init__(self):

        gtk.Table.__init__(self, rows=7, columns=3, homogeneous=True)

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        self.imagen = False
        self.temp_path = "/dev/shm/jamtank_intro_img.png"

        boton = gtk.Button("Jugar Solo")
        boton.connect("clicked", self.__emit_switch, "solo")
        self.attach(boton, 1, 2, 1, 2)
        boton.set_sensitive(False)

        boton = gtk.Button("Crear en Red")
        boton.connect("clicked", self.__emit_switch, "red")
        self.attach(boton, 1, 2, 2, 3)

        boton = gtk.Button("Unirse en Red")
        boton.connect("clicked", self.__emit_switch, "join")
        self.attach(boton, 1, 2, 3, 4)

        boton = gtk.Button("Creditos")
        boton.connect("clicked", self.__emit_switch, "creditos")
        self.attach(boton, 1, 2, 4, 5)
        boton.set_sensitive(False)

        boton = gtk.Button("Salir")
        boton.connect("clicked", self.__emit_switch, "salir")
        self.attach(boton, 1, 2, 5, 6)

        self.show_all()

    def __do_draw(self, widget, event):
        context = widget.window.cairo_create()
        rect = self.get_allocation()
        src = self.imagen
        dst = gtk.gdk.pixbuf_new_from_file_at_size(
            self.temp_path, rect.width, rect.height)
        gtk.gdk.Pixbuf.scale(src, dst, 0, 0, 100, 100, 0, 0, 1.5, 1.5,
            0) #GdkPixbuf.InterpType.BILINEAR
        x = rect.width / 2 - dst.get_width() / 2
        y = rect.height / 2 - dst.get_height() / 2
        context.set_source_pixbuf(dst, x, y)
        context.paint()

    def __emit_switch(self, widget, valor):
        self.emit("switch", valor)

    def load(self, path):
        """
        Carga una imagen para pintar el fondo.
        """
        if path:
            if os.path.exists(path):
                self.imagen = gtk.gdk.pixbuf_new_from_file(path)
                self.imagen.save(self.temp_path, "png")#, [], [])
                self.set_size_request(-1, -1)
        self.connect("expose-event", self.__do_draw)
