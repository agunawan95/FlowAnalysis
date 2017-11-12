import database


class Enterprise(database.Database):
    """
    This is a Enterprise Helper Class based on Enterprise Entity
    """

    msg = ""

    def add_enterprise(self, name, address, email, phone, filesize, user_limit, admin):

        """
        :param name: Name of Enterprise (Enterprise Data)
        :param address: Address of Enterprise (Enterprise Data)
        :param email: Email of Enterprise (Enterprise Data)
        :param phone: Phone of Enterprise (Enterprise Data)
        :param filesize: Maximum File Size this Enterprise can Have
        :param user_limit: Maximum User this Enterprise can Have
        :param admin: User ID Assigned as Administrator for this Enterprise
        :type name: String
        :type address: String
        :type email: String
        :type phone: String
        :type filesize: int
        :type user_limit: int
        :type admin: int
        :return: True if Successfully add a Enterprise, False if Failed
        :rtype: boolean
        """

        sql = "INSERT INTO enterprise VALUES (default, '" + name + "', '" + address + "', '" + email + "', '" + phone + "', " + str(filesize) + ", " + str(user_limit) + ", " + str(admin) + ")"
        res = self.cur.execute(sql)
        if res:
            self.con.commit()
        return res

    def get_enterprise_by_user(self, id):

        """
        :param id: User ID that is an Administrator of an Enterprise
        :type id: int
        :return: Dictionary of an User
        :rtype: Dictionary
        """

        sql = "SELECT * FROM enterprise WHERE admin = " + str(id)
        self.cur.execute(sql)
        data = self.cur.fetchone()
        return data

    def update_enterprise(self, id, name, address, email, phone, filesize, user_limit):

        """
        :param id: ID of an Enterprise
        :param name: New Name for this Enterprise
        :param address: New Address for this Enterprise
        :param email: New Email for this Enterprise
        :param phone: New Phone Number for this Enterprise
        :param filesize: New File Size Limit for this Enterprise
        :param user_limit: New User Count Limit for this Enterprise
        :type id: int
        :type name: String
        :type address: String
        :type email: String
        :type phone: String
        :type filesize: int
        :type user_limit: int
        :return: True if Successfully edit a Enterprise, False if Failed
        :rtype: boolean
        """

        sql = "UPDATE enterprise SET name = '" + name + "', address = '" + address + "', email = '" + email + "', phone = '" + phone + "', filesize_limit = " + str(filesize) + ", user_limit = " + str(user_limit) + " WHERE admin = " + str(id)
        if self.cur.execute(sql):
            self.con.commit()
            return True
        else:
            self.msg = "No Change Have Made!"
            return False

    def error_msg(self):

        """
        :return: Last Recorded Error Message
        :rtype: String
        """

        return self.msg
