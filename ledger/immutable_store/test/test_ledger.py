import time

from ledger.immutable_store.ledger import Ledger
from ledger.immutable_store.leveldb_ledger import LevelDBLedger
from ledger.immutable_store.merkle import CompactMerkleTree, TreeHasher

# TODO Remove hard-coded CompactMerkleTree
ledger_db = LevelDBLedger("/tmp/testLedger")
ledger = Ledger(CompactMerkleTree(), ledger_db)

hasher = TreeHasher()


def testAddTxn():
    txn1 = {
        'clientId': 'cli1',
        'reqId': 1,
        'op': 'do something',
        'reference': 'K2GI8SX89'
    }
    data_to_persist1 = {
        'client_id': txn1['clientId'],
        'request_id': 1,
        'STH': 1,
        'leaf_data': txn1,
        'leaf_data_hash': hasher.hash_leaf(bytes(str(txn1), 'utf-8')),
        'created': time.time(),
        'added_to_tree': time.time(),
        'audit_info': None,
        'seq_no': 1
    }

    txn2 = {
        'clientId': 'cli1',
        'reqId': 2,
        'op': 'do something',
        'reference': 'K2GI8SX89'
    }
    data_to_persist2 = {
        'client_id': txn2['clientId'],
        'request_id': 2,
        'STH': 2,
        'leaf_data': txn2,
        'leaf_data_hash': hasher.hash_leaf(bytes(str(txn2), 'utf-8')),
        'created': time.time(),
        'added_to_tree': time.time(),
        'audit_info': None
    }


    ledger.add(data_to_persist1)
    ledger.add(data_to_persist2)

    # Check that the transaction is added to the Merkle Tree
    assert len(ledger.tree) == 2
    # leaf_data_hash = data_to_persist1['leaf_data_hash']
    # assert ledger.tree.root_hash() == \
    #        hasher.hash_children(leaf_data_hash, leaf_data_hash)

    # Check that the data is appended to the immutable store
    assert data_to_persist1['leaf_data'] == ledger.store.get(1)['leaf_data']

"""
If the server holding the ledger restarts, the ledger should be fully rebuilt
from persisted data. Any incoming commands should be stashed. (Does this affect
creation of Signed Tree Heads? I think I don't really understand what STHs are.)
"""


def testRecoverMerkleTreeFromLedger():
    ledger2 = Ledger(CompactMerkleTree(), ledger_db)
    assert ledger.tree.root_hash() == ledger2.tree.root_hash()


def testTearDown():
    ledger_db.drop()

