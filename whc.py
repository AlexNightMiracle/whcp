import sys
from datetime import timedelta, datetime
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel, QSqlError
from PyQt5.QtGui import *
import os
from pyform1 import *
import string
import calendar
import sqlite3
import math
import time
from functools import partial
import whcpush
from qt_material import apply_stylesheet

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()

        self.qbt = [0] * 7
        self.rew = [0, 0, 0, 0]
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.curdate = datetime.now()
        #self.curdate = QDate.currentDate()
#блок открытия БД
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('dbwt.db')
        self.db.open()
        self.query = QSqlQuery()
        self.query.exec("CREATE TABLE IF NOT EXISTS wt (    date    DATE   PRIMARY KEY,    time1   TIME,    time2   TIME,    time3   TIME,    time4   TIME,    time5   TIME,    profit  DOUBLE,    difference BOOLEAN, route INT, release INT, trs INT, shift VARCHAR, stat INT);")
        self.query.exec("CREATE TABLE IF NOT EXISTS norms (date DATE PRIMARY KEY,   nh   INT)")
        self.query.exec("CREATE TABLE IF NOT EXISTS template (    release  INT,    route      INT,    drive      TIME,    other      TIME,    night      TIME,    difference BOOLEAN,    weekand    BOOLEAN);")
        self.query.exec("CREATE TABLE IF NOT EXISTS sc (    rate  DOUBLE,    night DOUBLE,    idle  DOUBLE,    trs   INT, route  INT, release  INT, id INT PRIMARY KEY, shift INT);")
        self.query.exec("CREATE TABLE IF NOT EXISTS reward (    rew1name VARCHAR,    rew1rate INT,    rew2name VARCHAR,    rew2rate INT,    rew3name VARCHAR,    rew3rate INT,    rew4name VARCHAR,    rew4rate INT, id       INT     PRIMARY KEY);")
        self.query.prepare("INSERT INTO sc (rate, trs, route, release, id, shift) VALUES (155.64, 1000, 1, 1, 1, 0)")
        self.query.exec()
        self.query.prepare("INSERT INTO reward (rew1name, rew1rate, rew2name, rew2rate, rew3name, rew3rate, rew4name, rew4rate, id) VALUES ('регулярность', 20, 'обслуживание', 20, 'вредность', 12, 'классность', 0, 1);")
        self.query.exec()
        self.query.prepare("DELETE FROM sc WHERE id != 1")
        self.query.exec()
        self.query.prepare("DELETE FROM reward WHERE id != 1")
        self.query.exec()

        self.popup = whcpush.PopupWindowClass()
#        
        self.ui.comboBox_3.addItem('Первая')
        self.ui.comboBox_3.addItem('Средняя')
        self.ui.comboBox_3.addItem('Разрывная')
        self.ui.comboBox_3.addItem('Вторая')
        self.ui.comboBox_3.addItem('Развозка')
        self.ui.comboBox_2.addItem('Первая')
        self.ui.comboBox_2.addItem('Средняя')
        self.ui.comboBox_2.addItem('Разрывная')
        self.ui.comboBox_2.addItem('Вторая')
        self.ui.comboBox_2.addItem('Развозка')
        self.ui.comboBox_4.addItem('Первая')
        self.ui.comboBox_4.addItem('Средняя')
        self.ui.comboBox_4.addItem('Разрывная')
        self.ui.comboBox_4.addItem('Вторая')
        self.ui.comboBox_4.addItem('Развозка')
        self.ui.comboBox.addItem('Первая')
        self.ui.comboBox.addItem('Средняя')
        self.ui.comboBox.addItem('Разрывная')
        self.ui.comboBox.addItem('Вторая')
        self.ui.comboBox.addItem('Развозка')
        
        self.ui.comboBox_5.addItem('Рабочий день')
        self.ui.comboBox_5.addItem('Выходной')
        self.ui.comboBox_5.addItem('Больничный')
        self.ui.comboBox_5.addItem('Отпуск')
        self.ui.comboBox_5.addItem('Прогул')

        self.ui.comboBox_5.currentIndexChanged.connect(self.cb5con)
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
        self.ui.dateEdit.setDate(QDate.currentDate())
        self.ui.dateEdit_4.setDate(QDate.currentDate())
