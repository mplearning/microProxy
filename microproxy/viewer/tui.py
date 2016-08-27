import zmq
from zmq.eventloop import ioloop, zmqstream
import urwid
import json

import gviewer
from format import Formatter

ioloop.install()


class Tui(gviewer.BaseDisplayer):
    SUMMARY_MAX_LENGTH = 100
    PALETTE = [
        ("code ok", "light green", "black", "bold"),
        ("code error", "light red", "black", "bold")
    ]

    def __init__(self, stream):
        self.stream = stream
        self.data_store = self.create_data_store()
        self.viewer = gviewer.GViewer(
            self.data_store, self,
            palette=self.PALETTE,
            event_loop=urwid.TornadoEventLoop(ioloop.IOLoop.instance()))
        self.formatter = Formatter()

    def create_data_store(self):
        return ZmqAsyncDataStore(self.stream.on_recv)

    def start(self):
        self.viewer.start()

    def _code_text_markup(self, code):
        if int(code) < 400:
            return ("code ok", str(code))
        return ("code error", str(code))

    def _fold_path(self, path):
        return path if len(path) < self.SUMMARY_MAX_LENGTH else path[:self.SUMMARY_MAX_LENGTH - 1] + "..."

    def summary(self, message):
        return [
            self._code_text_markup(message["response"]["code"]),
            " {0:7} {1}://{2}{3}".format(
                message["request"]["method"],
                message["scheme"],
                message["host"],
                self._fold_path(message["path"]))]

    def get_views(self):
        return [("Request", self.request_view),
                ("Response", self.response_view)]

    def request_view(self, message):
        groups = []
        request = message["request"]
        groups.append(gviewer.PropsGroup(
            "",
            [gviewer.Prop("method", request["method"]),
             gviewer.Prop("path", request["path"]),
             gviewer.Prop("version", request["version"])]))
        groups.append(gviewer.PropsGroup(
            "Request Header",
            [gviewer.Prop(k, v) for k, v in request["headers"]]))

        if request["body"]:
            groups.append(gviewer.Group(
                "Request Body",
                [gviewer.Line(s) for s in self.formatter.format_request(request)]))
        return gviewer.Groups(groups)

    def response_view(self, message):
        groups = []
        response = message["response"]
        groups.append(gviewer.PropsGroup(
            "",
            [gviewer.Prop("code", str(response["code"])),
             gviewer.Prop("reason", response["reason"]),
             gviewer.Prop("version", response["version"])]))
        groups.append(gviewer.PropsGroup(
            "Response Header",
            [gviewer.Prop(k, v) for k, v in response["headers"]]))

        if response["body"]:
            groups.append(gviewer.Group(
                "Response Body",
                [gviewer.Line(s) for s in self.formatter.format_response(response)]))
        return gviewer.Groups(groups)


class ZmqAsyncDataStore(gviewer.AsyncDataStore):
    def transform(self, message):
        return json.loads(message[0])


def create_msg_channel(channel):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(channel)
    socket.setsockopt(zmq.SUBSCRIBE, "")
    return socket


def start(config):
    socket = create_msg_channel(config["viewer_channel"])
    stream = zmqstream.ZMQStream(socket)
    tui = Tui(stream)
    tui.start()
