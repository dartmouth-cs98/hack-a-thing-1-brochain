import hashlib
import json
from time import time

class Brochain(object):
    def __init__(self):
        self.chain = []
        self.current_bumps = []
    
    def new_bro(self, proof, previous_hash=None):
        """
        creates a new bro in the brochain

        :param proof: <int> the proof given by the PoW algorithm
        :param previous_hash: (optional) <str>
        :return: <dict> new bro
        """

        bro = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_bumps,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        self.current_bumps = []

        self.chain.append(bro)
        return bro

    def new_bump(self, sender, recipient, amount):
        """
        creates a new bump to go into the next mined bro

        :param sender: <str>
        :param recipient: <str>
        :param amount: <int>
        :return: <int> the index of the bro that will hold this transaction
        """

        self.current_bumps.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_bro['index'] + 1
    
    @staticmethod
    def hash(bro):
        """
        creates a SHA-256 hash of a bro

        :param bro: <dict>
        :return: <str>
        """
        bro_string = json.dumps(bro, sort_keys=True).encode()
        return hashlib.sha256(bro_string).hexdigest()
    
    @property
    def last_bro(self):
        """
        returns the last bro in the chain
        """
        pass