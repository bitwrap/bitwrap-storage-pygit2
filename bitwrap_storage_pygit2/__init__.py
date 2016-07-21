import os
import shutil
import json
from pygit2 import init_repository, Signature

repo_root = os.environ.get(
    'BITWRAP_REPO_PATH',
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../_repo/'))
)

eventstore_path = os.path.join(repo_root, 'eventstore')

def staterepo(repo_name):
    return os.path.join(repo_root, repo_name)

class Storage(object):

    @staticmethod
    def truncate(repo_name):
        try:
          shutil.rmtree(staterepo(repo_name))
          shutil.rmtree(eventstore_path)
        except:
          pass

    @staticmethod
    def open(repo_name):
        return Storage(staterepo(repo_name))

    def __init__(self, repo_path):
        self.path = repo_path
        self.repo = init_repository(staterepo(repo_path))
        self.eventstore = init_repository(eventstore_path)

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

        sender_actor = Signature(sender, sender_email)
        target_actor = Signature(msg['addresses']['target'], 'system@bitwrap.io')

        self.repo.create_commit(
            'refs/heads/master',
            sender_actor,
            target_actor,
            msg['signal']['action'],
            index.write_tree(),
            []
        )

        res['uuid'] = self.repo.head.target.__str__()

        event_index = self.eventstore.index
        event_index.read()

        self.eventstore.create_commit(
            'refs/heads/master',
            sender_actor,
            target_actor,
            json.dumps(res),
            event_index.write_tree(),
            []
        )

        
    def fetch(self, key):
        with open(os.path.join(self.path, key), 'r') as keystore:
            return json.load(keystore)

    def fetch_event(self, event_index):
        # TODO: read commit message from event repo
        pass
