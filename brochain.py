import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask

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
        return self.chain[-1]


    def proof_of_work(self, last_proof):
        """
        Simple Proof of Work Algorithm

        TODO: make number of 0s a variable 
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates the Proof
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"


# instantiate node 
# TODO: separate into separate files
app = Flask(__name__)

# generate globally unique address for this brode
brode_id = str(uuid4()).replace('-', '')

brochain = Brochain()

@app.route('/mine', methods=['GET'])
def mine():
    return "mining a new bro"

@app.route('/transactions/new', methods=['POST'])
def new_bump():
    return "adding a new bump"

@app.route('/chain', methods=['GET'])
def full_chain():
    reponse = {
        'chain': brochain.chain,
        'length': len(brochain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)