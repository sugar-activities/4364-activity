#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Server.py por:
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
import SocketServer
import time
import json
import codecs
import gobject


MAKELOG = True
LOGPATH = os.path.join(os.environ["HOME"], "JAMTank_server.log")
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


class RequestHandler(SocketServer.StreamRequestHandler):

    def handle(self):
        while 1:
            try:
                entrada = self.rfile.readline().strip()
                if not entrada:
                    self.request.close()
                    return

                respuesta = self.__procesar(entrada,
                    str(self.client_address[0]))

                if respuesta:
                    while len(respuesta) < 1024:
                        respuesta = "%s*" % respuesta
                    self.wfile.write(respuesta)
                else:
                    if MAKELOG:
                        key = 'server %s' % time.time()
                        ip = self.client_address[0]
                        valor = "Cierre de Conexion: %s" % ip
                        APPEND_LOG({key: valor})
                    self.request.close()
                    #return

            except socket.error, err:
                if MAKELOG:
                    key = "Error: %s" % time.time()
                    APPEND_LOG({key: (str(err), self.client_address[0])})
                self.request.close()

    def __procesar(self, entrada, ip):
        if not self.server.GAME['estado']:
            return "END"
        datos = entrada.split(",")
        if datos:
            if datos[0] == "UPDATE":
                self.__actualizar_jugador(ip, datos)
                return self.__get_data()

            elif datos[0] == "REMOVE":
                self.__remover_jugador(ip, datos)
                return "REMOVIDO"

            elif datos[0] == "END":
                self.__remover_jugador(ip, datos)
                self.server.GAME['estado'] = False
                return "END"

            elif datos[0] == "Config":
                self.__config_server(ip, datos)
                return "OK"

            elif datos[0] == "JOIN":
                return self.__connect_client(ip, datos)

            else:
                if MAKELOG:
                    key = "Mensaje no considerado %s" % time.time()
                    APPEND_LOG({key: datos})
                return "*" * 512

        else:
            return ""

    def __actualizar_jugador(self, ip, datos):
        """
        Jugador actualizando su tanque.
        """
        a, x, y = datos[1:4]
        if self.server.JUGADORES[ip]['activar']:
            a, x, y = (0,0,0)
            self.server.JUGADORES[ip]['estado'] = True
            self.server.JUGADORES[ip]['activar'] = False
        if not self.server.JUGADORES[ip]['estado']:
            a, x, y = ("-","-","-")
        self.server.JUGADORES[ip]['pos'] = "%s,%s,%s" % (a, x, y)
        self.__actualizar_balas(ip, datos)

    def __actualizar_balas(self, ip, datos):
        """
        Jugador actualizando sus Balas.
        """
        a, x, y = datos[4:7]
        self.server.JUGADORES[ip]['bala'] = "%s,%s,%s" % (a, x, y)
        self.__actualizar_explosiones(ip, datos)

    def __actualizar_explosiones(self, ip, datos):
        """
        Jugador actualizando explosiones.
        """
        ene, x, y = datos[7:10]
        if ene != '-':
            # Quitar energía y/o vidas a quien es alcanzado por disparo
            energia = self.server.JUGADORES[ene]['energia']
            self.server.JUGADORES[ene]['energia'] = energia - 1

            if self.server.JUGADORES[ene]['energia'] < 1:
                vidas = self.server.JUGADORES[ene]['vidas']
                self.server.JUGADORES[ene]['vidas'] = vidas - 1
                self.server.JUGADORES[ip]['puntos'] += 10
            else:
                self.server.JUGADORES[ip]['puntos'] += 1

            if self.server.JUGADORES[ene]['vidas'] < 1:
                # Game Over para este Jugador.
                self.server.JUGADORES[ene]['pos'] = "-,-,-"
                self.server.JUGADORES[ene]['estado'] = False
            else:
                if self.server.JUGADORES[ene]['energia'] < 1:
                    # Jugador pierde una Vida pero sigue en Juego.
                    self.server.JUGADORES[ene]['pos'] = "-,-,-"
                    self.server.JUGADORES[ene]['estado'] = False
                    gobject.timeout_add(4000, self.server.reactivar_jugador, ene)

            for i in self.server.JUGADORES.keys():
                # pasar x,y de explosion a todos los jugadores.
                self.server.JUGADORES[ip]['explosiones'][i] = "%s,%s" % (x, y)

    def __remover_jugador(self, ip, datos):
        """
        Jugador Abandonando el Juego.
        """
        if MAKELOG:
            key = "Jugador Removido %s" % time.time()
            APPEND_LOG({key: ip})
        self.server.JUGADORES[ip]['pos'] = "-,-,-"
        self.server.JUGADORES[ip]['bala'] = "-,-,-"

    def __connect_client(self, ip, datos):
        """
        Nuevo Jugador desea conectarse.
        """
        ips = self.server.JUGADORES.keys()
        if not ip in self.server.JUGADORES.keys():
            if len(ips) < self.server.GAME['jugadores']:
                self.server.JUGADORES[ip] = dict(self.server.model)
                self.server.JUGADORES[ip]['path'] = datos[1].strip()
                self.server.JUGADORES[ip]['nick'] = datos[2].strip()
                retorno = "%s" % str(self.server.GAME['mapa'].strip())
                if MAKELOG:
                    APPEND_LOG({"JOIN %s" % ip: dict(self.server.JUGADORES)})
                return retorno
            else:
                if MAKELOG:
                    key = "Jugador Rechazado %s" % time.time()
                    APPEND_LOG({key: ip})
                return "CLOSE"
        else:
            if MAKELOG:
                key = "El Jugador ya estaba en game %s" % time.time()
                APPEND_LOG({key: ip})
            self.server.JUGADORES[ip]['path'] = datos[1].strip()
            self.server.JUGADORES[ip]['nick'] = datos[2].strip()
            retorno = "%s" % str(self.server.GAME['mapa'].strip())
            return retorno

    def __config_server(self, ip, datos):
        """
        Host Configurando el juego y sus datos como cliente.
        """
        self.server.GAME['mapa'] = datos[1].strip()
        self.server.GAME['jugadores'] = int(datos[2].strip()) + 1
        self.server.GAME['vidas'] = int(datos[3].strip())
        self.server.model['vidas'] = int(datos[3].strip())
        self.server.JUGADORES[ip] = dict(self.server.model)
        self.server.JUGADORES[ip]['path'] = datos[4].strip()
        self.server.JUGADORES[ip]['nick'] = datos[5].strip()
        self.server.JUGADORES[ip]['vidas'] = int(self.server.GAME['vidas'])
        if MAKELOG:
            APPEND_LOG({"Configuracion Juego": dict(self.server.GAME)})
            APPEND_LOG({
                "Configuracion Jugadores": dict(self.server.JUGADORES)})

    def __get_data(self):
        """
        Devuelve a quien se ha conectado, los datos de todos los jugadores.
        """
        ips = self.server.JUGADORES.keys()
        convida = list(ips)
        retorno = ""
        for ip in ips:
            nick = self.server.JUGADORES[ip]['nick']
            tanque = self.server.JUGADORES[ip]['path']
            energia = self.server.JUGADORES[ip]['energia']
            vidas = self.server.JUGADORES[ip]['vidas']
            puntos = self.server.JUGADORES[ip]['puntos']
            posicion = self.server.JUGADORES[ip]['pos']
            bala = self.server.JUGADORES[ip]['bala']

            datos = "%s,%s,%s,%s,%s,%s,%s,%s" % (ip, nick, tanque,
                posicion, vidas, energia, puntos, bala)

            explosion = self.server.JUGADORES[ip]['explosiones'].get(
                self.client_address[0], False)
            if explosion:
                datos = "%s,%s" % (datos, explosion)
                del(self.server.JUGADORES[ip][
                    'explosiones'][self.client_address[0]])

            retorno = "%s%s||" % (retorno, datos)
            if vidas == 0:
                convida.remove(ip)

        if len(ips) > 1 and len(convida) == 1:
            return "END"
        else:
            return retorno.strip()


