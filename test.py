import sqlite3
import sys

from datetime import datetime as date


from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem, QListWidget, QListWidgetItem

#from PyQt5.Qt import QStandardItemModel, QStandardItem
from PyQt5.QtGui import QFont


class Main(QMainWindow):
    def __init__(self):  ## initialization
        super().__init__()
        uic.loadUi("untitledproject.ui", self)
        self.setWindowTitle("Project")
        self.con = sqlite3.connect("prote_db.sqlite")
        self.gcur = self.con.cursor()
 #       print([i for i in self.cur.execute("SELECT title FROM notes")])
        self.font = QFont(None, 19)
        self.rfont = QFont(None, 17)
        self.title_edit.setFont(self.font)
        self.notes_display.setFont(self.font)
        self.used_user = 1
        self.used_dser = 0
        self.cur_row = None
        self.cur_itemg()
        self.first = True
        self.tst = None


        self.notes = self.gcur.execute('SELECT * from notes').fetchall()

        if self.notes == []:
            self.create_note(False)
        self.note_list_update()
        self.update_screen()

        #self.gcur.close()
        #self.ucur.execute('''UPDATE notes SET last_note_if = 1 WHERE id = 3''')
        #self.con.commit()
        #self.ucur.close()
        #self.gcur = self.con.cursor()

        print(self.notes)



        self.notes_display.currentItemChanged.connect(lambda c: self.signal_interceptor_change_note(c))
        self.notes_display.itemClicked.connect(lambda x: self.signal_interceptor_change_note(x))
        self.title_edit.textChanged.connect(self.load_title_change)
        self.note_text.textChanged.connect(self.load_text_change)
        self.NewButton.clicked.connect(lambda: self.create_note(True))
        self.DeleteButton.clicked.connect(self.delete_note)
        self.SaveButton.clicked.connect(self.save)

    def create_note(self, notes_present=True):
        if notes_present:
            #self.cur.execute()

            note_type = "text"
            if note_type == 'text':

                self.load_text_change()
                self.load_text()

                self.gcur.close()
                self.ucur = self.con.cursor()
                self.ucur.execute('''UPDATE notes SET last_note_if = 0 WHERE last_note_if = 1''')
                self.con.commit()
                self.ucur.close()
                self.gcur = self.con.cursor()

                type_id = self.gcur.execute('''SELECT id from types
                WHERE title = ?''', (note_type,)).fetchone()
                max_id = self.gcur.execute('SELECT MAX(id) from notes').fetchone()[0]
                self.gcur.execute(
                    "INSERT INTO notes(id, title, type, last_change, contents, last_note_if) VALUES " +
                    "(?, 'Untitled', ?, ?, '', 1)",
                    (max_id + 1, type_id[0], date.now().strftime("%d %B %Y, %H:%M")))
                self.con.commit()


                self.note_list_update()
                self.update_screen()
        else:
            self.gcur.close()
            self.ucur = self.con.cursor()
            self.ucur.execute('''UPDATE notes SET last_note_if = 0 WHERE last_note_if = 1''')
            self.con.commit()
            self.ucur.close()
            self.gcur = self.con.cursor()

            self.gcur.execute(
                "INSERT INTO notes(id, title, type, last_change, contents, last_note_if) VALUES " +
                "(?, 'Untitled', ?, ?, '', 1)",
                (0, 1, date.now().strftime("%d %B %Y, %H:%M")))
            self.con.commit()
            self.note_list_update()
            self.update_screen()

    def note_list_update(self):
        self.notes_display.clear()
        self.notes = self.gcur.execute("SELECT * FROM notes").fetchall()
        for i in self.notes:
            #print(str(i[0]), str(i[1]))
            # Creates a QListWidgetItem
            item_to_add = QListWidgetItem()
            item_to_add.setText(str(i[1]))
            item_to_add.setData(QtCore.Qt.UserRole, str(i[0]))

            # Add the new rule to the QListWidget
            self.notes_display.addItem(item_to_add)
            #self.notes_display.addTopLevelItem(QTreeWidgetItem([str(i[0]), str(i[1])]))

    def signal_interceptor_change_note(self, current_item, row=-2):
            if current_item != None or row != -2:
                #print(self.notes_display.headerItem())
                #print(current_item)
                if row != -2:
                    current_item = self.notes_display.item(row)
                    if current_item == None:
                        current_item = self.notes_display.item(row - 1)
                self.item_ge(int(self.notes_display.row(current_item)))
                self.cur_item = self.gcur.execute('''SELECT * from notes
                WHERE id = ?''', (current_item.data(QtCore.Qt.UserRole),)).fetchone()

                self.gcur.close()
                self.ucur = self.con.cursor()
                self.ucur.execute('''UPDATE notes SET last_note_if = 0, title = ?, contents = ?
                WHERE last_note_if = 1''',
                (self.title_edit.toPlainText(), self.note_text.toPlainText(),))
                self.con.commit()
                self.ucur.execute('''UPDATE notes SET last_note_if = 1
                WHERE id = ?''', (current_item.data(QtCore.Qt.UserRole),))
                self.con.commit()
                self.ucur.close()
                self.gcur = self.con.cursor()

                print(self.cur_item[0:])
                print(current_item.data(QtCore.Qt.UserRole))
                self.change_note(current_item.data(QtCore.Qt.UserRole))

    def change_note(self, new_note_id):
        self.date_label.setText(self.cur_item[3])
        self.used_user = 0
        self.title_edit.setText(self.cur_item[1])
        self.note_text.clear()
        self.note_text.setPlainText(self.cur_item[4])
        self.used_user = 1
        self.note_list_update()

    def update_screen(self):

        note = self.gcur.execute('''SELECT * from notes
    WHERE last_note_if = 1''',).fetchone()
        print(note)
        self.used_user = 0
        self.title_edit.setText(note[1])
        self.note_text.setPlainText(note[4])
        self.date_label.setText(note[3])
        self.used_user = 1

    def save(self):
        self.load_text()
        self.load_text_change()
        #print(self.cur_item)
        #self.notes_display.editItem(self.notes_display.itemAt(self.cur_item[0], 0), self.cur_item[0]).setText('qeqwr')
        #self.notes_display.currentItem().setSelected(False)
        #self.notes_display.topLevelItem(0).setSelected(True)

    def item_ge(self, row):
        self.cur_row = row

    def delete_note(self):
        #self.notes_display.setCurrentRow(1)
        if self.cur_row != None:
            if len(self.notes) != 1:

                self.gcur.close()
                self.dcur = self.con.cursor()
                self.dcur.execute('''DELETE FROM notes WHERE last_note_if = 1''')
                self.con.commit()
                self.dcur.close()
                self.gcur = self.con.cursor()

                #print(self.notes_display.item(self.cur_row))
                if self.cur_row == 0:
                    print("FIRST")
                #print(self.next)
                  #  self.next = self.notes_display.item(self.cur_row + 1)

                #self.used_dser = 0
                self.note_list_update()
                self.signal_interceptor_change_note(self.notes_display.item(self.cur_row), int(self.cur_row))

                self.used_dser = 1
            else:
                self.gcur.close()
                self.dcur = self.con.cursor()
                self.dcur.execute('''DELETE FROM notes WHERE last_note_if = 1''')
                self.con.commit()
                self.dcur.close()
                self.gcur = self.con.cursor()

                self.create_note(False)


    def cur_itemg(self):
        self.cur_item = self.gcur.execute('''SELECT * from notes WHERE last_note_if = 1''').fetchone()

    def load_text_change(self):
        if self.used_user:
            self.gcur.close()
            self.ucur = self.con.cursor()
            self.ucur.execute('''UPDATE notes SET last_change = ? WHERE last_note_if = 1''',
                              (date.now().strftime("%d %B %Y, %H:%M"),))
            self.date_label.setText(date.now().strftime("%d %B %Y, %H:%M"))
            self.con.commit()
            self.ucur.close()
            self.gcur = self.con.cursor()

    def load_text(self):
            self.gcur.close()
            self.ucur = self.con.cursor()
            self.ucur.execute('''UPDATE notes SET contents = ? WHERE last_note_if = 1''',
                              (self.note_text.toPlainText(),))
            self.con.commit()
            self.ucur.close()
            self.gcur = self.con.cursor()
    def load_title_change(self):
        if self.used_user:
            self.gcur.close()
            self.ucur = self.con.cursor()
            self.ucur.execute('''UPDATE notes SET title = ?  WHERE last_note_if = 1''',
                              (self.title_edit.toPlainText(),))
            self.con.commit()
            self.ucur.close()
            self.gcur = self.con.cursor()
            self.note_list_update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec_())

#self.notes_display.currentItem().setSelected(False)
#self.notes_display.topLevelItem(0).setSelected(True)

