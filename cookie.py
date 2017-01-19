#!/usr/bin/python3

#
# Copyright(c) 2017 Daniel Knüttel
#

# This program is free software.
# Anyways if you think this program is worth it
# and we meet shout a drink for me.


#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Dieses Programm ist Freie Software: Sie können es unter den Bedingungen
#    der GNU Lesser General Public License, wie von der Free Software Foundation,
#    Version 3 der Lizenz oder (nach Ihrer Wahl) jeder neueren
#    veröffentlichten Version, weiterverbreiten und/oder modifizieren.
#
#    Dieses Programm wird in der Hoffnung, dass es nützlich sein wird, aber
#    OHNE JEDE GEWÄHRLEISTUNG, bereitgestellt; sogar ohne die implizite
#    Gewährleistung der MARKTFÄHIGKEIT oder EIGNUNG FÜR EINEN BESTIMMTEN ZWECK.
#    Siehe die GNU Lesser General Public License für weitere Details.
#
#    Sie sollten eine Kopie der GNU Lesser General Public License zusammen mit diesem
#    Programm erhalten haben. Wenn nicht, siehe <http://www.gnu.org/licenses/>.


import json, hashlib
dformat = "%d.%m.%y-%H:%M"

class LoginCookie(object):
	"""
	.. _LoginCookie:

	A cryptograpy based way to authorize actions.
	
	"""
	def __init__(self, name, ip, setdate, expiredate):
		# XXX this has to be a string but JSON is like
		# nah just use a list
		while(isinstance(name, (list, tuple))):
			name = name[0]
		self.name = name,
		self.ip = ip
		self.setdate = setdate
		self.expiredate = expiredate
		self._sign = None
	def get_hash(self):
		"""
		Returns a secure hash(``bytes``) of the cookie.
		Currently this uses sha256.

		The hashed string is::

			"name{name}ip{ip}setdate{setdate}expiredate{expiredate}".format(...).encode("UTF-8")
	
		
		"""
		summer = hashlib.sha256()
		data = "name" + str(self.name) + "ip" + str(self.ip) + "setdate" + str(self.setdate) + "expiredate" + str(self.expiredate)
		print("XXX: data = ", data)
		summer.update(data.encode("UTF-8"))
		return summer.digest()
	def checksign(self, checkfkt, *fktargs):
		"""
		Checks if the signature of the cookie is valid. Returns boolean.

		Takes a verify function and *args for this function.
		Example:
		::

			cookie.checksign(rsapubkey.verify)
		

		"""
		if(self.sign == None):
			return False
		return checkfkt(self.get_hash(), self._sign, *fktargs)
	def sign(self, signfkt, *fktargs):
		"""
		Sign this cookie. Takes a sign function and *args for this function.
		Example:
		::

			cookie.sign(rsakey.sign, "")

		"""
		self._sign = signfkt(self.get_hash(), *fktargs)
	def to_json(self):
		"""
		Returns a JSON string represenation
		"""
		return json.dumps({"name": self.name, "ip": self.ip, "setdate": self.setdate, "expiredate": self.expiredate,
				"sign": self._sign})
	@staticmethod
	def from_json(json_string):
		"""
		Creates a LoginCookie object from a JSON string
		"""
		dct = json.loads(json_string)
		cookie = LoginCookie(dct["name"], dct["ip"], dct["setdate"], dct["expiredate"])
		cookie._sign = dct["sign"]
		return cookie

