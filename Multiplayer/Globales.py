#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Globales.py por:
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
import json
import codecs
import socket


"""
def __return_ip(interfaz):
    import commands
    import platform
    sistema = platform.platform()
    text = commands.getoutput('ifconfig %s' % interfaz).splitlines()
    datos = ''
    for linea in text:
        if 'olpc' in sistema:
            if 'inet ' in linea and 'netmask ' in linea and 'broadcast ' in linea:
                datos = linea
                break
        else:
            if 'Direc. inet:' in linea and 'Difus.:' in linea and 'Másc:' in linea:
                datos = linea
                break
    ip = ''
    if datos:
        if 'olpc' in sistema:
            ip = datos.split('inet ')[1].split('netmask ')[0].strip()
        else:
            ip = datos.split('Direc. inet:')[1].split('Difus.:')[0].strip()
    return ip
"""


def get_ip():
    ip = ""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("google.com", 80))
        ip = s.getsockname()[0]
    except:
        pass
    """
    ip = __return_ip("wlan0")
    if not ip:
        ip = __return_ip("eth0")
    """
    return ip


MAKELOG = True
LOGPATH = os.path.join(os.environ["HOME"], "JAMTank_load.log")


def reset_log():
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
