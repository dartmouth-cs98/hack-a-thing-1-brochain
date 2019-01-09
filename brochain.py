class Brochain(object):
    def __init__(self):
        self.chain = []
        self.current_bumps = []
    
    def new_bro(self):
        """
        creates a new bro and adds it to the chain
        """
        pass

    def new_bump(self, sender, recipient, amount):
        """
        creates a new bump to go into the next bro
        """

        pass
    
    @staticmethod
    def hash(bro):
        """
        hashes a bro
        """
        pass
    
    @property
    def last_bro(self):
        """
        returns the last bro in the chain
        """
        pass