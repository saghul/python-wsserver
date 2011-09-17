# WSServer a simple, single threaded WebSocket server

## Important note!
This project is now dead. I did have the intention to further develop it, but I no
longer have enough time and I also found another way to achieve the goal of bridging
WebSocket with ZeroMQ, which was the reason why I started this. I'll use Tornado + TornadIO
as described here: http://code.saghul.net/a-zeromq-to-websocket-gateway-take-2

## Description
WSServer is a really simple (it does not yet implement all WS variants) WebSocket
server which runs in a single thread.

I needed a single threaded WebSocket server implementation and couldn't find any
that could quite fit so I wrote my own (sort of) by looking at other WS server
implementations. In order to multiplex all the connections it uses *poll*.

## Python version compatibility
WSServer was developed and tested with Python 2.6. It will **not** work on Python 2.5.
Support for Python 3 has not been tested.

## Just give me an example
Have a look at the test/ directory.

## What's missing?
See the TODO file.

## Can I help?
Sure! Check the TODO file. Implement something. Fork this project. Send a pull request :-)

