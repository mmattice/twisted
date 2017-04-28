# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Test cases for twisted.test.proto_helpers package.
"""
from twisted.trial import unittest
from twisted.test.proto_helpers import MemoryReactor
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.defer import Deferred
from twisted.protocols.basic import LineReceiver

class HookedProtocol(Protocol):
    def __init__(self, hook):
        self.hook = hook

    def connectionMade(self):
        self.hook.callback(self)


class TestFactory(Factory):
    protocol = HookedProtocol

    def __init__(self, hook):
        self.hook = hook

    def buildProtocol(self, addr):
        p = self.protocol(hook)
        p.factory = self
        return p

    def startedConnecting(self, connector):
        pass

    def clientConnectionFailed(self, connector, reason):
        pass

    def clientConnectionLost(self, connector, reason):
        pass

class MemoryReactorTests(unittest.TestCase):
    """
    Test MemoryReactor actions.
    """

    def test_connection(self):
        port = 80
        reactor = MemoryReactor()
        srvd, clid = Deferred(), Deferred()
        srvconn, cliconn = [], []
        srvd.addCallback(srvconn.append)
        clid.addCallback(cliconn.append)
        srvfactory = TestFactory(srvd)
        reactor.listenTCP(port, srvfactory)
        clifactory = TestFactory(clid)
        reactor.connectTCP('localhost', port, clifactory)
        self.assertEqual(srvconn, [])
        self.assertEqual(cliconn, [])
        #reactor.pump()
        self.assertEqual(len(srvconn), 1)
        self.assertEqual(len(cliconn), 1)
