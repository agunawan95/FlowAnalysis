import database
import os
import datetime


class Log(database.Database):

    def __init__(self):
        database.Database.__init__(self)

    def write(self, actor, level, log, project = 0):
        today = datetime.datetime.now()
        sql = "INSERT INTO log VALUES(default, '" + str(today) + "', " + str(actor) + ", '" + level + "', '" + log + "', " + str(project) + ")"
        self.cur.execute(sql)
        self.con.commit()

    def read(self, actor):
        sql = "SELECT * FROM log WHERE actor = " + str(actor)
        self.cur.execute(sql)
        data = self.cur.fetchall()
        return data

    def get_project_log_heatmap(self, actor, project):
        sql = "SELECT date, COUNT(log) FROM log GROUP BY date WHERE actor = " + str(actor) + " AND project = " + str(project)
        self.cur.execute(sql)
        data = self.cur.fetchall()
        return data