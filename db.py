import MySQLdb
from contextlib import closing
from Configs import Configs


def __init_vars():
    with closing(db.cursor()) as cursor:
        __query = "SELECT {}, {} FROM {} ;".format(
            __settings_key,
            __settings_value,
            __settings
        )
        try:
            cursor.execute(__query)
        except (AttributeError, MySQLdb.OperationalError):
            db.connect(user=Configs.user, passwd=Configs.password)
            cursor.execute(__query)
        entry = []
        for row in cursor:
            entry.append(row[1])
        if len(entry) == 0:
            return -1, -1
        return entry[0], entry[1]


def __init_db():
    global __last_block_id, __last_tx_id
    with closing(db.cursor()) as cursor:
        # check if database already exists
        __query = "SELECT COUNT(*) FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{}'".format(
            Configs.db_name
        )
        try:
            cursor.execute(__query)
        except (AttributeError, MySQLdb.OperationalError):
            db.connect(user=Configs.user, passwd=Configs.password)
            cursor.execute(__query)
        if cursor.fetchone()[0] == 0:
            # create database
            cursor.execute("CREATE DATABASE IF NOT EXISTS " + Configs.db_name)
        # select necessary database
        __query = "USE " + Configs.db_name
        try:
            cursor.execute(__query)
        except (AttributeError, MySQLdb.OperationalError):
            db.connect(user=Configs.user, passwd=Configs.password)
            cursor.execute(__query)
        # check if table already exists
        __query = "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{}' AND TABLE_NAME = '{}'".format(
            Configs.db_name,
            __transactions
        )
        try:
            cursor.execute(__query)
        except (AttributeError, MySQLdb.OperationalError):
            db.connect(user=Configs.user, passwd=Configs.password)
            cursor.execute(__query)
        if cursor.fetchone()[0] == 1:
            __query = "USE " + Configs.db_name
            cursor.execute(__query)
            try:
                cursor.execute(__query)
            except (AttributeError, MySQLdb.OperationalError):
                db.connect(user=Configs.user, passwd=Configs.password)
                cursor.execute(__query)
            return
        # create table 'transactions'
        __query = "CREATE TABLE IF NOT EXISTS " + __transactions + "(" +\
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT, " +\
                  __shop_id + " INT UNSIGNED, " +\
                  __hash + " CHAR(64), " +\
                  __block_id + " INT UNSIGNED, " +\
                  __date + " TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, " +\
                  "PRIMARY KEY (id)," \
                  "INDEX (" + __block_id + ")," \
                  "INDEX (" + __hash + "(4)));"
        try:
            cursor.execute(__query)
        except (AttributeError, MySQLdb.OperationalError):
            db.connect(user=Configs.user, passwd=Configs.password)
            cursor.execute(__query)
        # create table 'blocks'
        __query = "CREATE TABLE IF NOT EXISTS " + __blocks + " (" +\
                  __block_id + " INT UNSIGNED, " +\
                  __root_hash + " CHAR(64), " +\
                  __blockchain_tx_hash + " CHAR(64), " \
                  "PRIMARY KEY (" + __block_id + "));"
        try:
            cursor.execute(__query)
        except (AttributeError, MySQLdb.OperationalError):
            db.connect(user=Configs.user, passwd=Configs.password)
            cursor.execute(__query)
        # create table 'settings'
        __query = "CREATE TABLE IF NOT EXISTS {} ({} CHAR(64), {} INT UNSIGNED, UNIQUE ({}));".format(
            __settings,
            __settings_key,
            __settings_value,
            __settings_key
        )
        try:
            cursor.execute(__query)
        except (AttributeError, MySQLdb.OperationalError):
            db.connect(user=Configs.user, passwd=Configs.password)
            cursor.execute(__query)
        __query = "INSERT IGNORE INTO {} VALUES ('last_block_id', 0);".format(__settings)
        try:
            cursor.execute(__query)
        except (AttributeError, MySQLdb.OperationalError):
            db.connect(user=Configs.user, passwd=Configs.password)
            cursor.execute(__query)
        __query = "INSERT IGNORE INTO {} VALUES ('last_tx_id', 0);".format(__settings)
        try:
            cursor.execute(__query)
        except (AttributeError, MySQLdb.OperationalError):
            db.connect(user=Configs.user, passwd=Configs.password)
            cursor.execute(__query)
    __last_block_id, __last_tx_id = __init_vars()


# transactions
__shop_id = "shop_id"
__block_id = "block_id"
__hash = "hash"
__date = "date"
__settings_key = "mKey"
__settings_value = "mValue"
# blocks
__root_hash = "root_hash"
__blockchain_tx_hash = "blockchain_tx_hash"
# Tables
__transactions = "transactions"
__blocks = "blocks"
__settings = "settings"
# Connect to db
db = MySQLdb.connect(user=Configs.user, passwd=Configs.password)
db.autocommit(True)
# create tables if necessary
__init_db()
# init last block id from db
__last_block_id, __last_tx_id = __init_vars()


