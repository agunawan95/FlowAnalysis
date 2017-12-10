import database
import pymysql
import os
import datetime
import shutil


class Project(database.Database):
    git_location = ''
    err = 0
    err_msg = ''

    def __init__(self):
        database.Database.__init__(self)
        self.err = 0
        self.err_msg = ''
        self.git_location = "git@localhost:/home/git/Data/"
        
    def add_project(self, owner, name, upload_folder, home_folder):
        sql = "SELECT * FROM projects WHERE owner = " + str(owner) + " AND name = '" + name + "'"
        self.cur.execute(sql)
        if self.cur.rowcount > 0:
            self.err = 1
            self.err_msg = 'Name Already Exist'
        else:
            today = datetime.datetime.now()
            url = self.git_location + str(owner) + "/" + name.replace(' ', '_').strip()
            sql = "INSERT INTO projects VALUES(default, " + str(owner) + ", '" + name + "', '" + str(today) + "', '" + url + "')"
            self.cur.execute(sql)
            self.con.commit()
            self.err_msg = "Success"

            basedir = os.getcwd()
            if not os.path.exists(basedir + upload_folder + "/" + home_folder + "/projects"):
                os.makedirs(basedir + upload_folder + "/" + home_folder + "/projects")
            if not os.path.exists(basedir + upload_folder + "/" + home_folder + "/projects" + '/' + name):
                os.makedirs(basedir + upload_folder + "/" + home_folder + "/projects" + '/' + name)
            if not os.path.exists(basedir + upload_folder + "/" + home_folder + "/projects" + '/' + name + '/charts'):
                os.makedirs(basedir + upload_folder + "/" + home_folder + "/projects" + '/' + name + '/charts')
            if not os.path.exists(basedir + upload_folder + "/" + home_folder + "/projects" + '/' + name + '/models'):
                os.makedirs(basedir + upload_folder + "/" + home_folder + "/projects" + '/' + name + '/models')
            return True
        return False

    def scan_project(self, home_folder, project_id):
        sql = "SELECT * FROM projects WHERE id = " + str(project_id)
        self.cur.execute(sql)
        data = self.cur.fetchone()

        target = 'upload/' + home_folder + '/projects/' + data['name']
        charts = [f for f in os.listdir(target + '/charts') if os.path.isfile(os.path.join(target + '/charts', f))]
        models = [f for f in os.listdir(target + '/models') if os.path.isfile(os.path.join(target + '/models', f))]
        res = {
            'charts': charts,
            'models': models
        }
        return res

    def all_projects(self):
        sql = "SELECT * FROM projects"
        self.cur.execute(sql)
        data = self.cur.fetchall()
        return data

    def get_project(self, id):
        sql = "SELECT * FROM projects WHERE id = " + str(id)
        self.cur.execute(sql)
        data = self.cur.fetchone()
        return data

    def get_user_project(self, id):
        sql = "SELECT * FROM projects WHERE owner = " + str(id)
        self.cur.execute(sql)
        data = self.cur.fetchall()
        return data

    def delete_project(self, upload, home_folder, id):
        sql = "SELECT * FROM projects WHERE id = " + str(id)
        self.cur.execute(sql)
        data = self.cur.fetchone()

        target = 'upload/' + home_folder + '/projects/' + data['name']
        shutil.rmtree(target)

        sql = "DELETE FROM projects WHERE id = " + str(id)
        self.cur.execute(sql)
        self.con.commit()
        return True

    def get_error_msg(self):
        return self.err_msg