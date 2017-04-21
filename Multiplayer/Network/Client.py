#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Client.py por:
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
import socket
import time
import json
import codecs
import gobject

MAKELOG = True
LOGPATH = os.path.join(os.environ["HOME"], "JAMTank_load.log")
if os.path.exists(LOGPATH):
    os.remove(LOGPATH)


def WRITE_LOG(_dict):
    archivo = open(LOGPATH, "w")
    archivo.write(json.dumps(
        _dict, indent=4, separators=(", ", ":"), sort_keys=True))
    archivo.close()


def APPEND_LOG(_dict):
    new = {}
    if os.path.exists(LOGPATH):
        archivo = codecs.open(LOGPATH, "r", "utf-8")
        new = json.JSONDecoder("utf-8").decode(archivo.read())
        archivo.close()
    for key in _dict.keys():
        new[key] = _dict[key]
    WRITE_LOG(new)


class Client(gobject.GObject):

    def __init__(self, ip):

        gobject.GObject.__init__(self)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dir = (ip, 5000)

    def conectarse(self):
        try:
            self.socket.connect(self.dir)
            self.socket.setblocking(0)
            time.sleep(0.5)
            return True
        except socket.error, err:
            # FIXME: socket.error: [Errno 111] Conexión rehusada
            if MAKELOG:
                APPEND_LOG({'Client Connect %s' % time.time(): str(err)})
            return False

    def desconectarse(self):
        self.socket.close()
        time.sleep(0.5)

    def enviar(self, datos):
        datos = "%s\n" % datos
        enviado = False
        while not enviado:
            try:
                self.socket.sendall(datos)
                enviado = True
            except socket.error, err:
                if MAKELOG:
                    APPEND_LOG({'Client Envio %s' % time.time(): str(err)})
            time.sleep(0.02)

    def recibir(self):
        entrada = ""
        while not entrada:
            try:
                entrada = self.socket.recv(1024)
                entrada = entrada.replace("*", "").strip()
            except socket.error, err:
                if MAKELOG:
                    APPEND_LOG({'Client Recibo %s' % time.time(): str(err)})
                time.sleep(0.02)
        return entrada
