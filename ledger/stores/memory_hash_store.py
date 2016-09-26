from ledger.stores.hash_store import HashStore


# TODO: The api has changed for FileHashStore and OrientDBStore and
# should be changed here too
class MemoryHashStore(HashStore):
    def __init__(self):
        self.reset()

    def writeLeaf(self, leafHash):
        self._leafs.append(leafHash)

    def writeNode(self, nodeHash):
        self._nodes.append(nodeHash)

    def readLeaf(self, pos):
        return self._leafs[pos - 1]

    def readNode(self, pos):
        return self._nodes[pos - 1]

    def readLeafs(self, startpos, endpos):
        return (n for n in self._leafs[startpos-1:endpos-1])

    def readNodes(self, startpos, endpos):
        return (n for n in self._nodes[startpos-1:endpos-1])

    @property
    def leafCount(self) -> int:
        return len(self._leafs)

    @property
    def nodeCount(self) -> int:
        return len(self._nodes)

    def reset(self):
        self._nodes = []
        self._leafs = []
        return True