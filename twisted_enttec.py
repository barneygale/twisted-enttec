import struct
from twisted.internet import protocol, serialport, task


class EnttecProtocol(protocol.Protocol):
    """
    Twisted protocol supporting the Enttec DMX USB Pro widget.
    """

    buf = ""

    def connect(self, device, reactor):
        """
        Connects to a device.

        :param device: The device name or port number.
        :param reactor: The twisted reactor.
        """
        serialport.SerialPort(self, device, reactor, baudrate=57600)

    def sendPacket(self, ident, payload):
        """
        Sends a packet.

        :param ident: The packet ID.
        :param payload: The packet payload.
        """
        self.transport.write(
            '\x7E' +
            struct.pack('<BH', ident, len(payload)) +
            payload +
            '\xE7')

    def packetReceived(self, ident, payload):
        """
        Called when a packet is received.

        :param ident: The packet ID.
        :param payload: The packet payload.
        """
        pass

    def dataReceived(self, data):
        self.buf += data
        if len(self.buf) < 4:
            return
        head, body = self.buf[:4], self.buf[4:]
        assert head[0] == '\x7E'
        ident, length = struct.unpack('<BH', head[1:4])
        if len(body) < length + 1:
            return
        assert body[length] == '\xE7'
        payload = body[:length]
        self.buf = body[length + 1:]
        self.packetReceived(ident, payload)


class EnttecOutputProtocol(EnttecProtocol):
    """
    Twisted protocol supporting writing of DMX data to an Enttec DMX USB Pro
    widget.
    """

    #: List of channel values (0-255). The length of this list determines the
    #: universe size.
    frame = None

    #: Dict of widget parameters.
    params = {}

    #: The DMX start code.
    start_code = 0

    param_names = ('firmware_version', 'break_time',
                   'mark_after_break_time', 'output_rate')

    def setup(self):
        """
        Called when the device's parameters have been discovered.
        """
        pass

    def configure(self):
        """
        Configures the device, i.e. sends ``self.params``.
        """
        param_values = [self.params[name] for name in self.param_names]
        self.sendPacket(4, struct.pack('<HBBB', param_values))

    def render(self):
        """
        Writes DMX data, i.e. sends ``self.frame``
        """
        fmt = 'B' + 'B' * len(self.frame)
        self.sendPacket(6, struct.pack(fmt, self.start_code, *self.frame))

    def connectionMade(self):
        self.frame = [0] * 24
        self.params = {}
        self.sendPacket(3, '\x00\x00')

    def packetReceived(self, ident, payload):
        if ident == 3:
            param_values = struct.unpack('<HBBB', payload)
            self.params.update(zip(self.param_names, param_values))
            self.setup()


class EnttecOutputLoopProtocol(EnttecOutputProtocol):
    """
    Twisted protocol supporting writing of DMX data to an Enttec DMX USB Pro
    widget.
    """

    #: The loop interval in seconds.
    interval = 0.01

    #: The current step.
    step = 0

    def packetReceived(self, ident, payload):
        EnttecOutputProtocol.packetReceived(self, ident, payload)
        if ident == 3:
            task.LoopingCall.withCount(self._loop).start(self.interval)

    def _loop(self, count):
        self.step += count * self.interval
        self.loop()

    def loop(self):
        """
        Called repeatedly.
        """
        pass
