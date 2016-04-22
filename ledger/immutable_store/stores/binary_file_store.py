import os

from ledger.immutable_store.stores.file_store import FileStore


class BinaryFileStore(FileStore):
    def __init__(self, dbDir, dbName, keyIsLineNo: bool=False, storeContentHash: bool=True):
        # This is the separator between key and value
        self.delimiter = b"\t"
        # TODO: This line separator might conflict with some data format.
        # So prefix the value data in the file with size and only read those
        # number of bytes.
        self.lineSep = b'\n\x07\n\x01'
        super().__init__(dbDir, dbName, keyIsLineNo, storeContentHash)
        self._initDB(dbDir, dbName)

    def _isBytes(self, arg):
        return isinstance(arg, (bytes, bytearray))

    def _initDB(self, dbDir, dbName):
        super()._initDB(dbDir, dbName)
        self.dbPath = os.path.join(dbDir, "{}.bin".format(dbName))
        self._dbFile = open(self.dbPath, mode="a+b", buffering=0)

    def put(self, value, key=None):
        if not (self._isBytes(key) or self._isBytes(value)):
            raise ValueError("key and value need to be bytes-like object")
        super().put(key=key, value=value)

    def get(self, key):
        if not self._isBytes(key):
            raise TypeError("key needs to be a bytes-like object")
        return super().get(key)

    def iterator(self, include_key=True, include_value=True, prefix=None):
        if prefix and not self._isBytes(prefix):
            raise TypeError("prefix needs to be a bytes-like object")

        return super().iterator(include_key, include_value, prefix)

    def _getLines(self):
        return (line.strip(self.lineSep) for line in
                self._dbFile.read().split(self.lineSep)
                if len(line.strip(self.lineSep)) != 0)
