#!/usr/bin/env python
"""Simplified chat demo for websockets.
"""

import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import json
import os.path
import uuid

from tornado.options import define, options

define("port", default=8889, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/chatsocket", ChatSocketHandler),
        ]
        settings = dict(
            cookie_secret="MYVERYOWNCOOKIESECRET",  # TODO
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            autoreload=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", messages=ChatSocketHandler.cache)


class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    cache = []
    cache_size = 5
    device = None

    def get_compression_options(self):
        # Non-None enables compression with default options
        return {}

    def open(self):
        logging.info("New waiter connected")
        ChatSocketHandler.waiters.add(self)

    def on_close(self):
        logging.info("Waiter closed connection")
        ChatSocketHandler.waiters.remove(self)

    @classmethod
    def update_cache(cls, chat):
        cls.cache.append(chat)
        if len(cls.cache) > cls.cache_size:
            cls.cache = cls.cache[-cls.cache_size:]

    @classmethod
    def send_updates(cls, chat):
        logging.info("sending message to {} waiters".format(len(cls.waiters)))
        for waiter in cls.waiters:
            try:
                waiter.write_message(chat)
            except:
                logging.error("Error sending message", exc_info=True)

    def on_message(self, message):
        logging.debug("Got message {}".format(message))
        assert self.device is not None

        packet = self.device.transceive(self.decode_message(message), unpack=True)
        logging.debug("Got {}".format(repr(packet)))
        response = self.to_chat(json.dumps({"response": packet._asdict()}))
        ChatSocketHandler.update_cache(response)
        ChatSocketHandler.send_updates(response)

    @classmethod
    def decode_message(self, json_string):
        return tornado.escape.json_decode(json_string)["body"]
    
    def to_chat(self, message):
        chat = {"id": str(uuid.uuid4()), "body": message}
        chat["html"] = tornado.escape.to_basestring(
            self.render_string("message.html", message=chat))
        return chat


def main(device=None):
    app = Application()
    app.listen(options.port)
    ChatSocketHandler.device = device
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    tornado.options.parse_command_line()
    main()
