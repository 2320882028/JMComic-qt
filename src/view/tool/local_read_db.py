import json
import os.path

from PySide6.QtSql import QSqlDatabase, QSqlQuery
import sqlite3
from config.setting import Setting
from task.task_local import LocalData
from tools.log import Log
from view.download.download_item import DownloadItem, DownloadEpsItem


class LocalReadDb(object):
    def __init__(self):
        self.db = sqlite3.connect(os.path.join(Setting.GetLocalHomePath(), "local_read.db"), check_same_thread=False)
        self.cur = self.db.cursor()

        sql = """\
            create table if not exists local_book(\
            id varchar primary key,\
            title varchar,\
            file varchar,\
            path varchar,\
            cover varchar,\
            category varchar,\
            epsId int,\
            isZipFile int,\
            lastIndex int,\
            lastEpsId int,\
            addTime int,\
            lastReadTime int,\
            picCnt int,\
            pic varchar,\
            main_id varchar\
            )\
            """
        try:
            suc = self.db.execute(sql)
        except Exception as es:
            Log.Error(es)

    def DelDownloadDB(self, bookId):
        sql = "delete from local_book where id='{}'".format(bookId)
        suc = self.cur.execute(sql)
        self.cur.execute("COMMIT")
        return

    def GetSaveStr(self, name):
        return name.replace("'", "''")

    def AddLoadLocalBook(self, info):
        assert isinstance(info, LocalData)
        sql = "INSERT INTO local_book(id, title, file, path, cover, epsId, isZipFile, lastIndex, lastEpsId, addTime, lastReadTime, picCnt, main_id) " \
              "VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', {5}, {6}, {7}, {8}, {9}, {10}, {11}, '{12}') " \
              "ON CONFLICT(id) DO UPDATE SET lastIndex='{7}', file='{2}', path='{3}', lastEpsId={8}, addTime={9}, lastReadTime={10}, picCnt={11}, cover='{4}' ".\
            format(info.id, self.GetSaveStr(info.title), self.GetSaveStr(info.file), self.GetSaveStr(info.path), self.GetSaveStr(info.cover), info.epsId, int(info.isZipFile), info.lastIndex
                   , info.lastEpsId, info.addTime, info.lastReadTime, info.picCnt, info.main_id)

        suc = self.cur.execute(sql)
        self.cur.execute("COMMIT")
        return

    def LoadLocalBook(self):
        suc = self.cur.execute(
            """
            select id, main_id, title, file, path, cover, epsId, isZipFile, lastIndex, lastEpsId,addTime,lastReadTime,picCnt,pic  from local_book
            """
        )

        downloads = {}
        for query in self.cur.fetchall():
            # bookId, downloadEpsIds, curDownloadEpsId, curConvertEpsId, title, savePath, convertPath
            info = LocalData()
            info.id = query[0]
            info.main_id = query[1]
            info.title = query[2]
            info.file = query[3]
            info.path = query[4]
            info.cover = query[5]
            info.epsId = query[6]
            info.isZipFile = bool(query[7])
            info.lastIndex = query[8]
            info.lastEpsId = query[9]
            info.addTime = query[10]
            info.lastReadTime = query[11]
            info.picCnt = query[12]
            # info.pic = json.loads(query[13])
            # info.pic = [i for i in info.pic]
            downloads[info.id] = info
        books = {}
        for v in downloads.values():
            if v.main_id != v.id:
                newV = downloads.get(v.main_id)
                if not newV:
                    continue
                newV.eps.append(v)
                newV.eps.sort(key=lambda a: a.epsId)
            else:
                books[v.id] = v
        return books
