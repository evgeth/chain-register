import MySQLdb
from contextlib import closing
from Configs import Configs


def __init_vars():
    # TODO: check
    with closing(db.cursor()) as cursor:
        cursor.execute("SELECT key, value FROM " + __settings + ";")
        entry = []
        for row in cursor:
            entry.append(row[1])
        return entry[0], entry[1]


def __init_db():
    with closing(db.cursor()) as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS " + Configs.db_name)
        cursor.execute("USE " + Configs.db_name)
        __query = "CREATE TABLE IF NOT EXISTS " + __transactions + "(" +\
                  "id INT UNSIGNED, " +\
                  __shop_id + " INT UNSIGNED, " +\
                  __hash + " CHAR(64), " +\
                  __block_id + " INT UNSIGNED, " +\
                  __date + " TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, " +\
                  "PRIMARY KEY (id));"
        cursor.execute(__query)
        __query = "ALTER TABLE {} ADD INDEX ({})".format(__transactions, __block_id)
        cursor.execute(__query)

        __query = "CREATE TABLE IF NOT EXISTS " + __blocks + "(" +\
                  __block_id + " INT UNSIGNED, " +\
                  __root_hash + " CHAR(64), " +\
                  __blockchain_tx_hash + " CHAR(64), " \
                  "PRIMARY KEY (" + __block_id + ");"
        cursor.execute(__query)
        
        __query = "CREATE TABLE IF NOT EXISTS {} (key CHAR(64), value INT UNSIGNED);".format(__settings)
        cursor.execute(__query)
        cursor.execute("INSERT IGNORE INTO {} VALUES (last_block_id, 0);".format(__transactions))
        cursor.execute("INSERT IGNORE INTO {} VALUES (last_tx_id, 0);".format(__transactions))


# transactions
__shop_id = "shop_id"
__block_id = "block_id"
__hash = "hash"
__date = "date"
# blocks
__root_hash = "root_hash"
__blockchain_tx_hash = "blockchain_tx_hash"
# Tables
__transactions = "transactions"
__blocks = "blocks"
__settings = "settings"
# Connect to db
db = MySQLdb.connect(user=Configs.user, passwd=Configs.password)
# create tables if necessary
__init_db()
# init last block id from db
__last_block_id, __last_tx_id = __init_vars()


def __get_block(block_id):
    # TODO: check
    with closing(db.cursor()) as cursor:
        cursor.execute("SELECT " + __root_hash + "," +
                       __blockchain_tx_hash + " FROM " + __blocks +
                       " WHERE " + __block_id + " = " + str(block_id) + ";")
        result = cursor.fetchone()
        return {"root_hash": result[0], "blockchain_tx_hash": result[1]}


def __set_last_block_id(val):
    # TODO: check
    with closing(db.cursor()) as cursor:
        global __last_block_id
        if val < __last_block_id:
            raise ValueError("val should be more than" + str(__last_block_id))
        cursor.execute("UPDATE " + __settings + " SET value = " + str(val) + " WHERE key = last_block_id;")
        __last_block_id = val


def save_tx(shop_id, _hash):
    # TODO: check
    with closing(db.cursor()) as cursor:
        cursor.execute("INSERT INTO " + __transactions + " VALUES (" +
                       str(shop_id) + ", " + _hash + ", -1);")


def get_txs_for_new_block():
    with closing(db.cursor()) as cursor:
        cursor.execute("SELECT id, {} FROM {} WHERE id > {} ;".format(__hash, __transactions, __last_tx_id))
        hashes = []
        for row in cursor: 
            hashes.append(row)
    return __last_block_id + 1, hashes


def save_block(block_id, root_hash, blockchain_tx_hash, txs):
    # TODO: check
    with closing(db.cursor()) as cursor:
        cursor.execute("UPDATE {} SET value = {} WHERE {} >= {} AND {} <= {};".format(
            __transactions, 
            __block_id, 
            "id", 
            txs[0][0], 
            "id",
            txs[-1][0]))

        __set_last_block_id(block_id)
        cursor.execute("INSERT INTO " + __blocks + " VALUES (" +
                       block_id, ", " + root_hash + ", " + blockchain_tx_hash + ");")




def get_block_by_tx_hash(tx_hash):
    # TODO: check
    with closing(db.cursor()) as cursor:
        cursor.execute("SELECT {0} FROM {1} WHERE {2} = {3};".format(__block_id, __transactions, __hash, tx_hash))
        tx = cursor.fetchone()
        if tx is None:
            return None
        return __get_block(tx[0])