#блок вызова событий нажатия внопок ЭВД
        self.ui.pushButton.clicked.connect(self.disp2)
        self.ui.pushButton_2.clicked.connect(self.savenh)
        self.ui.pushButton_3.clicked.connect(self.loadtemplate)
        self.ui.pushButton_4.clicked.connect(self.inserttemplate)
        self.ui.pushButton_5.clicked.connect(self.updatemr)
        self.ui.pushButton_6.clicked.connect(self.updatetrs)
        self.ui.pushButton_7.clicked.connect(self.updaterate)
        self.ui.pushButton_8.clicked.connect(self.updaterew)
#блок вызова событий изменения времени на ЭВД
        self.ui.timeEdit.timeChanged.connect(self.disp1)
        self.ui.timeEdit_2.timeChanged.connect(self.disp1)
        self.ui.timeEdit_3.timeChanged.connect(self.disp1)
        self.ui.timeEdit_4.timeChanged.connect(self.disp1)
        self.ui.dateEdit.dateChanged.connect(self.disp1)
        self.ui.comboBox_2.currentIndexChanged.connect(self.disp1)
#блок обработки события изменения времени ЭВД

    def cb5con(self):
        cb5index = self.ui.comboBox_5.currentIndex()

        if cb5index > 0:
            self.ui.label.hide()
            self.ui.timeEdit.hide()
            self.ui.label_2.hide()
            self.ui.timeEdit_2.hide()
            self.ui.label_3.hide()
            self.ui.timeEdit_3.hide()
            self.ui.label_4.hide()
            self.ui.timeEdit_4.hide()
            self.ui.label_29.hide()
            self.ui.spinBox_8.hide()
            self.ui.label_30.hide()
            self.ui.spinBox_9.hide()
            self.ui.label_14.hide()
            self.ui.comboBox_2.hide()
            self.ui.label_27.hide()
            self.ui.spinBox_6.hide()
            self.ui.lcdNumber.display('--')
            self.ui.lcdNumber_2.display('--')
        else:
            self.ui.label.show()
            self.ui.timeEdit.show()
            self.ui.label_2.show()
            self.ui.timeEdit_2.show()
            self.ui.label_3.show()
            self.ui.timeEdit_3.show()
            self.ui.label_4.show()
            self.ui.timeEdit_4.show()
            self.ui.label_29.show()
            self.ui.spinBox_8.show()
            self.ui.label_30.show()
            self.ui.spinBox_9.show()
            self.ui.label_14.show()
            self.ui.comboBox_2.show()
            self.ui.label_27.show()
            self.ui.spinBox_6.show()
            self.ui.lcdNumber_2.display(self.profit)
            self.ui.lcdNumber.display("{0}:{1}".format(self.th5, self.tm5))
            return

    def disp1(self):
        if self.ui.comboBox_5.currentIndex() == 0:
            pay1, pay2, pay3 = self.rate, (self.rate / 2.5), (self.rate / 1.5)
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
        
            if self.ui.comboBox_2.currentIndex() != 2:
                self.profit = paytohours + paytother
            else:
                self.profit = (paytohours + (paytohours * 0.3)) + paytother
            self.ui.lcdNumber_2.display(self.profit)
            self.ui.lcdNumber.display("{0}:{1}".format(self.th5, self.tm5))
            
        return
