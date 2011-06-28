# WSServer a simple, single threaded WebSocket server

## Description
WSServer is a really simple (it does not yet implement all WS variants) WebSocket
server which runs in a single thread.

I needed a single threaded WebSocket server implementation and couldn't find any
that could quite fit so I wrote my own (sort of) by looking at other WS server
implementations. In order to multiplex all the connections it uses *poll*.

## Just give me an example
Have a look at the test/ directory.

## What's missing?
See the TODO file.

## Can I help?
Sure! Check the TODO file. Implement something. Fork this project. Send a pull request :-)

