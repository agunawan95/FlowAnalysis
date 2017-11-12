import database
import datetime
import os


class Files(database.Database):
    """
    This is a File Helper Class based on File Entity
    """
    data = None
    msg = ""

    def user_file(self, id):

        """
        :param id: User ID
        :type id: int
        :return: List of Files Owned by User
        :rtype: List
        """

        sql = "SELECT * FROM files f LEFT JOIN recycle r ON r.id_file = f.id WHERE f.owner = " + str(id) + " AND r.id is null"
        self.cur.execute(sql)
        data = self.cur.fetchall()
        return data

    def add_file(self, name, owner, location):

        """
        :param name: Name of a File
        :param owner: User ID that Own the Uploaded File
        :param location: Where the File Located
        :type name: String
        :type owner: int
        :type location: String
        :return: True if Successfully add a File, False if Failed
        :rtype: boolean
        """

        today = datetime.datetime.now()
        sql = "INSERT INTO files VALUES(default, '" + name + "', " + str(owner) + ", '" + str(today) + "', '" + location + "')"
        if self.cur.execute(sql):
            self.con.commit()
            return True
        else:
            return False

    def load_file(self, id):

        """
        :param id: ID of a File
        :type id: int
        :return: No Return, it will fill a member variable in this object (Use get_data Function to get Data)
        :rtype: void
        """

        sql = "SELECT * FROM files WHERE id = " + str(id)
        self.cur.execute(sql)
        self.data = self.cur.fetchone()

    def get_data(self):

        """
        :return: Dictionary of File
        :rtype: Dictionary
        """

        return self.data

    def delete_file(self, upload_folder):
        """
        Delete Record on Database and the Actual File in the System
        The Deleted File are Based on ID that Loaded

        :param upload_folder: What Folder Contain Targeted File
        :return: True if Successfully delete a File, False if Failed
        :rtype: boolean
        """
        if self.data is not None:
            basedir = os.getcwd()
            path = basedir + upload_folder + "/" + self.data['location']
            os.remove(path)

            # Delete Shared Files
            sql = "DELETE FROM shared_files WHERE id_file = " + str(self.data['id'])
            if self.cur.execute(sql):
                self.con.commit()

            sql = "DELETE FROM files WHERE id = " + str(self.data['id'])
            if self.cur.execute(sql):
                self.con.commit()
                return True
            else:
                self.msg = "Cannot Delete File Metadata on Server"
                return False

    def err_msg(self):

        """
        :return: Last Recorded Error Message
        :rtype: String
        """

        return self.msg

    def search_file(self, id, query):

        """
        Search File Based on Name

        :param id: User ID
        :param query: a String that Indicate a File
        :type id: int
        :type query: String
        :return: List of Files Data
        :rtype: List
        """

        sql = "SELECT * FROM files WHERE owner = " + str(id) + " AND name LIKE '%" + query + "%'"
        self.cur.execute(sql)
        data = self.cur.fetchall()
        return data

    def search_shareable_user(self, id_user, file):

        """
        Seach Potential Share User

        :param id_user: User ID Owner of a File
        :param file: File ID of Targeted File
        :type id_user: int
        :type file: int
        :return: List of Potential User
        :rtype: List
        """

        sql = "SELECT * FROM user WHERE id = " + str(id_user)
        self.cur.execute(sql)
        user = self.cur.fetchone()

        if user['auth'] == "admin":
            sql = "SELECT id, username FROM user WHERE id NOT IN (SELECT id_user FROM shared_files WHERE id_file = " + str(file) + ") AND admin = " + str(id_user)
        elif user['auth'] == 'user':
            sql = "SELECT id, username FROM user WHERE id NOT IN (SELECT id_user FROM shared_files WHERE id_file = " + str(file) + ") AND (admin = " + str(user['admin']) + " OR id = " + str(user['admin'])
        elif user['auth'] == 'root':
            sql = "SELECT id, username FROM user WHERE id NOT IN (SELECT id_user FROM shared_files WHERE id_file = " + str(file) + ") AND auth = 'admin'"

        self.cur.execute(sql)
        data = self.cur.fetchall()
        return data

    def share_detail(self, file):

        """
        List of User that Have Access of a File Owned by Other User

        :param file: ID File of Targeted File
        :type file: int
        :return: List of User
        :rtype: List
        """

        sql = "SELECT sf.id, u.username, DATE_FORMAT(sf.shared_at, '%W, %d %M %Y') as shared_at, sf.permission FROM user u JOIN shared_files sf ON sf.id_user = u.id WHERE sf.id_file = " + str(file)
        self.cur.execute(sql)
        data = self.cur.fetchall()
        return data

    def share_file(self, users, file, permission):

        """
        Share a File to Other User with Some Permission

        :param users: User ID Targeted User for Share
        :param file: File ID of a File
        :param permission: Permission of Shared File {r(Read), w(Read & Write)}
        :type users: int
        :type file: int
        :type permission: String
        :return: True if Successfully share a File, False if Failed
        :rtype: boolean
        """

        if users is '':
            self.msg = "No User Selected"
            return False
        if permission is not 'r' and permission is not 'w':
            permission = 'r'
        today = str(datetime.datetime.now())
        users = str(users).strip().split(",")
        for user in users:
            sql = "INSERT INTO shared_files VALUES(default, " + user + ", " + str(file) + ", '" + today + "', '" + permission + "')"
            if self.cur.execute(sql):
                self.con.commit()
        return True

    def get_shared_file(self, id_user):
        """
        Get Files That Shared to Targeted User

        :param id_user: Targeted User ID
        :type id_user: int
        :return: List of File
        :rtype: List
        """
        sql = "SELECT f.location, f.name, f.id FROM shared_files sf JOIN files f ON f.id = sf.id_file WHERE sf.id_user = " + str(id_user)
        self.cur.execute(sql)
        data = self.cur.fetchall()
        return data

    def search_shared_file(self, id_user, query):
        """
        Search From Sharable File

        :param id_user: ID User
        :param query: Query for Search
        :type id_user: int
        :type query: String
        :return: List of File
        :rtype: List
        """
        sql = "SELECT f.location, f.name, f.id FROM shared_files sf JOIN files f ON f.id = sf.id_file WHERE sf.id_user = " + str(id_user) + " AND f.name LIKE '%" + query + "%'"
        self.cur.execute(sql)
        data = self.cur.fetchall()
        return data

    def check_shared(self, user, file):
        """
        Check if User Have Access of a File

        :param user: User ID
        :param file: File ID
        :type user: int
        :type file: int
        :return: True if User Have Access, False if No
        :rtype: boolean
        """
        sql = "SELECT * FROM shared_files WHERE id_user = " + str(user) + " AND id_file = " + str(file)
        self.cur.execute(sql)
        row = self.cur.rowcount
        return row > 0

    def transfer_protocol(self, user, admin):
        """
        Protocol for Transfer File Owner to Enterprise Administrator if a User Deleted

        :param user:  User ID of Targeted User
        :param admin: Administrator of a User
        :type user: int
        :type admin: int
        :return: True if Successfully Transfer Files Permission, False if Failed
        :rtype: boolean
        """
        sql = "UPDATE files SET owner = " + str(admin) + " WHERE owner = " + str(user)
        if self.cur.execute(sql):
            self.con.commit()
            return True
        else:
            return False

    def get_recycle_bin(self, admin):
        """
        List of File in Enterprise Recycle Bin

        :param admin:  ID of Administrator of a Enterprise
        :type admin: int
        :return: List of File
        :rtype: List
        """
        sql = "SELECT r.*, f.location, f.name, f.id AS id_file FROM recycle r JOIN files f ON f.id = r.id_file WHERE r.id_admin = " + str(admin)
        self.cur.execute(sql)
        data = self.cur.fetchall()
        return data

    def restore_file(self, id_recycle):
        """
        Restore File in Enterprise Recycle Bin

        :param id_recycle: ID of Recycle Process of a File
        :type id_recycle: int
        :return: True if Successfully restore a File, False if Failed
        :rtype: boolean
        """
        sql = "DELETE FROM recycle WHERE id = " + str(id_recycle)
        if self.cur.execute(sql):
            self.con.commit()
            return True
        else:
            self.msg = "Cannot Delete From Database"
            return False

    def recycle_file(self, id_file, id_admin):
        """
        Send File to Enterprise Recycle Bin

        :param id_file:  ID of Targeted File
        :param id_admin: ID of User Administrator
        :type id_file: int
        :type id_admin: int
        :return: True if Successfully recycle a File, False if Failed
        :rtype: boolean
        """
        today = datetime.datetime.now()
        sql = "INSERT INTO recycle VALUES(default, " + str(id_admin) + ", " + str(id_file) + ", '" + str(today) + "')"
        if self.cur.execute(sql):
            self.con.commit()
            return True
        else:
            self.msg = "Cannot Recycle File"
            return False

    def search_recycle(self, admin, query):
        """
        Search File in Enterprise Recycle Bin

        :param admin: Administrator ID
        :param query: Query for Search a File
        :type admin: int
        :type query: String
        :return: List of File
        :rtype: List
        """
        sql = "SELECT r.*, f.location, f.name, f.id AS id_file FROM recycle r JOIN files f ON f.id = r.id_file WHERE r.id_admin = " + str(admin) + " AND f.name LIKE '%" + query + "%'"
        self.cur.execute(sql)
        data = self.cur.fetchall()
        return data

    def unshare(self, id):
        sql = "DELETE FROM shared_files WHERE id = " + str(id)
        if self.cur.execute(sql):
            self.con.commit()
            return True
        else:
            self.msg = "Cannot Delete From Database"
            return False