#блок записи данных в БД с ЭВД
    def disp2(self):
        cb5index = self.ui.comboBox_5.currentIndex()
        date = self.ui.dateEdit.date().toString('d.M.yyyy')
        if cb5index == 0:
            route = self.ui.spinBox_8.value()
            release = self.ui.spinBox_9.value()
            trs = self.ui.spinBox_6.value()
            shift = self.ui.comboBox_2.currentText()
            self.query.prepare("INSERT INTO wt (date, time1, time2, time3, time4, time5, profit, route, release, trs, shift, stat) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
            self.query.addBindValue(date)
            self.query.addBindValue(f'{self.th1}:{self.tm1}')
            self.query.addBindValue(f'{self.th2}:{self.tm2}')
            self.query.addBindValue(f'{self.th3}:{self.tm3}')
            self.query.addBindValue(f'{self.th4}:{self.tm4}')
            self.query.addBindValue(f'{self.th5}:{self.tm5}')
            self.query.addBindValue(self.profit)
            self.query.addBindValue(route)
            self.query.addBindValue(release)
            self.query.addBindValue(trs)
            self.query.addBindValue(shift)
            self.query.addBindValue(cb5index)
            self.query.exec()

            if self.query.lastError().text():
                self.popup.setPopupText('Ячейка \n перезаписана')
                self.popup.show()
                self.query.prepare("UPDATE wt SET (time1, time2, time3, time4, time5, profit, route, release, trs, shift, stat) = (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) WHERE date = ?")
                self.query.addBindValue(f'{self.th1}:{self.tm1}')
                self.query.addBindValue(f'{self.th2}:{self.tm2}')
                self.query.addBindValue(f'{self.th3}:{self.tm3}')
                self.query.addBindValue(f'{self.th4}:{self.tm4}')
                self.query.addBindValue(f'{self.th5}:{self.tm5}')
                self.query.addBindValue(self.profit)
                self.query.addBindValue(route)
                self.query.addBindValue(release)
                self.query.addBindValue(trs)
                self.query.addBindValue(shift)
                self.query.addBindValue(cb5index)
                self.query.addBindValue(date)
                self.query.exec()
                self.loaddist()
            else:
                self.popup.setPopupText('Данные \n Успешно внесены')
                self.popup.show()
                self.loaddist()
        else:
            self.query.prepare("INSERT INTO wt (date, stat) VALUES (?, ?)")
            self.query.addBindValue(f'{date}')
            self.query.addBindValue(cb5index)
            self.query.exec()
            if self.query.lastError().text():
                self.query.prepare("DELETE FROM wt WHERE date = ?")
                self.query.addBindValue(f'{date}')
                self.query.exec()
                self.query.prepare("INSERT INTO wt (date, stat) VALUES (?, ?)")
                self.query.addBindValue(f'{date}')
                self.query.addBindValue(cb5index)
                self.query.exec()
                self.popup.setPopupText('Ячейка \n перезаписана')
                self.popup.show()
                self.loaddist()
            else:
                self.popup.setPopupText('Данные \n Успешно внесены')
                self.popup.show()
                self.loaddist()
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
                    strdateday = str(f'{day}.{month}.{year}')
                    dateday = QtCore.QDate.fromString(strdateday, 'd.M.yyyy')
                    dateday = QtCore.QDate.toString(dateday, 'd.M.yyyy')
                    self.qbt[x] = str(f'{dateday}\nПустая запись\n')
                    self.qbt[x] = QPushButton(self.qbt[x])
                    self.ui.gridLayout_3.addWidget(self.qbt[x], x, y)
                    self.qbt[x].setProperty('class', 'button0')
                    self.qbt[x].clicked.connect(partial(self.printd, dateday))
                    self.s2 = QSqlQuery(self.db)
                    self.s2.prepare("SELECT * FROM wt WHERE date = ?")
                    self.s2.addBindValue(dateday)
                    self.s2.exec()
                    
                    while self.s2.next():
                        stat = self.s2.value(12)
                        if stat == 1:
                            stattemp = 1
                            self.qbt[x] = str(f'{self.s2.value(0)}\nВыходной\n')
                            self.qbt[x] = QPushButton(self.qbt[x])
                            self.ui.gridLayout_3.addWidget(self.qbt[x], x, y)
                            self.qbt[x].setProperty('class', 'button1')
                        if stat == 2:
                            stattemp = 1
                            self.qbt[x] = str(f'{self.s2.value(0)}\nБольничный\n')
                            self.qbt[x] = QPushButton(self.qbt[x])
                            self.ui.gridLayout_3.addWidget(self.qbt[x], x, y)
                            self.qbt[x].setProperty('class', 'button2')
                        if stat == 3:
                            stattemp = 1
                            self.qbt[x] = str(f'{self.s2.value(0)}\nОтпуск\n')
                            self.qbt[x] = QPushButton(self.qbt[x])
                            self.ui.gridLayout_3.addWidget(self.qbt[x], x, y)
                            self.qbt[x].setProperty('class', 'button3')
                        if stat == 4:
                            stattemp = 1
                            self.qbt[x] = str(f'{self.s2.value(0)}\nПрогул\n')
                            self.qbt[x] = QPushButton(self.qbt[x])
                            self.ui.gridLayout_3.addWidget(self.qbt[x], x, y)
                            self.qbt[x].setProperty('class', 'button4')
                        if stat == 0:
                            stattemp = 0
                            self.qbt[x] = str(f'{self.s2.value(0)}\n{self.s2.value(11)} смена: {self.s2.value(5)} ч.\nRUB: {round(self.s2.value(6), 2)}')
                            dateof[x] = self.s2.value(0)
                            self.qbt[x] = QPushButton(self.qbt[x])
                            self.ui.gridLayout_3.addWidget(self.qbt[x], x, y)
                            time = QtCore.QTime.fromString(self.s2.value(5), 'h:m')
                            time1 = '8:0'
                            time2 = QTime.fromString(time1, 'h:m')
                            if time < time2:
                                self.qbt[x].setProperty('class', 'button00')
                            else:
                                self.qbt[x].setProperty('class', 'button01')
                    
                            if type(self.s2.value(6)) == float:
                                monthprofit[x] += self.s2.value(6)
                                toQtime1[x] = QTime.fromString(self.s2.value(5), "h:m")
                                if QTime.isValid(toQtime1[x]) == True and QTime.isNull(toQtime1[x]) == False:
                                    toPytime1 = toQtime1[x].toPyTime()
                                    monthallhours[x] += toPytime1.hour
                                    monthallminutes[x] += toPytime1.minute
                        self.qbt[x].clicked.connect(partial(self.loadinfo, stattemp, self.s2.value(0), self.s2.value(1), self.s2.value(2), self.s2.value(3), self.s2.value(4), self.s2.value(5), self.s2.value(6), self.s2.value(8), self.s2.value(9), self.s2.value(10), self.s2.value(11), self.s2.value(12)))
                                
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
            reward = (self.rew[0] + self.rew[1] + self.rew[2] + self.rew[3]) / 100
            monthreward = ((monthallhours * self.rate) * reward) + (((monthallminutes * self.rate) * reward) / 60)
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
            reward = (self.rew[0] + self.rew[1] + self.rew[2] + self.rew[3]) / 100
            monthreward = ((monthallhours * self.rate) * reward) + (((monthallminutes * self.rate) * reward) / 60)
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
        #date = self.ui.dateEdit_4.date().toString('MM.yyyy')
        #year, month = self.ui.dateEdit_4.date().toString('yyyy'), self.ui.dateEdit_4.date().toString('MM')
        #year, month = year.toPyDate(), month.toPyDate()
        #print(year, month)
        date = self.ui.dateEdit_4.date().toPyDate()
        year, month = date.year, date.month
        #print(year, month)
        #year, month = date('yyyy'), date('MM')
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
            self.query.prepare("UPDATE norms SET nh = ? WHERE date = ?")
            self.query.addBindValue(nh)
            self.query.addBindValue(f'{month}.{year}')
            self.query.exec()
            self.popup.setPopupText('Норма часов \n перезаписана')
            self.popup.show()
            self.loaddist()
        else:
            self.popup.setPopupText('Норма часов \n записана')
            self.popup.show()
            self.loaddist()
            
#ввод шаблона
    def inserttemplate(self):
        drive = self.ui.timeEdit_5.time().toString('h:m')
        other = self.ui.timeEdit_6.time().toString('h:m')
        night = self.ui.timeEdit_7.time().toString('h:m')
        difference = self.ui.comboBox_4.currentIndex()
        weekand = self.ui.checkBox_3.isChecked()
        route = self.ui.spinBox_2.value()
        release = self.ui.spinBox_3.value()
        query = QSqlQuery(self.db)
        query.prepare("SELECT * FROM template WHERE release = ? AND route = ? AND weekand = ? AND difference = ?")
        query.addBindValue(release)
        query.addBindValue(route)
        query.addBindValue(weekand)
        query.addBindValue(difference)
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

        return
    
#Обработка нажатия динамических кнопок    
    def loadinfo(self, stattemp, date, drive, other, night, idle, alltime, profit, route, release, trs, shift, stat):
        #print(date)
        msg = QMessageBox()
        if stat == 0:
            msg.setText(str(f'Дата: {date}\nРублевые: {drive}\nПрочее: {other}\nНочные: {night}\nПростой: {idle}\nВсего на работе: {alltime}\nДоход: {profit}\nМаршрут: {route}\nВыпуск: {release}\nТроллейбус: {trs}\n'))
        if stat == 1:
            msg.setText(str(f'Дата: {date}\nСтатус: Выходной'))
        if stat == 2:
            msg.setText(str(f'Дата: {date}\nСтатус: Больничный'))
        if stat == 3:
            msg.setText(str(f'Дата: {date}\nСтатус: Отпуск'))
        if stat == 4:
            msg.setText(str(f'Дата: {date}\nСтатус: Прогул'))
        connectButton = msg.addButton('Изменить', QMessageBox.ActionRole);
        abortButton = msg.addButton(QMessageBox.Close);
        msg.exec()
        if (msg.clickedButton() == connectButton):
            msg1 = QMessageBox()
            msg1.setText(str(f'Выберите тип ячейки дня:'))
            connectButton1 = msg1.addButton('Рабочий день', QMessageBox.ActionRole);
            connectButton2 = msg1.addButton('Выходной', QMessageBox.ActionRole);
            connectButton3 = msg1.addButton('Больничный', QMessageBox.ActionRole);
            connectButton4 = msg1.addButton('Отпуск', QMessageBox.ActionRole);
            connectButton5 = msg1.addButton('Прогул', QMessageBox.ActionRole);
            abortButton1 = msg1.addButton(QMessageBox.Close);
            msg1.exec()
            query = QSqlQuery(self.db)
            if (msg1.clickedButton() == connectButton1):
                if stattemp == 1:
                    self.ui.tabWidget.setCurrentIndex(0)
                    self.ui.dateEdit.setDate(QDate.fromString(date, 'd.M.yyyy'))
                    self.loadtemplate()
                if stattemp == 0:
                    self.ui.tabWidget.setCurrentIndex(0)
                    self.ui.dateEdit.setDate(QDate.fromString(date, 'd.M.yyyy'))
                    self.ui.timeEdit.setTime(QTime.fromString(drive, "h:m"))
                    self.ui.timeEdit_2.setTime(QTime.fromString(other, "h:m"))
                    self.ui.timeEdit_3.setTime(QTime.fromString(night, "h:m"))
                    self.ui.timeEdit_4.setTime(QTime.fromString(idle, "h:m"))
                    self.ui.spinBox_8.setValue(route)
                    self.ui.spinBox_9.setValue(release)
                    self.ui.spinBox_6.setValue(trs)
                    self.ui.comboBox_5.setCurrentIndex(0)
                    self.ui.comboBox_2.setCurrentText(shift)
            if (msg1.clickedButton() == connectButton2):
                self.ui.tabWidget.setCurrentIndex(0)
                self.ui.dateEdit.setDate(QDate.fromString(date, 'd.M.yyyy'))
                self.ui.comboBox_5.setCurrentIndex(1)
            if (msg1.clickedButton() == connectButton3):
                self.ui.tabWidget.setCurrentIndex(0)
                self.ui.dateEdit.setDate(QDate.fromString(date, 'd.M.yyyy'))
                self.ui.comboBox_5.setCurrentIndex(2)
            if (msg1.clickedButton() == connectButton4):
                self.ui.tabWidget.setCurrentIndex(0)
                self.ui.dateEdit.setDate(QDate.fromString(date, 'd.M.yyyy'))
                self.ui.comboBox_5.setCurrentIndex(3)
            if (msg1.clickedButton() == connectButton5):
                self.ui.tabWidget.setCurrentIndex(0)
                self.ui.dateEdit.setDate(QDate.fromString(date, 'd.M.yyyy'))
                self.ui.comboBox_5.setCurrentIndex(4)

    def printd(self, date):
        #msg = QMessageBox()
        #msg.setText('lol')
        #msg.exec()
        date = QtCore.QDate.fromString(date, 'd.M.yyyy')
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.dateEdit.setDate(date)
        #print(date)
        
#Загрузить шаблон
    def loadtemplate(self):
        weekand = self.ui.checkBox_4.isChecked()
        route = self.ui.spinBox_10.value()
        release = self.ui.spinBox_11.value()
        shift = self.ui.comboBox_3.currentIndex()
        models2 = QSqlQuery(self.db)
        models2.prepare("SELECT * FROM template WHERE route = ? AND release = ? AND weekand = ? AND difference = ?")
        models2.addBindValue(route)
        models2.addBindValue(release)
        models2.addBindValue(weekand)
        models2.addBindValue(shift)
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
            self.ui.comboBox_2.setCurrentIndex(difference)
        return
#Обновить тариф
    def updaterate(self):
        rate = self.ui.doubleSpinBox.value()
        query = QSqlQuery(self.db)
        query.prepare("UPDATE sc SET rate = ?")
        query.addBindValue(rate)
        query.exec()
        if query.exec():
            self.popup.setPopupText('Тариф \n перезаписан')
            self.popup.show()
        else:
            self.popup.setPopupText('Ошибка \n записи')
            self.popup.show()
        self.loaddist()

# Обновить премии
    def updaterew(self):
        urew1name = self.ui.lineEdit.text()
        urew1rate = self.ui.spinBox_12.value()
        urew2name = self.ui.lineEdit_2.text()
        urew2rate = self.ui.spinBox_13.value()
        urew3name = self.ui.lineEdit_3.text()
        urew3rate = self.ui.spinBox_14.value()
        urew4name = self.ui.lineEdit_4.text()
        urew4rate = self.ui.spinBox_15.value()
        query = QSqlQuery(self.db)
        query.prepare("UPDATE reward SET (rew1name, rew1rate, rew2name, rew2rate, rew3name, rew3rate, rew4name, rew4rate) = (?, ?, ?, ?, ?, ?, ?, ?)")
        query.addBindValue(urew1name)
        query.addBindValue(urew1rate)
        query.addBindValue(urew2name)
        query.addBindValue(urew2rate)
        query.addBindValue(urew3name)
        query.addBindValue(urew3rate)
        query.addBindValue(urew4name)
        query.addBindValue(urew4rate)
        query.exec()
        if query.exec():
            self.popup.setPopupText('Данные премирования \n перезаписаны')
            self.popup.show()
        else:
            self.popup.setPopupText('Ошибка \n записи')
            self.popup.show()
        self.loaddist()

#обновить машину
    def updatetrs(self):
        trs = self.ui.spinBox_7.value()
        query = QSqlQuery(self.db)
        query.prepare("UPDATE sc SET trs = ?")
        query.addBindValue(trs)
        query.exec()
        if query.exec():
            self.popup.setPopupText('Машина \n переназначена')
            self.popup.show()
        else:
            self.popup.setPopupText('Ошибка \n записи')
            self.popup.show()
        self.loaddist()
#обновить выпуск
    def updatemr(self):
        route = self.ui.spinBox_4.value()
        release = self.ui.spinBox_5.value()
        shift = self.ui.comboBox.currentIndex()
        query1 = QSqlQuery(self.db)
        query1.prepare("UPDATE sc SET (route, release, shift) = (?, ?, ?)")
        query1.addBindValue(route)
        query1.addBindValue(release)
        query1.addBindValue(shift)
        query1.exec()
        if query1.exec():
            self.popup.setPopupText('Выпуск \n перезаписан')
            self.popup.show()
        else:
            self.popup.setPopupText('Ошибка \n записи')
            self.popup.show()
        self.loaddist()
#загрузка тарифа и машины
    def loaddist(self):
        querytoprepare = QSqlQuery()
        querytoprepare2 = QSqlQuery()
        querytoprepare.prepare("SELECT * FROM sc")
        querytoprepare.exec()
        while querytoprepare.next():
            self.rate = querytoprepare.value(0)
            self.trs = querytoprepare.value(3)
            route = querytoprepare.value(4)
            release = querytoprepare.value(5)
            shift = querytoprepare.value(7)

        querytoprepare2.prepare("SELECT * FROM reward")
        querytoprepare2.exec()
        while querytoprepare2.next():
            self.rew[0] = querytoprepare2.value(1)
            self.rew[1] = querytoprepare2.value(3)
            self.rew[2] = querytoprepare2.value(5)
            self.rew[3] = querytoprepare2.value(7)
            rew1name = querytoprepare2.value(0)
            rew2name = querytoprepare2.value(2)
            rew3name = querytoprepare2.value(4)
            rew4name = querytoprepare2.value(6)

        
        self.ui.doubleSpinBox.setValue(self.rate)
        self.ui.spinBox_6.setValue(self.trs)
        self.ui.spinBox_7.setValue(self.trs)
        self.ui.spinBox_4.setValue(route)
        self.ui.spinBox_10.setValue(route)
        self.ui.spinBox_5.setValue(release)
        self.ui.spinBox_11.setValue(release)
        self.disp3(self.curdate.year, self.curdate.month)
        self.ui.comboBox_2.setCurrentIndex(shift)
        self.ui.comboBox.setCurrentIndex(shift)
        self.ui.comboBox_3.setCurrentIndex(shift)

        self.ui.spinBox_12.setValue(self.rew[0])
        self.ui.spinBox_13.setValue(self.rew[1])
        self.ui.spinBox_14.setValue(self.rew[2])
        self.ui.spinBox_15.setValue(self.rew[3])
        self.ui.lineEdit.setText(rew1name)
        self.ui.lineEdit_2.setText(rew2name)
        self.ui.lineEdit_3.setText(rew3name)
        self.ui.lineEdit_4.setText(rew4name)
        #now = QDate.currentDate()
        #self.disp3(now.toString('yyyy'), now.toString('M'))
        #print(self.curdate.year, self.curdate.month)
        self.loadtemplate()
        self.disp1()
    
def main():
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    apply_stylesheet(app, theme="dark_teal.xml")
    stylesheet = app.styleSheet()
    with open('custom_buttons.css') as file: app.setStyleSheet(stylesheet + file.read().format(**os.environ))
    application.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()