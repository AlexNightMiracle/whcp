import sys
from datetime import timedelta, datetime
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel, QSqlError
import sys
import os
from pyform1 import *
import string
import calendar
import sqlite3
import math
import time
from functools import partial

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        #self.rate = 155.64
        #self.trs = 1000
        self.qbt = [0] * 7
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.curdate = datetime.now()
#блок открытия БД
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('dbwt.db')
        self.db.open()
        self.query = QSqlQuery()
        self.query.exec("CREATE TABLE IF NOT EXISTS wt (    date    DATE   PRIMARY KEY,    time1   TIME,    time2   TIME,    time3   TIME,    time4   TIME,    time5   TIME,    profit  DOUBLE,    difference BOOLEAN, route INT, release INT, trs INT);")    
        self.query.exec("CREATE TABLE IF NOT EXISTS norms (date DATE,   nh   INT)")
        self.query.exec("CREATE TABLE IF NOT EXISTS template (    release  INT,    route      INT,    drive      TIME,    other      TIME,    night      TIME,    difference BOOLEAN,    weekand    BOOLEAN);")
        self.query.exec("CREATE TABLE IF NOT EXISTS sc (    rate  DOUBLE,    night DOUBLE,    idle  DOUBLE,    trs   INT, route  INT, release  INT, id INT PRIMARY KEY);")
        self.query.prepare("INSERT INTO sc (rate, trs, route, release, id) VALUES (155.64, 1000, 1, 1, 1)")
        self.query.exec()
        self.query.prepare("DELETE FROM sc WHERE id != 1")
        self.query.exec()
#подгрузка данных
        self.loaddist()
#блок вывода БД на таблицу ЭС1        
        model = QSqlQueryModel()
        model.setQuery('SELECT * FROM wt')
        self.ui.tableView.setModel(model)
        model.setHeaderData(0, Qt.Horizontal, "Дата")
        model.setHeaderData(1, Qt.Horizontal, "Рулевые")
        model.setHeaderData(2, Qt.Horizontal, "Прочее")
        model.setHeaderData(3, Qt.Horizontal, "Ночные")
        model.setHeaderData(4, Qt.Horizontal, "Простой")
        model.setHeaderData(5, Qt.Horizontal, "Часов на смене")
        model.setHeaderData(6, Qt.Horizontal, "Доход")
#блок вывода БД на ЭС2
        self.ui.dateEdit_4.dateChanged.connect(self.givedate)
#блок регулировки дат ЭВД
        self.ui.dateEdit.setDate(self.curdate)
        self.ui.dateEdit_4.setDate(self.curdate)
#блок вызова событий нажатия внопок ЭВД
        self.ui.pushButton.clicked.connect(self.disp2)
        self.ui.pushButton_2.clicked.connect(self.savenh)
        self.ui.pushButton_3.clicked.connect(self.loadtemplate)
        self.ui.pushButton_4.clicked.connect(self.inserttemplate)
        self.ui.pushButton_5.clicked.connect(self.updatemr)
        self.ui.pushButton_6.clicked.connect(self.updatetrs)
        self.ui.pushButton_7.clicked.connect(self.updaterate)
#блок вызова событий изменения времени на ЭВД     
        self.ui.timeEdit.timeChanged.connect(self.disp1)
        self.ui.timeEdit_2.timeChanged.connect(self.disp1)
        self.ui.timeEdit_3.timeChanged.connect(self.disp1)
        self.ui.timeEdit_4.timeChanged.connect(self.disp1)
        self.ui.dateEdit.dateChanged.connect(self.disp1)
#блок обработки события изменения времени ЭВД
    def disp1(self):
        pay1, pay2, pay3 = self.rate, (self.rate / 2.5), (self.rate / 1.5)
        difference = self.ui.checkBox.isChecked()
        v1 = self.ui.timeEdit.time().toPyTime() # рулевое
        v2 = self.ui.timeEdit_2.time().toPyTime() # прочее
        v3 = self.ui.timeEdit_3.time().toPyTime() # ночные
        v4 = self.ui.timeEdit_4.time().toPyTime() # простой
        self.th1, self.tm1, ts1 = v1.hour, v1.minute, v1.second
        self.th2, self.tm2, ts2 = v2.hour, v2.minute, v2.second
        self.th3, self.tm3, ts3 = v3.hour, v3.minute, v3.second
        self.th4, self.tm4, ts4 = v4.hour, v4.minute, v4.second
        
        self.th5, self.tm5, ts5 = self.th1 + self.th2, self.tm1 + self.tm2, ts1 + ts2
        self.tm5, ts5 = self.tm5 + ts5 // 60, ts5 % 60
        self.th5, self.tm5 = self.th5 + self.tm5 // 60, self.tm5 % 60
        paytohours = (self.th1*pay1)+(self.tm1*(pay1/60))
        paytother = ((self.th2*pay1)+(self.tm2*(pay1/60)))+((self.th3*pay2)+(self.tm3*(pay2/60)))+((self.th4*pay3)+(self.tm4*(pay3/60)))
        
        if difference == False:
            self.profit = paytohours + paytother
        else:
            self.profit = (paytohours + (paytohours * 0.3)) + paytother
        self.ui.lcdNumber_2.display(self.profit)
        self.ui.lcdNumber.display("{0}:{1}".format(self.th5, self.tm5))
            
        return
