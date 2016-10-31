import os
import sys
import logging
from Legobot import StorageInterface

logger = logging.getLogger(__name__)

class Key:
    """
    Creates a key object that is consumed by storage interface
    """

    def __init__(self, path):
        self.path = path

    def exists(self):
        return os.path.isfile(self.path)

class Local:
    """
    Provides a local key/value storage interface
    """

    def __init__(self, datadir):
        self.datadir = os.path.abspath(datadir)
        logger.info("Initialized local storage at {0}".format(self.datadir))

    def set(self, keypath, value, log_transation=True):
        logger.info("Writing value {0} to key {1}".format(value, keypath))
        # prevent arbitrary writes to anywhere on filesystem
        # I think this is still vulnerable to dir walks like ../../../etc/shadow
        if not os.path.isabs(key):
            key = Key(os.path.join(self.datadir, keypath))
        else:
            logger.error('Key provided is absolute path. Provide relative path instead.')
            return False

        if key.exists():
            with open(key.path, 'wb') as f:
                f.write(value)
            
            if log_transaction:
                logger.info('Wrote key {0}'.format(keypath))
            return True

    def get(self,keypath):
        # prevent arbitrary reads to anywhere on filesystem
        if not os.path.isabs(key):
            key = Key(os.path.join(self.datadir, keypath))
        else:
            logger.error('Key provided is absolute path. Provide relative path instead.')

        with open(key.path, 'r') as f:
            value = f.read(value)
        return value