class Server(SocketServer.ThreadingMixIn, SocketServer.ThreadingTCPServer):

    def __init__(self, logger=None, host='localhost',
        port=5000, handler=RequestHandler):

        SocketServer.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.allow_reuse_address = True
        self.socket.setblocking(0)

        self.GAME = {
            'mapa': "",
            'jugadores': 2,
            'vidas': 5,
            'estado': True,
            }

        self.model = {
            'nick': '',
            'path': '',
            'pos': '0,0,0',
            'energia': 5,
            'vidas': 5,
            'puntos': 0,
            'bala': '-,-,-',
            'explosiones': {},
            'estado': True,
            'activar': False,
            }

        self.JUGADORES = {}

        print "Server ON . . ."

    def reactivar_jugador(self, ip):
        self.JUGADORES[ip]['energia'] = int(self.model['energia'])
        self.JUGADORES[ip]['activar'] = True
        return False

    def shutdown(self):
        print "Server OFF"
        SocketServer.ThreadingTCPServer.shutdown(self)


if __name__ == "__main__":
    ip = ''
    import commands
    text = commands.getoutput('ifconfig wlan0').splitlines()
    datos = ''
    for linea in text:
        if 'Direc. inet:' in linea and 'Difus.:' in linea and 'Másc:' in linea:
            datos = linea
            break
    ip = 'localhost'
    if datos:
        ip = datos.split('Direc. inet:')[1].split('Difus.:')[0].strip()

    if ip:
        server = Server(host=ip, port=5000, handler=RequestHandler)
        server.GAME['mapa'] = "fondo1.png"
        server.GAME['jugadores'] = 3
        server.GAME['vidas'] = 5
        server.serve_forever()
