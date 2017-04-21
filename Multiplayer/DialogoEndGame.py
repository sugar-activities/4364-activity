#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   DialogoEndGame.py por:
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

import gtk
import gobject


class DialogoEndGame(gtk.Dialog):

    def __init__(self, parent=None, _dict={}):

        gtk.Dialog.__init__(self,
            parent=parent,
            flags=gtk.DIALOG_MODAL,
            buttons=("Cerrar", gtk.RESPONSE_ACCEPT))

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        self.set_decorated(False)
        self.set_border_width(15)
        label = gtk.Label("La Batalla ha Concluido")
        label.show()
        informe = InformeWidget(_dict)
        self.vbox.pack_start(label, False, False, 5)
        self.vbox.pack_start(informe, True, True, 5)
        self.set_size_request(500, 300)


class InformeWidget(gtk.EventBox):

    def __init__(self, _dict):

        gtk.EventBox.__init__(self)

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        self.lista = ListaDatos(_dict)
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(
            gtk.POLICY_NEVER,
            gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport(self.lista)
        self.add(scroll)
        self.show_all()


class ListaDatos(gtk.TreeView):

    def __init__(self, _dict):

        gtk.TreeView.__init__(self, gtk.ListStore(
            gtk.gdk.Pixbuf,
            gobject.TYPE_STRING,
            gobject.TYPE_INT))

        self.set_property("rules-hint", True)
        self.set_headers_clickable(True)
        self.set_headers_visible(True)
        self.__setear_columnas()
        self.show_all()

        ips = _dict.keys()
        items = []
        for ip in ips:
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(
                _dict[ip]['tanque'], 24, -1)
            item = (pixbuf, _dict[ip]['nick'], _dict[ip]['puntos'])
            items.append(item)
        if items:
            self.agregar_items(items)

    def __setear_columnas(self):
        self.append_column(self.__construir_columa_icono('Tanque', 0, True))
        self.append_column(self.__construir_columa('Jugador', 1, True))
        self.append_column(self.__construir_columa('Puntos', 2, True))

    def __construir_columa(self, text, index, visible):
        render = gtk.CellRendererText()
        columna = gtk.TreeViewColumn(text, render, text=index)
        columna.set_sort_column_id(index)
        columna.set_property('visible', visible)
        columna.set_property('resizable', False)
        columna.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        return columna

    def __construir_columa_icono(self, text, index, visible):
        render = gtk.CellRendererPixbuf()
        columna = gtk.TreeViewColumn(text, render, pixbuf=index)
        columna.set_property('visible', visible)
        columna.set_property('resizable', False)
        columna.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        return columna

    def __ejecutar_agregar_elemento(self, elementos):
        if not elementos:
            self.get_model().set_sort_column_id(2, gtk.SORT_DESCENDING)
            return False
        ip, nick, puntos = elementos[0]
        self.get_model().append([ip, nick, puntos])
        elementos.remove(elementos[0])
        gobject.idle_add(self.__ejecutar_agregar_elemento, elementos)
        return False

    def agregar_items(self, elementos):
        gobject.idle_add(self.__ejecutar_agregar_elemento, elementos)
