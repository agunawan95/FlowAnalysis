import database
import hashlib
import pymysql
import os


class User(database.Database):
    """
    This is a File Helper Class based on File Entity
    """
    err = 0
    msg = ''
    data = None
    count = 0
    user_per_page = 10
    offset = 0

    def __init__(self):
        database.Database.__init__(self)
        sql = "SELECT COUNT(*) as count FROM user"
        self.cur.execute(sql)
        self.count = self.cur.fetchone()['count']

    def set_user_per_page(self, user_count):
        self.user_per_page = user_count

    def set_offset(self, offset):
        self.offset = offset

    def next_page(self):
        self.offset += self.user_per_page

    def get_page_count(self):
        return round(self.count / self.user_per_page)

    def login(self, username, password):
        """
        Login to System

        :param username: Username of User
        :param password: Password of User
        :type username: String
        :type password: String
        :return: True if Successfully login to System, False if Failed
        :rtype: boolean
        """
        sql = "SELECT * FROM user WHERE username = '" + username + "' AND password = '" + password + "'"
        self.cur.execute(sql)
        data = self.cur.fetchone()
        self.data = data
        if self.cur.rowcount > 0:
            self.msg = "Success"
            return True
        if username == "" and password == "":
            self.msg = "Username and Password is Required"
            return False
        if username == "":
            self.msg = "Username is Required"
            return False
        if password == "":
            self.msg = "Password is Required"
            return False
        self.msg = "Wrong Username or Password"
        return False

    def err_msg(self):
        """
        :return: Last Recorded Error Message
        :rtype: String
        """
        return self.msg

    def get_data(self):
        """
        :return: Dictionary of User
        :rtype: Dictionary
        """
        return self.data

    def get_users(self):
        """
        Get all Users Except Root

        :return: List of User
        :rtype: List
        """
        sql = "SELECT * FROM user WHERE auth <> 'root' LIMIT " + str(self.user_per_page) + " OFFSET " + str(self.offset)
        self.cur.execute(sql)
        data = self.cur.fetchall()
        return data

    def get_all_admin(self):
        """
        Get all Administrator

        :return: List of User
        :rtype: List
        """
        sql = "SELECT * FROM user WHERE auth = 'admin' LIMIT " + str(self.user_per_page) + " OFFSET " + str(self.offset)
        self.cur.execute(sql)
        data = self.cur.fetchall()
        return data

    def get_enterprise_user(self, id):
        """
        Get User of Certain Enterprise

        :param id: Administrator ID
        :return: List of User
        :rtype: List
        """
        sql = "SELECT * FROM user WHERE auth <> 'root' AND admin = " + str(id)
        self.cur.execute(sql)
        data = self.cur.fetchall()
        return data

    def add_user(self, username, password, email, auth, admin):
        """
        Add a User to System, and to Gitlab

        :param username: Username of a User
        :param password: Password of a User
        :param email: Email of a User
        :param auth: Authentication of a User
        :param admin: Administrator of a User
        :type username: String
        :type password: String
        :type auth: String
        :type admin: int
        :return: True if Successfully add user, False if Failed
        :rtype: boolean
        """
        if username == "" and password == "":
            self.msg = "Username and Password is Required"
            return False
        if username == "":
            self.msg = "Username is Required"
            return False
        if email == "":
            self.msg = "Email is Required"
            return False
        if password == "":
            self.msg = "Password is Required"
            return False
        if auth == "":
            self.msg = "Authentication Level is Required"
            return False
        sql = "SELECT * FROM user WHERE username = '" + username + "'"
        self.cur.execute(sql)
        if self.cur.rowcount > 0:
            self.msg = "Username Already Exist"
            return False
        hash_object = hashlib.sha256(str(username).encode("utf-8"))
        hex = hash_object.hexdigest()
        home_folder = hex[0:30]

        basedir = os.getcwd()
        if not os.path.exists(basedir + "/upload/" + home_folder):
            os.makedirs(basedir + "/upload/" + home_folder)
        if not os.path.exists(basedir + "/upload/" + home_folder + "/files"):
            os.makedirs(basedir + "/upload/" + home_folder + "/files")
        if not os.path.exists(basedir + "/upload/" + home_folder + "/project"):
            os.makedirs(basedir + "/upload/" + home_folder + "/project")

        sql = "INSERT INTO user VALUES(default, '" + username + "', '" + email + "', '" + password + "', '" + home_folder + "', '" + auth + "', " + str(admin) + ")"
        if self.cur.execute(sql):
            # self.gl.users.create({
            #    'email': email,
            #    'password': password,
            #    'username': username,
            #    'name': username,
            #    'skip_confirmation': True
            # })
            self.con.commit()
            self.msg = "Success"
            return True
        else:
            self.msg = "Cannot Add New User to Database"
            return False

    def load_user(self, id):
        """
        Load a User Based of User ID

        :param id: User ID
        :type id: int
        :return: Safe User Dictionary (Without Password)
        :rtype: Dictionary
        """
        sql = "SELECT * FROM user WHERE id = " + str(id)
        self.cur.execute(sql)
        if self.cur.rowcount > 0:
            self.data = self.cur.fetchone()
            res = {
                "id": self.data['id'],
                "username": self.data['username'],
                "home_folder": self.data['home_folder'],
                "auth": self.data['auth']
            }
            return res
        else:
            return False

    def delete_user(self, id):
        """
        Delete User

        :param id: User ID
        :type id: int
        :return: True if Successfully delete user, False if Failed
        :rtype: boolean
        """
        sql = "DELETE FROM user WHERE id = " + str(id)
        if self.cur.execute(sql):
            self.con.commit()
            self.msg = "Success"
            return True
        else:
            self.msg = "Cannot Delete User From Database"
            return False

    def change_password(self, id, password):
        """
        Change Password of a User

        :param id: User ID
        :param password: New Password
        :type id: int
        :type password: String
        :return: True if Successfully update user, False if Failed
        :rtype: boolean
        """
        sql = "UPDATE user SET password = '" + password + "' WHERE id = " + str(id)
        if self.cur.execute(sql):
            self.con.commit()
            self.msg = "Success"
            return True
        else:
            self.msg = "Cannot Change User Password To Database"
            return False

    def change_username(self, id, username):
        """
        Change Username of a User

        :param id: User ID
        :param username: New Username
        :type id: int
        :type username: String
        :return: True if Successfully update user, False if Failed
        :rtype: boolean
        """
        sql = "UPDATE user SET username = '" + username + "' WHERE id = " + str(id)
        if username != '':
            if self.cur.execute(sql):
                self.con.commit()
                self.msg = "Success"
                return True
            else:
                self.msg = "No Data Affected"
                return False
        else:
            self.msg = "Username Must Have Value"
            return False

    def search_admin(self, query):
        """
        Search Administrator

        :param query: Query for Searching
        :type query: String
        :return: List of User
        :rtype: List
        """
        sql = "SELECT * FROM user WHERE username LIKE '%" + query + "%' AND auth = 'admin'"
        self.cur.execute(sql)
        data = self.cur.fetchall()
        return data

    def search_user(self, query, id):
        """
        Search Enterprise User

        :param query: Query for Searching User
        :param id: ID of an Administrator
        :type query: String
        :type id: int
        :return: List of a User
        :rtype: List
        """
        sql = "SELECT * FROM user WHERE username LIKE '%" + query + "%' AND admin = " + str(id)
        self.cur.execute(sql)
        data = self.cur.fetchall()
        return data

    def get_by_username(self, username):
        """
        Get User by Username

        :param username: Username of a User
        :type username: String
        :return: Dictionary of User
        :rtype: Dictionary
        """
        sql = "SELECT * FROM user WHERE username = '" + username + "'"
        self.cur.execute(sql)
        data = self.cur.fetchone()
        return data