def __get_block(block_id):
    with closing(db.cursor()) as cursor:
        __query = "SELECT " + __root_hash + "," +\
                           __blockchain_tx_hash + " FROM " + __blocks +\
                           " WHERE " + __block_id + " = " + str(block_id) + ";"
        try:
            cursor.execute(__query)
        except (AttributeError, MySQLdb.OperationalError):
            db.connect(user=Configs.user, passwd=Configs.password)
            cursor.execute(__query)
        result = cursor.fetchone()
        return {"root_hash": result[0], "blockchain_tx_hash": result[1]}


def __set_last_block_id(val):
    with closing(db.cursor()) as cursor:
        global __last_block_id
        if val < __last_block_id:
            raise ValueError("val should be more than" + str(__last_block_id))
        __query = "UPDATE {} SET {} =  {} WHERE {} = '{}';".format(
            __settings,
            __settings_value,
            val,
            __settings_key,
            "last_block_id"
        )
        try:
            cursor.execute(__query)
        except (AttributeError, MySQLdb.OperationalError):
            db.connect(user=Configs.user, passwd=Configs.password)
            cursor.execute(__query)
        __last_block_id = val


def __set_last_tx_id(val):
    with closing(db.cursor()) as cursor:
        global __last_tx_id
        if val < __last_tx_id:
            raise ValueError("val should be more than" + str(__last_tx_id))
        __query = "UPDATE {} SET {} =  {} WHERE {} = '{}';".format(
                __settings,
                __settings_value,
                val,
                __settings_key,
                "last_tx_id"
            )
        try:
            cursor.execute(__query)
        except (AttributeError, MySQLdb.OperationalError):
            db.connect(user=Configs.user, passwd=Configs.password)
            cursor.execute(__query)
        __last_tx_id = val


def save_tx(shop_id, _hash):
    with closing(db.cursor()) as cursor:
        __query = "INSERT INTO {} ({}, {}) VALUES ({}, '{}');".format(
            __transactions,
            __shop_id,
            __hash,
            str(shop_id),
            _hash
        )
        try:
            cursor.execute(__query)
        except (AttributeError, MySQLdb.OperationalError):
            db.connect(user=Configs.user, passwd=Configs.password)
            cursor.execute(__query)


def test_save_txs(shop_ids, _hashes):
    # function used only for tests
    with closing(db.cursor()) as cursor:
        __query = "INSERT INTO {} ({}, {}) VALUES ".format(
                __transactions,
                __shop_id,
                __hash
        )
        for i in range(len(_hashes)):
            __query += str((shop_ids[i], _hashes[i])) + ", "
        __query = __query[:-2] + ";"
        try:
            cursor.execute(__query)
        except (AttributeError, MySQLdb.OperationalError):
            db.connect(user=Configs.user, passwd=Configs.password)
            cursor.execute(__query)


def get_txs_for_new_block():
    with closing(db.cursor()) as cursor:
        __query = "SELECT id, {} FROM {} WHERE id > {} ;".format(
            __hash,
            __transactions,
            __last_tx_id
        )
        try:
            cursor.execute(__query)
        except (AttributeError, MySQLdb.OperationalError):
            db.connect(user=Configs.user, passwd=Configs.password)
            cursor.execute(__query)
        hashes = []
        t = cursor.fetchall()
        for row in t:
            hashes.append(row)
    return __last_block_id + 1, hashes


def save_block(block_id, root_hash, blockchain_tx_hash, txs):
    with closing(db.cursor()) as cursor:
        __query = "UPDATE {} SET {} = {} WHERE {} >= {} AND {} <= {};".format(
            __transactions,
            __block_id,
            block_id,
            "id",
            txs[0][0],
            "id",
            txs[-1][0]
        )
        try:
            cursor.execute(__query)
        except (AttributeError, MySQLdb.OperationalError):
            db.connect(user=Configs.user, passwd=Configs.password)
            cursor.execute(__query)
        __set_last_block_id(block_id)
        __set_last_tx_id(txs[-1][0])
        __query = "INSERT INTO {} ({}, {}, {}) VALUES ({},'{}','{}');".format(
            __blocks,
            __block_id,
            __root_hash,
            __blockchain_tx_hash,
            block_id,
            root_hash,
            blockchain_tx_hash
        )
        try:
            cursor.execute(__query)
        except (AttributeError, MySQLdb.OperationalError):
            db.connect(user=Configs.user, passwd=Configs.password)
            cursor.execute(__query)


def get_block_by_tx_hash(tx_hash):
    with closing(db.cursor()) as cursor:
        __query = "SELECT {0}, {1} FROM {2} WHERE {3} = '{4}';".format(
            __block_id,
            __date,
            __transactions,
            __hash,
            tx_hash
        )
        try:
            cursor.execute(__query)
        except (AttributeError, MySQLdb.OperationalError):
            db.connect(user=Configs.user, passwd=Configs.password)
            cursor.execute(__query)
        tx = cursor.fetchall()
        blocks = []
        for row in tx:
            if row is None or row[0] is None:
                continue
            blocks.append((__get_block(row[0]), row[1]))
        return blocks
