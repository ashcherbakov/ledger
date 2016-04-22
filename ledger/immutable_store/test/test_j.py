from binascii import hexlify
from string import ascii_lowercase

import pytest
from math import log

from ledger.immutable_store.merkle import CompactMerkleTree, TreeHasher, \
    MerkleVerifier, count_bits_set, highest_bit_set


@pytest.fixture()
def hasherAndTree():
    h = TreeHasher()
    m = CompactMerkleTree(hasher=h)

    def show(data):
        print("-" * 60)
        print("appended  : {}".format(data))
        print("hash      : {}".format(hexlify(h.hash_leaf(data))[:3]))
        print("tree size : {}".format(m.tree_size))
        print("root hash : {}".format(m.root_hash_hex()[:3]))
        for i, hash in enumerate(m.hashes):
            lead = "Hashes" if i == 0 else "      "
            print("{}    : {}".format(lead, hexlify(hash)[:3]))

    return h, m, show

"""
1: 221

  [221]
  /
221

2: e8b

  [e8b]
  /   \
221   fa6

3: e8b, 906

      fe6
     /   \
  [e8b]  [906]
  /   \
221   fa6


4: 4c4

        [4c4]
     /         \
   e8b         9c7
  /   \       /   \
221   fa6   906   11e


5: 4c4, 533

               e10
            /       \
        [4c4]       [533]
     /         \
   e8b         9c7
  /   \       /   \
221   fa6   906   11e


6: 4c4, 2b1

                 ecc
            /          \
        [4c4]          [2b1]
     /         \       /   \
   e8b         9c7   533   3bf
  /   \       /   \
221   fa6   906   11e


7: 4c4, 2b1, 797

                    74f
            /                \
        [4c4]                429
     /         \            /    \
   e8b         9c7       [2b1]  [797]
  /   \       /   \      /   \
221   fa6   906   11e  533   3bf


8: 50f

                    [50f]
            /                \
         4c4                 fed
     /         \            /    \
   e8b         9c7        2b1     800
  /   \       /   \      /   \    /  \
221   fa6   906   11e  533   3bf 797 754



"""

"""
hexlify(c(
    c(
        c(
            l(d[0]), l(d[1])
        ),
        c(
            l(d[2]), l(d[3])
        )
    ),
    c(
        c(
            l(d[4]),l(d[5])
        ),
        l(d[6])
    )
))
"""


def testStuff(hasherAndTree):
    h, m, show = hasherAndTree
    verifier = MerkleVerifier()

    for d in range(10000):
        data = str(d+1).encode()
        m.append(data)
        audit_path_length = verifier.audit_path_length(d, d+1)
        incl_proof = m.inclusion_proof(d, d+1)  # size before and size after
        if d % 100 == 0:
            show(data)
            print("aud path l: {}".format(audit_path_length))
            print("incl proof: {}".format(incl_proof))
            print("incl p len: {}".format(len(incl_proof)))


    # m.append(b'a')
    #
    #
    #
    # print("")
    # for d in range(0, 100):
    #     m.append(str(d).encode())
    #     print("s:{} h:{}".format(m.tree_size, len(m.hashes)))
    # m.append(b'hello')
    #
    # class O:
    #     def __init__(self):
    #         self.tree_size = None
    #         self.hashes = []
    #
    # o = O()
    # m.save(o)
    # print(o)


def getNodePosition(start, height):
    pwr = highest_bit_set(start) - 1
    if count_bits_set(start) == 1:
        adj = height - pwr
        return start - 1 + adj
    else:
        c = pow(2, pwr)
        return getNodePosition(c, pwr) + getNodePosition(start - c, height)


def testEfficientHashStore(hasherAndTree):
    h, m, show = hasherAndTree

    txns = 1000

    for d in range(txns):
        serNo = d+1
        data = str(serNo).encode()
        show(data)
        m.append(data)

    assert len(m.leaf_hash_deque) == txns
    while m.leaf_hash_deque:
        leaf = m.leaf_hash_deque.pop()
        print("leaf hash: {}".format(hexlify(leaf)))

    node_ptr = 0
    while m.node_hash_deque:
        start, height, node = m.node_hash_deque.pop()
        node_ptr += 1
        end = start - pow(2, height) + 1
        print("node hash start-end: {}-{}".format(start, end))
        print("node hash height: {}".format(height))
        print("node hash end: {}".format(end))
        print("node hash: {}".format(hexlify(node)))
        assert getNodePosition(start, height) == node_ptr

