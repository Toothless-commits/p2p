class PeerState:
    def __init__(self):
        self.peers = {}

    def __contains__(self, peer_id):
        return peer_id in self.peers

    def __getitem__(self, peer_id):
        return self.peers[peer_id]

    def __setitem__(self, peer_id, conn):
        self.peers[peer_id] = conn

    def __delitem__(self, peer_id):
        del self.peers[peer_id]

    def __iter__(self):
        return iter(self.peers)

    def __len__(self):
        return len(self.peers)

    def items(self):
        return self.peers.items()

    def keys(self):
        return self.peers.keys()

    def values(self):
        return self.peers.values()