#блок записи данных в БД с ЭВД
    def disp2(self):
        date = self.ui.dateEdit.date().toPyDate()
        year, month, day = date.year, date.month, date.day
        difference = self.ui.checkBox.isChecked()
        route = self.ui.spinBox_8.value()
        release = self.ui.spinBox_9.value()
        trs = self.ui.spinBox_6.value()
        self.query.prepare("INSERT INTO wt (date, time1, time2, time3, time4, time5, profit, difference, route, release, trs) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
        self.query.addBindValue(f'{day}.{month}.{year}')
        self.query.addBindValue(f'{self.th1}:{self.tm1}')
        self.query.addBindValue(f'{self.th2}:{self.tm2}')
        self.query.addBindValue(f'{self.th3}:{self.tm3}')
        self.query.addBindValue(f'{self.th4}:{self.tm4}')
        self.query.addBindValue(f'{self.th5}:{self.tm5}')
        self.query.addBindValue(self.profit)
        self.query.addBindValue(difference)
        self.query.addBindValue(route)
        self.query.addBindValue(release)
        self.query.addBindValue(trs)
        self.query.exec()
        self.loaddist()

        if self.query.lastError().text():
            msg = QMessageBox()
            msg.setText("Такая дата уже есть в базе!")
            msg.exec()
        else:
            msg = QMessageBox()
            msg.setText("Данные успешно внесены!")
            msg.exec()
        return
#Вывод на ЭС
    def disp3(self, year, month):
        str1 = calendar.monthcalendar(year, month)
        i = int(len(str1))
        j = 7
        monthprofit = [0] * 7
        monthallhours = [0] * 7
        monthallminutes = [0] * 7
        monthallseconds = [0] * 7
        toQtime1 = [0] * 7
        dateof = [0] * 7
        for x in range(0, i):
            for y in range(0, j):
                day = str(str1[x][y])
                dayz = int(day)
                if dayz > 0:
                    dateday = str(f'{day}.{month}.{year}')
                    self.ui.gridLayout_3.addWidget(QPushButton(str(f'{dateday}\n\n')), x, y)
                    self.s2 = QSqlQuery(self.db)
                    self.s2.prepare("SELECT * FROM wt WHERE date = ?")
                    self.s2.addBindValue(dateday)
                    self.s2.exec()
                    while self.s2.next():
                        self.qbt[x] = str(f'{self.s2.value(0)}\n{self.s2.value(5)}\n{self.s2.value(6)}')
                        dateof[x] = self.s2.value(0)
                        self.qbt[x] = QPushButton(self.qbt[x])
                        self.ui.gridLayout_3.addWidget(self.qbt[x], x, y)
                        self.qbt[x].setStyleSheet('QPushButton {background-color: green;}')
                        self.qbt[x].clicked.connect(partial(self.loadinfo, self.s2.value(0), self.s2.value(1), self.s2.value(2), self.s2.value(3), self.s2.value(4), self.s2.value(5), self.s2.value(6), self.s2.value(7), self.s2.value(8), self.s2.value(9), self.s2.value(10)))
                        if type(self.s2.value(6)) == float:
                            monthprofit[x] += self.s2.value(6)
                            toQtime1[x] = QTime.fromString(self.s2.value(5), "h:m")
                            if QTime.isValid(toQtime1[x]) == True and QTime.isNull(toQtime1[x]) == False:
                                toPytime1 = toQtime1[x].toPyTime()
                                monthallhours[x] += toPytime1.hour
                                monthallminutes[x] += toPytime1.minute
                                
        monthallminutes = sum(monthallminutes) + 0 // 60
        monthallhours = sum(monthallhours) + monthallminutes // 60
        monthallminutes = monthallminutes % 60

        models3 = QSqlQuery(self.db)
        models3.prepare("SELECT * FROM norms WHERE date = ?")
        datemonth = str(f'{month}.{year}')
        models3.addBindValue(datemonth)
        models3.exec()
        self.nh = 0
        while models3.next():
            self.nh += models3.value(1)
            
        if((monthallhours + (monthallminutes / 60)) > self.nh):
            monthreward = ((monthallhours * self.rate) * 0.4) + (((monthallminutes * self.rate) * 0.4) / 60)
            alltime = str(f'{monthallhours}:{monthallminutes}')
            x2h = monthallhours - self.nh
            profitnoreward = sum(monthprofit) + (x2h * self.rate) + (monthallminutes * (self.rate / 60))
            profitreward = profitnoreward + monthreward
            ndflreward = profitreward * 0.13
            ndflnoreward = profitnoreward * 0.13
            profitnoreward -= ndflnoreward
            profitreward -= ndflreward
            self.ui.lcdNumber_9.display(alltime)
            self.ui.lcdNumber_14.display(ndflreward)
            self.ui.lcdNumber_12.display(ndflnoreward)
            self.ui.lcdNumber_13.display(profitnoreward)
            self.ui.lcdNumber_10.display(profitreward)
            self.ui.lcdNumber_4.display(self.nh)
            self.ui.lcdNumber_8.display(str(f'{x2h}:{monthallminutes}'))
            self.ui.lcdNumber_11.display(monthreward)
        else:
            monthreward = ((monthallhours * self.rate) * 0.4) + (((monthallminutes * self.rate) * 0.4) / 60)
            alltime = str(f'{monthallhours}:{monthallminutes}')
            profitnoreward = sum(monthprofit) + (monthallminutes * (self.rate / 60))
            profitreward = profitnoreward + monthreward
            ndflreward = profitreward * 0.13
            ndflnoreward = profitnoreward * 0.13
            profitnoreward -= ndflnoreward
            profitreward -= ndflreward
            self.ui.lcdNumber_9.display(alltime)
            self.ui.lcdNumber_14.display(ndflreward)
            self.ui.lcdNumber_12.display(ndflnoreward)
            self.ui.lcdNumber_13.display(profitnoreward)
            self.ui.lcdNumber_10.display(profitreward)
            self.ui.lcdNumber_4.display(self.nh)
            self.ui.lcdNumber_8.display(str(f'0:0'))
            self.ui.lcdNumber_11.display(monthreward)
            
        self.ui.spinBox.setProperty("value", self.nh)
#Выборка по месяцу на ЭС
    def givedate(self):
        for i in reversed(range(self.ui.gridLayout_3.count())): 
            self.ui.gridLayout_3.itemAt(i).widget().setParent(None)
        date = self.ui.dateEdit_4.date().toPyDate()
        year, month = date.year, date.month
        self.disp3(year, month)
#Запись нормы часов
    def savenh(self):
        nh = self.ui.spinBox.value()
        date = self.ui.dateEdit_4.date().toPyDate()
        year, month = date.year, date.month
        self.query.prepare("INSERT INTO norms (date, nh) VALUES (?, ?)")
        self.query.addBindValue(f'{month}.{year}')
        self.query.addBindValue(nh)
        self.query.exec()
        if self.query.lastError().text():
            msg = QMessageBox()
            msg.setText("Уже есть в базе!")
            msg.exec()
        else:
            msg = QMessageBox()
            msg.setText("Данные успешно внесены!")
            msg.exec()
            
#ввод шаблона
    def inserttemplate(self):
        drive = self.ui.timeEdit_5.time().toString('h:m')
        other = self.ui.timeEdit_6.time().toString('h:m')
        night = self.ui.timeEdit_7.time().toString('h:m')
        difference = self.ui.checkBox_2.isChecked()
        weekand = self.ui.checkBox_3.isChecked()
        route = self.ui.spinBox_2.value()
        release = self.ui.spinBox_3.value()
        query = QSqlQuery(self.db)
        query.prepare("SELECT * FROM template WHERE release = ? AND route = ? AND weekand = ?")
        query.addBindValue(release)
        query.addBindValue(route)
        query.addBindValue(weekand)
        query.exec()
        while query.next():
            if query.next() != None:
                msg = QMessageBox()
                msg.setText("Запись уже существует!")
                msg.exec()
                return False
        query.prepare("INSERT INTO template (release, route, drive, other, night, difference, weekand) VALUES (?, ?, ?, ?, ?, ?, ?)")
        query.addBindValue(release)
        query.addBindValue(route)
        query.addBindValue(drive)
        query.addBindValue(other)
        query.addBindValue(night)
        query.addBindValue(difference)
        query.addBindValue(weekand)
        query.exec()
        msg = QMessageBox()
        msg.setText("Записано успешно!")
        msg.exec()

        return
    
#Обработка нажатия динамических кнопок    
    def loadinfo(self, date, drive, other, night, idle, alltime, profit, difference, route, release, trs):
        #print(date)
        msg = QMessageBox()
        msg.setText(str(f'Дата: {date}\nРублевые: {drive}\nПрочее: {other}\nНочные: {night}\nПростой: {idle}\nВсего на работе: {alltime}\nДоход: {profit}\nРазрыв: {difference}\nМаршрут: {route}\nВыпуск: {release}\nТроллейбус: {trs}\n'))
        msg.exec()
#Загрузить шаблон
    def loadtemplate(self):
        weekand = self.ui.checkBox_4.isChecked()
        route = self.ui.spinBox_10.value()
        release = self.ui.spinBox_11.value()
        models2 = QSqlQuery(self.db)
        models2.prepare("SELECT * FROM template WHERE route = ? AND release = ? AND weekand = ?")
        models2.addBindValue(route)
        models2.addBindValue(release)
        models2.addBindValue(weekand)
        models2.exec()
        while models2.next():
            drive = QTime.fromString(models2.value(2), "h:m")
            other = QTime.fromString(models2.value(3), "h:m")
            night = QTime.fromString(models2.value(4), "h:m")
            difference = models2.value(5)
            trs = models2.value(7)
            self.ui.timeEdit.setTime(drive)
            self.ui.timeEdit_2.setTime(other)
            self.ui.timeEdit_3.setTime(night)
            self.ui.spinBox_8.setValue(route)
            self.ui.spinBox_9.setValue(release)
        return
#Обновить тариф
    def updaterate(self):
        rate = self.ui.doubleSpinBox.value()
        query = QSqlQuery(self.db)
        query.prepare("UPDATE sc SET rate = ?")
        query.addBindValue(rate)
        query.exec()
        if query.exec():
            msg = QMessageBox()
            msg.setText("Тариф изменён!")
            msg.exec()
        else:
            msg = QMessageBox()
            msg.setText("Сожалею, но что-то пошло не так!")
            msg.exec()
        self.loaddist()
#обновить машину
    def updatetrs(self):
        trs = self.ui.spinBox_7.value()
        query = QSqlQuery(self.db)
        query.prepare("UPDATE sc SET trs = ?")
        query.addBindValue(trs)
        query.exec()
        if query.exec():
            msg = QMessageBox()
            msg.setText("Машина переназначена!")
            msg.exec()
        else:
            msg = QMessageBox()
            msg.setText("Сожалею, но что-то пошло не так!")
            msg.exec()
        self.loaddist()
#обновить выпуск
    def updatemr(self):
        route = self.ui.spinBox_4.value()
        release = self.ui.spinBox_5.value()
        query1 = QSqlQuery(self.db)
        query1.prepare("UPDATE sc SET (route, release) = (?, ?)")
        query1.addBindValue(route)
        query1.addBindValue(release)
        query1.exec()
        if query1.exec():
            msg = QMessageBox()
            msg.setText("Выпуск переназначен!")
            msg.exec()
        else:
            msg = QMessageBox()
            msg.setText("Сожалею, но что-то пошло не так!")
            msg.exec()
        self.loaddist()
#загрузка тарифа и машины
    def loaddist(self):
        querytoprepare = QSqlQuery()
        querytoprepare.prepare("SELECT * FROM sc")
        querytoprepare.exec()
        while querytoprepare.next():
            self.rate = querytoprepare.value(0)
            self.trs = querytoprepare.value(3)
            route = querytoprepare.value(4)
            release = querytoprepare.value(5)
            
        self.ui.doubleSpinBox.setValue(self.rate)
        self.ui.spinBox_6.setValue(self.trs)
        self.ui.spinBox_7.setValue(self.trs)
        self.ui.spinBox_4.setValue(route)
        self.ui.spinBox_10.setValue(route)
        self.ui.spinBox_5.setValue(release)
        self.ui.spinBox_11.setValue(release)
        self.disp3(self.curdate.year, self.curdate.month)
        self.loadtemplate()
        self.disp1()
    
        
    
def main():
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
