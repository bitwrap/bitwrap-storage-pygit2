import os
import shutil
import json
from pygit2 import init_repository, Signature
import pygit2

repo_root = os.environ.get(
    'BITWRAP_REPO_PATH',
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../_repo/'))
)

def staterepo(repo_name):
    return os.path.join(repo_root, repo_name)

class Storage(object):

    @staticmethod
    def truncate(repo_name):
        try:
          shutil.rmtree(staterepo(repo_name))
        except:
          pass

    @staticmethod
    def open(repo_name):
        return Storage(staterepo(repo_name))

    def __init__(self, repo_path):
        self.path = repo_path
        self.repo = init_repository(self.path)

    def commit(self, response):

        res = response['event']
        index = self.repo.index
        index.read()

        for address in res['cache']:
            if address == 'control':
                continue

            with open(os.path.join(self.path, address), 'w') as keystore:
                json.dump(res['cache'][address], keystore)

            index.add(address)

        index.write()

        msg = res['message']
        schema = msg['signal']['schema']

        sender = msg['addresses']['sender']
        sender_email = sender + '@' + schema

        target = msg['addresses']['target']
        target_email = target + '@' + schema

        try:
            head = self.repo.revparse_single('HEAD')
            parents = [head.id]
        except:
            parents = []



        oid = self.repo.create_commit(
            'refs/heads/master',
            Signature(sender, sender_email),
            Signature(target, target_email),
            json.dumps([msg['signal']['action'], response['hash'], response['oid'] ]),
            index.write_tree(),
            parents
        )

        msg_uuid = self.repo.head.target.__str__()

        return { 'txn': oid, 'hash': response['hash'], 'oid': response['oid'], 'event': res }

        
    def fetch(self, key):
        with open(os.path.join(self.path, key), 'r') as keystore:
            return json.load(keystore)
