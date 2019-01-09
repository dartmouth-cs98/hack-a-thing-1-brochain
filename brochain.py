import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request
from urllib.parse import urlparse

class Brochain(object):
    def __init__(self):
        self.chain = []
        self.current_bumps = []
        self.brodes = set()
    
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

    def register_broode(self, address):
        """
        add a new brode
        """
        parsed_url = urlparse(address)
        self.brodes.add(parsed_url.netloc)


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

    def valid_chain(self, chain):
        """
        determine if a given brochain is valid
        """
        last_bro = chain[0]
        current_index = 1

        while current_index < len(chain):
            bro = chain[current_index]
            print(f'{last_bro}')
            print(f'{bro}')
            print("\n-----------\n")
            if bro['previous_hash'] != self.hash(last_bro):
                return False
            if not self.valid_proof(last_bro['proof'], bro['proof']):
                return False

            last_bro = bro
            current_index += 1
        return True

    def resolve_conflicts(self):
        """
        resolve conflicts by replacing with longest chain in network
        """
        neighbros = self.brodes
        new_chain = None

        max_length = len(self.chain)

        for brode in neighbros:
            response = requests.get(f'http://{brode}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False



# instantiate brode 
# TODO: separate into separate files
app = Flask(__name__)

# generate globally unique address for this brode
brode_id = str(uuid4()).replace('-', '')

brochain = Brochain()

@app.route('/mine', methods=['GET'])
def mine():
    last_bro = brochain.last_bro
    last_proof = last_bro['proof']
    proof = brochain.proof_of_work(last_proof)

    # reward for finding the proof, always from sender 0
    # TODO: adjust amount accordingly?
    brochain.new_transaction(
        sender="0",
        recipient=brode_id,
        amount=1
    )

    # add bro to chain
    previous_hash = brochain.hash(last_bro)
    bro = brochain.new_bro(proof, previous_hash)

    response = {
        'message': "New Bro Forged",
        'index': bro['index'],
        'bumps': bro['bumps'],
        'proof': bro['proof'],
        'previous_hash': bro['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/bumps/new', methods=['POST'])
def new_bump():
    values = request.get_json()

    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = brochain.new_bump(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': brochain.chain,
        'length': len(brochain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

@app.route('/brodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    brodes = values.get('brodes')
    if brodes is None:
        return "Error: Please supply a valid list of brodes", 400

    for brode in brodes:
        brochain.register_node(brode)

    response = {
        'message': 'New brodes have been added',
        'total_nodes': list(brochain.brodes),
    }
    return jsonify(response), 201

@app.route('/brodes/resolve', methods=['GET'])
def consensus():
    replaced = brochain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': brochain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': brochain.chain
        }

    return jsonify(response), 200