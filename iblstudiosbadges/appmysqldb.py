

import MySQLdb

class mysql:
    """
    MySQL class provides easy 
    interaction with MySQL databases
    """
    def __init__(self, db_host, db_port, db_name, db_user, db_pass):
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_name = db_name
        self.dbh = None

    def connect(self):
        """ Connect to the database """
        if self.dbh == None:
            self.dbh = MySQLdb.connect(host=self.db_host, user=self.db_user, passwd=self.db_pass, db=self.db_name, charset='utf8', use_unicode=1)

    def query(self, query):
        """ Exectue a query """
        self.connect()
        self.cur = self.dbh.cursor()
        self.res = self.cur.execute(query)
        return self.res

    def numrows(self):
        """ Return the num of results """
        return self.cur.rowcount

    def fetchall(self):
        """ Fetchall results """
        return self.cur.fetchall()

    def showConfig(self):
        result = "db_host : %s" % (self.db_host)
        result += "db_name : %s" % (self.db_name)
        result += "db_user : %s" % (self.db_user)
        result += "db_pass : %s" % (self.db_pass)
        return result

    def disconnect(self):
        """ Closing database connection """
        self.dbh.close()
