#!/usr/bin/env python
"""Simplified chat demo for websockets.
"""

import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
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
            cookie_secret="MYVERYOWNCOOKIESECRET",  # TODO Read from file
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            compiled_template_cache=False,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")  # , messages=ChatSocketHandler.cache


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
        logging.info("Got message {}".format(message))

        chat = self.to_chat(message)
        ChatSocketHandler.update_cache(chat)
        ChatSocketHandler.send_updates(chat)

        if self.device is not None:
            response = self.to_chat(self.device.transceive(chat["body"]), json=False)
            ChatSocketHandler.update_cache(response)
            ChatSocketHandler.send_updates(response)
    
    def to_chat(self, msg, json=True):
        chat = {"id": str(uuid.uuid4()), "body": tornado.escape.json_decode(msg)["body"] if json else msg}
        chat["html"] = tornado.escape.to_basestring(
            self.render_string("message.html", message=chat))
        return chat


def main(device=None):
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    ChatSocketHandler.device = device
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
