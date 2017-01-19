CookieLogin Specification
#########################

This file describes the basic principles of CookieLogin.

Concept
=======

CookieLogin is based on cryptographic cookies. Those cookies are splitted into two parts:

- hashed part
- signature

The hashed part contains the following information:

- client IP address
- username (UNIQUE)
- date of issue
- date of expiry

The client IP address must match the IP address the client uses currently. 
If the client changes his IP address the cookie becomes invalid.

The username is the name the user uses to log into the service.

The dates are in the format ``%d.%m.%y-%H:%M``.

The signature is a publickey signature (i.e. using RSA).

Hashing
=======

The hashed part must be hashed in a certain way. The string to hash is

::
	
	"name{name}ip{ip}setdate{setdate}expiredate{expiredate}".format(...).encode("UTF-8")

The hash algorithm should be cryptographic secure. 
Currently SHA256 is used.

Transmission
============

The cookie will be stored and transmitted as a JSON string.

The cookie can be passed to a service either via HTTP POST, HTTP GET 
of passively as a usual cookie.

The JSON format is

::

	{"name": name, 
		"ip": ip, 
		"setdate": setdate, 
		"expiredate": expiredate,
		"sign": _sign}

The order of the fields must not matter. 
Implementations must deal with JSON's beaviour of converting single values
to lists, so ``"name":name`` might be changed to ``"name":[name]``.

Checks
======

The server must perform the following checks:

- The signature matches the cookie
- The name is registered
- The IP address matches the client's IP address
- The expiredate is in the future

It might be usefull to check the setdate to prevent
problems with wrong local times.


