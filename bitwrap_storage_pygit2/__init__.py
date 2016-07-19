import os
import shutil
import json
from pygit2 import init_repository, Signature

repo_root = os.environ.get(
    'BITWRAP_REPO_PATH',
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../_repo/'))
)


class Storage(object):

    @staticmethod
    def truncate(repo_name):
        try:
          shutil.rmtree(os.path.join(repo_root, repo_name))
        except:
          pass

    @staticmethod
    def open(repo_name):
        return Storage(os.path.join(repo_root, repo_name))

    def __init__(self, repo_path):
        self.path = repo_path
        self.repo = init_repository(repo_path)

    def commit(self, res):

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
        sender = msg['addresses']['sender']
        sender_email = sender + '@' + msg['signal']['schema']

        # REVIEW: consider adding md5sum of payload as 4th arg
        self.repo.create_commit(
            'refs/heads/master',
            Signature(sender, sender_email),
            Signature('system', 'system@bitwrap.io'),
            json.dumps([
                msg['signal']['action'],
                msg['addresses']['sender'],
                msg['addresses']['target']
            ]),
            index.write_tree(),
            []
        )

        
    def fetch(self, key):
        with open(os.path.join(self.path, key), 'r') as keystore:
            return json.load(keystore)
