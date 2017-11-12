import pymysql
import gitlab


class Database:

    """
    This Class is Base Class for connecting Database MySQL to Inheritance Helper Class
    This Class Have 2 Member Variable con & cur for Connection and Cursor
    """

    con = None
    cur = None
    gl = None

    def __init__(self):

        """
        Initialize Connection to Database MySQL and Create a Cursor

        :rtype: void
        """

        self.con = pymysql.connect(host='localhost', user='root', password='', db='flow_analysis')
        self.cur = self.con.cursor(pymysql.cursors.DictCursor)
        # self.initGitlab()

    def initGitlab(self):
        """
        Initialize Gitlab API Connection (Authorization)
        :return: None
        :rtype: void
        """
        self.gl = gitlab.Gitlab(url='http://192.168.1.12', private_token='b16g6FKQiVsrVJahVzzj', api_version="4")
        self.gl.auth()
