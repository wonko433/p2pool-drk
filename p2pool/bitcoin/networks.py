import os
import platform

from twisted.internet import defer

from . import data
from p2pool.util import math, pack, jsonrpc

@defer.inlineCallbacks
def check_genesis_block(bitcoind, genesis_block_hash):
    try:
        yield bitcoind.rpc_getblock(genesis_block_hash)
    except jsonrpc.Error_for_code(-5):
        defer.returnValue(False)
    else:
        defer.returnValue(True)

def get_mnp(height, value, testnet):
    ret = value // 5

    if testnet:
        if (height > 46000):              ret += value // 20 # 25% - 2014-10-07
        if (height > 46000+((576*30)*1)): ret += value // 20 # 30% - 2014-10-08
        if (height > 46000+((576*30)*2)): ret += value // 20 # 35% - 2014-10-09
        if (height > 46000+((576*30)*3)): ret += value // 20 # 40% - 2014-10-10
        if (height > 46000+((576*30)*4)): ret += value // 20 # 45% - 2014-10-11
        if (height > 46000+((576*30)*5)): ret += value // 20 # 50% - 2014-10-12
        if (height > 46000+((576*30)*6)): ret += value // 20 # 55% - 2014-10-13
        if (height > 46000+((576*30)*7)): ret += value // 20 # 60% - 2014-10-14

    if (height > 158000):               ret += value // 20 # 25.0% - 2014-10-23
    if (height > 158000+((576*30)* 1)): ret += value // 20 # 30.0% - 2014-11-23
    if (height > 158000+((576*30)* 2)): ret += value // 20 # 35.0% - 2014-12-23
    if (height > 158000+((576*30)* 3)): ret += value // 40 # 37.5% - 2015-01-23
    if (height > 158000+((576*30)* 4)): ret += value // 40 # 40.0% - 2015-02-23
    if (height > 158000+((576*30)* 5)): ret += value // 40 # 42.5% - 2015-03-23
    if (height > 158000+((576*30)* 6)): ret += value // 40 # 45.0% - 2015-04-23
    if (height > 158000+((576*30)* 7)): ret += value // 40 # 47.5% - 2015-05-23
    if (height > 158000+((576*30)* 9)): ret += value // 40 # 50.0% - 2015-07-23
    if (height > 158000+((576*30)*11)): ret += value // 40 # 52.5% - 2015-09-23
    if (height > 158000+((576*30)*13)): ret += value // 40 # 55.0% - 2015-11-23
    if (height > 158000+((576*30)*15)): ret += value // 40 # 57.5% - 2016-01-23
    if (height > 158000+((576*30)*17)): ret += value // 40 # 60.0% - 2016-03-23

    return ret

nets = dict(
    darkcoin=math.Object(
        P2P_PREFIX='bf0c6bbd'.decode('hex'),
        P2P_PORT=9999,
        ADDRESS_VERSION=76,
        RPC_PORT=9998,
        RPC_CHECK=defer.inlineCallbacks(lambda bitcoind: defer.returnValue(
            'darkcoinaddress' in (yield bitcoind.rpc_help()) and
            not (yield bitcoind.rpc_getinfo())['testnet']
        )),
        MNP_FUNC=lambda height, value: get_mnp(height, value, False),
        SUBSIDY_FUNC=lambda nBits, height: __import__('darkcoin_subsidy').GetBlockBaseValue(nBits, height),
        BLOCKHASH_FUNC=lambda data: pack.IntType(256).unpack(__import__('xcoin_hash').getPoWHash(data)),
        POW_FUNC=lambda data: pack.IntType(256).unpack(__import__('xcoin_hash').getPoWHash(data)),
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
        P2P_PORT=19999,
        ADDRESS_VERSION=111,
        RPC_PORT=19998,
        RPC_CHECK=defer.inlineCallbacks(lambda bitcoind: defer.returnValue(
            'darkcoinaddress' in (yield bitcoind.rpc_help()) and
            (yield bitcoind.rpc_getinfo())['testnet']
        )),
        MNP_FUNC=lambda height, value: get_mnp(height, value, True),
        SUBSIDY_FUNC=lambda nBits, height: __import__('darkcoin_subsidy').GetBlockBaseValue_testnet(nBits, height),
        BLOCKHASH_FUNC=lambda data: pack.IntType(256).unpack(__import__('xcoin_hash').getPoWHash(data)),
        POW_FUNC=lambda data: pack.IntType(256).unpack(__import__('xcoin_hash').getPoWHash(data)),
        BLOCK_PERIOD=150, # s
        SYMBOL='tDRK',
        CONF_FILE_FUNC=lambda: os.path.join(os.path.join(os.environ['APPDATA'], 'Darkcoin') if platform.system() == 'Windows' else os.path.expanduser('~/Library/Application Support/Darkcoin/') if platform.system() == 'Darwin' else os.path.expanduser('~/.darkcoin'), 'darkcoin.conf'),
        BLOCK_EXPLORER_URL_PREFIX='',
        ADDRESS_EXPLORER_URL_PREFIX='',
        TX_EXPLORER_URL_PREFIX='',
        SANE_TARGET_RANGE=(2**256//2**32//1000 - 1, 2**256//2**20 - 1),
        DUMB_SCRYPT_DIFF=1,
        DUST_THRESHOLD=0.001e8,
    ),
)
for net_name, net in nets.iteritems():
    net.NAME = net_name
