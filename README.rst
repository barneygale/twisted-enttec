twisted-enttec: Python/Twisted support for the Enttec DMX USB Pro
=================================================================

This package provides a twisted protocol supports the Enttec DMX USB Pro.

These protocol classes are available, each a subclass of the previous:

- ``EnttecProtocol`` - provides ``connect()``, ``sendPacket()``, and
  ``packetReceived()`` methods.
- ``EnttecOutputProtocol`` - provides ``step``, ``frame`` and ``params``
  attributes, plus ``setup()``, ``configure()`` and ``render()`` methods.
- ``EnttecOutputLoopProtocol`` - provides a ``loop()`` method.

Example
-------

.. code-block:: python

    from twisted.internet import reactor
    from twisted_enttec import EnttecOutputLoopProtocol

    class Protocol(EnttecOutputLoopProtocol):
        interval = 0.01

        def loop(self):
            for chan in range(24):
                self.frame[chan] = (100 * self.step) % 256
            self.render()

    protocol = Protocol()
    protocol.connect("/dev/ttyUSB0", reactor)
    reactor.run()