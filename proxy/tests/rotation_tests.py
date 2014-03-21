from django.test import TestCase
from proxy.rotations import RoundRobin, NoServersAvailableException

__author__ = 'nick'


class RotationTests(TestCase):
    def setUp(self):
        self.server_list = ['server1', 'server2', 'server3']

    def testRoundRobinRotation(self):
        round_robin = RoundRobin(self.server_list)
        self.assertEqual("server1", round_robin.pick())
        self.assertEqual("server2", round_robin.pick())
        self.assertEqual("server3", round_robin.pick())
        self.assertEqual("server1", round_robin.pick())
        self.assertNotEqual("server4", round_robin.pick())

    def testEmptyRoundRobinRotation(self):
        round_robin = RoundRobin([])
        self.assertRaises(NoServersAvailableException, round_robin.pick)
