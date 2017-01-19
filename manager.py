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


import hashlib, datetime, json
from .cookie import LoginCookie, dformat

class LoginManager(object):
	"""
	Login Manager used to authorize actions.
	This manager supports Password and LoginCookie authorization.

	You have to provide the method isvalid_ with a dict object that contains

	- Name and Password (password mode) or
	- A LoginCookie dict representation (generated by ``json.loads(cookie.to_json())``)

	The manager will automatically choose the correct way to login.

	You need to provide the LoginManager with the following function:

	- db_get_passwd_hash: queries a password hash from a database. Takes a name as an argument.
	- db_get_expiretime_by_name: queries a expiretime(for LoginCookies) from a database
	- hash_function: hash function for passwords
	- get_ip: returns the IP of the client
	- place_cookie: sets a cookie in the client Browser
	- remove_cookie: deletes the given cookie
	
	The following arguments are necessary:

	- pubks: A list of authorized publickeys that may sign cookies
	- privk: A private key that will be used to sign a LoginCookie
	"""
	def __init__(self, db_get_passwd_hash, 
			place_cookie, 
			hash_function,
			get_ip,
			db_get_expiretime_by_name,
			remove_cookie,
			pubks, privk):
		self.db_get_passwd_hash = db_get_passwd_hash
		self.place_cookie = place_cookie
		self.hash_function = hash_function
		self.db_get_expiretime_by_name = db_get_expiretime_by_name
		self.remove_cookie = remove_cookie
		self.pubks = pubks
		self.privk = privk
		self.get_ip = get_ip

	def login_password(self, name, passwd):
		"""
		Login via password. Automatically places a LoginCookie.
		"""
		hash_ = self.hash_function(name, passwd)
		if(hash_ == self.hash_function(name, passwd)):
			self.place_cookie(self.make_cookie(name).to_json())
			return True
		raise Exception("Invalid Username or Password")
	def make_cookie(self, name):
		"""
		Generate a LoginCookie.
		"""
		now = datetime.datetime.now()
		expiredate = self.db_get_expiretime_by_name(name) + now
		ip = self.get_ip()
		cookie = LoginCookie(name, ip, now.strftime(dformat), expiredate.strftime(dformat))
		cookie.sign(self.privk.sign, "")
		return cookie
	def isvalid(self, login):
		"""
		.. _isvalid:

		Check if the given login (type: dict) is valid.
		Raises an Exception if the login was invalid.
		"""
		if(not "sign" in login):
			return self.login_password(login["name"], login["passwd"])
		cookie = LoginCookie.from_json(json.dumps(login))
		if(not self.check_cookie(cookie)):
			raise Exception("Invalid cookie signature")
		if(not self.is_active(cookie)):
			self.remove_cookie(cookie)
			raise Exception("Cookie expired.")
		if(cookie.ip != self.get_ip()):
			self.remove_cookie(cookie)
			raise Exception("Cookie IP addr does not match Client IP addr")
		return True

	def is_active(self, cookie):
		"""
		Check if the cookie is still active. Returns False if the cookie is expired.
		"""
		now = datetime.datetime.now()
		if(datetime.datetime.strptime(cookie.expiredate, dformat) < now):
			return False
		return True
	
	def check_cookie(self, cookie):
		"""
		Check the cookie signature.
		"""
		for key in self.pubks:
			if(cookie.checksign(key.verify)):
				return True
		return False
	
if( __name__ == "__main__"):
	import cherrypy
	import Crypto.PublicKey.RSA as RSA
	import os
	#
	# XXX This test requires the module chat (a simple webbased chatsystem)
	# To be in the parent folder and a __init__.py file in the parent folder.
	#
	from ..chat.iface.web_cherry import WebIface
	key = RSA.generate(1024,os.urandom)
	pubkeys = [key.publickey()]

	# All password logins
	logins = {"User": "fickdichinsknie"}
	
	# Functions used by LoginManager
	def make_hash(string1, string2):
		if(not isinstance(string1, bytes)):
			string1 = string1.encode("UTF-8")
			string2 = string2.encode("UTF-8")
		return hashlib.sha256(string1 + string2).digest()
	get_ip = lambda:  cherrypy.request.remote.ip
	def set_cookie(c): 
		print(c)
		cherrypy.response.cookie["login"] = c
	def remove_cookie(c): 
		print(c)
		cherrypy.response.cookie["login"] = ''

	# hash the passwords
	logins = {k: make_hash(k, v) for k,v in logins.items()}
	get_passwd_hash = lambda name: logins[name]
	get_expire_time = lambda name: datetime.timedelta(hours = 24)

	manager = LoginManager(get_passwd_hash, set_cookie,
			make_hash, get_ip,
			get_expire_time, remove_cookie, 
			pubkeys, key)
	webif = WebIface(manager)

	conf = {\
		"/": {\
			'tools.sessions.on': True
		},
	}
	cherrypy.config.update({
		'server.socket_host': '0.0.0.0'
	})
	cherrypy.quickstart(webif, "/", conf)

