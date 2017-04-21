#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   SelectWidgets.py por:
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
import gtk
import gobject

BASE = os.path.dirname(__file__)


class OponentesSelectBox(gtk.VBox):
    """
    Widget para seleccionar cantidad de enemigos y vidas.
    """

    __gsignals__ = {
    "valor": (gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, (gobject.TYPE_INT,
        gobject.TYPE_STRING))}

    def __init__(self):

        gtk.VBox.__init__(self)

        hbox = gtk.HBox()
        oponentes = gtk.Label("Oponentes")
        spin = NumBox(range(1, 10))
        spin.connect("valor", self.__emit_valor, "oponentes")
        hbox.pack_start(spin, False, False, 5)
        hbox.pack_start(oponentes, False, False, 5)
        self.pack_start(hbox, False, False, 0)

        hbox = gtk.HBox()
        limite = gtk.Label("Vidas")
        spin = NumBox(range(5, 51))
        spin.connect("valor", self.__emit_valor, "vidas")
        hbox.pack_start(spin, False, False, 5)
        hbox.pack_start(limite, False, False, 5)
        self.pack_start(hbox, False, False, 0)

        self.show_all()

    def __emit_valor(self, widget, valor, tipo):
        self.emit("valor", valor, tipo)


class NumBox(gtk.HBox):
    """
    Spin para cambiar la cantidad de vidas o enemigos.
    """

    __gsignals__ = {
    "valor": (gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, (gobject.TYPE_INT, ))}

    def __init__(self, rango):

        gtk.HBox.__init__(self)

        self.rango = rango
        self.valor = min(self.rango)

        menos = gtk.Button("-")
        menos.connect("clicked", self.__change)
        self.label = gtk.Label("0")
        mas = gtk.Button("+")
        mas.connect("clicked", self.__change)

        self.pack_start(menos, False, False, 5)
        self.pack_start(self.label, False, False, 5)
        self.pack_start(mas, False, False, 5)

        self.show_all()

        self.label.set_text(str(self.valor))
        gobject.idle_add(self.emit, "valor", self.valor)

    def __change(self, widget):
        label = widget.get_label()
        if label == "-":
            if self.valor - 1 > min(self.rango):
                self.valor -= 1
        elif label == "+":
            if self.valor + 1 < max(self.rango) + 1:
                self.valor += 1
        self.emit("valor", self.valor)
        self.label.set_text(str(self.valor))


class Lista(gtk.TreeView):

    __gsignals__ = {
    "nueva-seleccion": (gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))}

    def __init__(self):

        gtk.TreeView.__init__(self)

        self.set_property("rules-hint", True)
        self.set_headers_clickable(True)
        self.set_headers_visible(True)

        self.permitir_select = True
        self.valor_select = None

        self.modelo = gtk.ListStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING,
            gobject.TYPE_STRING)

        self.__setear_columnas()
        self.set_model(self.modelo)

        #self.get_selection().set_select_function(self.__selecciones, full=True)
        self.get_selection().connect('changed', self.__selecciones)
        self.show_all()

    def __selecciones(self, seleccion):
        if not self.permitir_select:
            return True
        model, pathlist = seleccion.get_selected_rows()
        iter = model.get_iter(pathlist[0])
        valor = model.get_value(iter, 2)
        self.valor_select = valor
        self.scroll_to_cell(model.get_path(iter))
        self.emit('nueva-seleccion', self.valor_select)
        return True

    def __setear_columnas(self):
        self.append_column(self.__construir_columa_icono('', 0, True))
        self.append_column(self.__construir_columa('Nombre', 1, True))
        self.append_column(self.__construir_columa('', 2, False))

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
            self.permitir_select = True
            self.seleccionar_primero()
            self.get_toplevel().set_sensitive(True)
            return False

        texto, path = elementos[0]
        texto = texto.split('.')[0]
        icono = os.path.join(path)
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(icono, 50, -1)
        self.modelo.append([pixbuf, texto, path])

        elementos.remove(elementos[0])
        gobject.idle_add(self.__ejecutar_agregar_elemento, elementos)
        return False

    def limpiar(self):
        self.permitir_select = False
        self.modelo.clear()
        self.permitir_select = True

    def agregar_items(self, elementos):
        self.get_toplevel().set_sensitive(False)
        self.permitir_select = False
        gobject.idle_add(self.__ejecutar_agregar_elemento, elementos)

    def seleccionar_primero(self, widget=None):
        self.get_selection().select_path(0)


class IpFrame(gtk.Frame):

    def __init__(self):

        gtk.Frame.__init__(self)

        self.set_label(" Ip Local: 192.168.1.1  ")
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        event = gtk.EventBox()
        event.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        event.set_border_width(4)

        hbox = gtk.HBox()
        self.serverip = gtk.Entry()
        #self.serverip.connect("changed", self.__change_ip)
        #self.serverip.set_size_request(100, -1)
        hbox.pack_start(gtk.Label("Ip del Servidor:"), False, False, 5)
        hbox.pack_end(self.serverip, True, True, 0)

        event.add(hbox)
        self.add(event)
        self.show_all()
