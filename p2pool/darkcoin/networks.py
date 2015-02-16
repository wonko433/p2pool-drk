import os
import platform

from twisted.internet import defer

from . import data
from p2pool.util import math, pack, jsonrpc

@defer.inlineCallbacks
def check_genesis_block(darkcoind, genesis_block_hash):
    try:
        yield darkcoind.rpc_getblock(genesis_block_hash)
    except jsonrpc.Error_for_code(-5):
        defer.returnValue(False)
    else:
        defer.returnValue(True)

nets = dict(
    darkcoin=math.Object(
        P2P_PREFIX='bf0c6bbd'.decode('hex'),
        P2P_PORT=8888,
        ADDRESS_VERSION=76,
        RPC_PORT=8887,
        RPC_CHECK=defer.inlineCallbacks(lambda darkcoind: defer.returnValue(
            'darkcoinaddress' in (yield darkcoind.rpc_help()) and
            not (yield darkcoind.rpc_getinfo())['testnet']
        )),
        SUBSIDY_FUNC=lambda nBits, height: __import__('darkcoin_subsidy').GetBlockBaseValue(nBits, height),
        BLOCKHASH_FUNC=lambda data: pack.IntType(256).unpack(__import__('darkcoin_hash').getPoWHash(data)),
        POW_FUNC=lambda data: pack.IntType(256).unpack(__import__('darkcoin_hash').getPoWHash(data)),
        BLOCK_PERIOD=150, # s
        SYMBOL='DRK',
        CONF_FILE_FUNC=lambda: os.path.join(os.path.join(os.environ['APPDATA'], 'Darkcoin') if platform.system() == 'Windows' else os.path.expanduser('~/Library/Application Support/Darkcoin/') if platform.system() == 'Darwin' else os.path.expanduser('~/.darkcoin'), 'darkcoin.conf'),
        BLOCK_EXPLORER_URL_PREFIX='http://explorer.darkcoin.io/block/',
        ADDRESS_EXPLORER_URL_PREFIX='http://explorer.darkcoin.io/address/',
        TX_EXPLORER_URL_PREFIX='http://explorer.darkcoin.io/tx/',
        SANE_TARGET_RANGE=(2**256//2**32//1000 - 1, 2**256//2**20 - 1),
        DUMB_SCRYPT_DIFF=1,
        DUST_THRESHOLD=0.001e8,
    ),
    darkcoin_testnet=math.Object(
        P2P_PREFIX='cee2caff'.decode('hex'),
        P2P_PORT=18888,
        ADDRESS_VERSION=139,
        RPC_PORT=18887,
        RPC_CHECK=defer.inlineCallbacks(lambda darkcoind: defer.returnValue(
            'darkcoinaddress' in (yield darkcoind.rpc_help()) and
            (yield darkcoind.rpc_getinfo())['testnet']
        )),
        SUBSIDY_FUNC=lambda nBits, height: __import__('darkcoin_subsidy').GetBlockBaseValue_testnet(nBits, height),
        BLOCKHASH_FUNC=lambda data: pack.IntType(256).unpack(__import__('darkcoin_hash').getPoWHash(data)),
        POW_FUNC=lambda data: pack.IntType(256).unpack(__import__('darkcoin_hash').getPoWHash(data)),
        BLOCK_PERIOD=150, # s
        SYMBOL='tDRK',
        CONF_FILE_FUNC=lambda: os.path.join(os.path.join(os.environ['APPDATA'], 'Darkcoin') if platform.system() == 'Windows' else os.path.expanduser('~/Library/Application Support/Darkcoin/') if platform.system() == 'Darwin' else os.path.expanduser('~/.darkcoin'), 'darkcoin.conf'),
        BLOCK_EXPLORER_URL_PREFIX='http://test.explorer.darkcoin.qa/block/',
        ADDRESS_EXPLORER_URL_PREFIX='http://test.explorer.darkcoin.qa/address/',
        TX_EXPLORER_URL_PREFIX='http://test.explorer.darkcoin.qa/tx/',
        SANE_TARGET_RANGE=(2**256//2**32//1000 - 1, 2**256//2**20 - 1),
        DUMB_SCRYPT_DIFF=1,
        DUST_THRESHOLD=0.001e8,
    ),
)
for net_name, net in nets.iteritems():
    net.NAME = net_name
