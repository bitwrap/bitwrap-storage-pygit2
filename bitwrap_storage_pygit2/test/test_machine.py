from bitwrap_storage_pygit2 import Storage
from twisted.trial import unittest
from twisted.internet import defer, reactor

#twisted.internet.base.DelayedCall.debug = True
class MachineTestCase(unittest.TestCase):

    def setUp(self):
        Storage.truncate('karmanom.com')
        self.storage = Storage.open('karmanom.com')

    def tearDown(self):
        pass

    def test_multiple_commits(self):

        request = {
           'cache': {
               'control': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               'dib': [0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 2, 1],
               'zim': [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0]
            },
           'context': {
               'action': [0, -1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, -1],
               'control': [ 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
               'target': [ 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0 ],
               'sender': [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1 ],
            },
            'errors': [],
            'message': {
               'addresses': {'sender': 'zim', 'target': 'dib'},
               'signal': {'action': 'positive_tip', 'role': 1, 'schema': 'karmanom.com'}
            }
        }

        self.storage.commit({ 'event': request, 'hash': 'fake-hash1', 'oid': 'fake-oid1' })
        res = self.storage.commit({ 'event': request, 'hash': 'fake-hash2', 'oid': 'fake-oid2' })
        assert request['cache']['dib'] == self.storage.fetch('dib') 
