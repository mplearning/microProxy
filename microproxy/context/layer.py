class LayerContext(object):
    """
    LayerContext: Context used to communicate with different layer.
    """
    def __init__(self,
                 mode,
                 src_stream=None,
                 dest_stream=None,
                 scheme=None,
                 host=None,
                 port=None,
                 client_tls=None,
                 server_tls=None,
                 done=False,
                 src_info=None):
        if mode not in ("socks", "transparent", "replay", "http"):
            raise ValueError("incorrect mode value")

        self.mode = mode
        self.src_stream = src_stream
        self.dest_stream = dest_stream
        self.scheme = scheme
        self.host = host
        self.port = port
        self.client_tls = client_tls
        self.server_tls = server_tls
        self.done = done
        self.src_info = src_info
