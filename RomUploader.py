import sys
import os
import shutil
import time
import setting
from PySide6.QtWidgets import (
    QMainWindow, QApplication, QTableWidget, QLabel, QPushButton, QComboBox, QMessageBox
)


def make_dirs():
    make_rom_dir_on_quest2()
    make_end_dir()
    make_rom_dir()


def make_rom_dir_on_quest2():
    dirs = setting.ROM_directory[1:]
    command = 'adb shell mkdir /sdcard/MyROMs'
    os.system(command)
    command = 'adb shell mkdir /sdcard/MyCores'
    os.system(command)
    command = 'adb shell mkdir /sdcard/MyCores/Android'
    os.system(command)
    command = 'adb shell mkdir /sdcard/MyCores/Android/arm64-v8a'
    os.system(command)
    for each in dirs:
        command = 'adb shell mkdir /sdcard/MyROMs/{0}'.format(each)
        os.system(command)


def make_end_dir():
    if not os.path.isdir(old_path + '/End'):
        os.mkdir(os.getcwd() + '/End')


def make_rom_dir():
    all_rom_dirs = setting.ROM_directory[1:]
    os.chdir(os.getcwd() + '/End')
    for each in all_rom_dirs:
        if not os.path.isdir(os.getcwd() + '/' + each):
            os.mkdir(os.getcwd() + '/' + each)


def is_myroms_exist():
    return os.path.isdir(old_path + '/MyROMs')


def reset_up():
    w.table.clearContents()
    w.reset()


class MainWindow(QMainWindow):
    def __init__(self):
        self.combo_boxs = []
        self.current_dirs = []
        self.old_path = old_path
        self.rows = 0
        self.cols = 2
        self.table = None
        self.button_confirm = None
        self.button_refresh = None
        self.window_setting()
        self.init_widget()

    def window_setting(self):
        super(MainWindow, self).__init__()
        self.resize(1000, 600)
        self.setFixedSize(1000, 600)
        self.setWindowTitle("ROM Uploader")

    def init_widget(self):
        self.init_table()
        self.init_buttons()
        self.get_roms()

    def get_roms(self):
        if is_myroms_exist():
            os.chdir(old_path + '/MyROMs')
            self.replace_space()
            self.update_table()
        else:
            message_box = self.get_message_box('Warning',
                                               'MyROMs directory not exists',
                                               'Close')
            message_box.show()

    def init_table(self):
        self.table = QTableWidget(self.rows, self.cols, self)
        self.table.setGeometry(0, 0, 1000, 500)
        self.table.setColumnWidth(0, 500)
        self.table.setColumnWidth(1, 400)
        self.table.setHorizontalHeaderLabels(['ROM', 'Core'])

    def init_buttons(self):
        self.button_refresh = QPushButton(self)
        self.button_refresh.setGeometry(100, 530, 200, 50)
        self.button_refresh.setText("Refresh")
        self.button_confirm = QPushButton(self)
        self.button_confirm.setGeometry(700, 530, 200, 50)
        self.button_confirm.setText("Confirm")
        font = self.button_refresh.font()
        font.setPointSize(20)
        self.button_refresh.setFont(font)
        self.button_confirm.setFont(font)
        self.button_refresh.clicked.connect(reset_up)
        self.button_confirm.clicked.connect(self.check_rom_file)

    def replace_space(self):  # 取代檔案名稱內的空格使adb命令可以執行
        self.current_dirs = os.listdir()
        for each in self.current_dirs:
            after_replace = each.replace(' ', '_')
            os.rename(each, after_replace)
        self.current_dirs = os.listdir()

    def update_table(self):  # 更新表格
        self.rows = len(self.current_dirs)
        self.table.setRowCount(self.rows)
        for row in range(self.rows):
            self.set_table_content(row)

    def set_table_content(self, row):  # 設定表格內容
        self.table.setCellWidget(row, 0, QLabel(self.current_dirs[row]))
        combobox = QComboBox()
        combobox.wheelEvent = lambda e: e.ignore()
        combobox.addItems(setting.ROM_directory)
        self.table.setCellWidget(row, 1, combobox)
        self.combo_boxs.append(combobox)

    def check_rom_file(self):
        if len(self.combo_boxs) == 0:
            message_box = self.get_message_box('Warning',
                                               'No ROM needs to upload',
                                               'Close')
            message_box.show()
        else:
            for i in range(len(self.combo_boxs)):
                if self.combo_boxs[i].currentText() == 'None':
                    message_box = self.get_message_box('Warning', 'There are some ROMs which select the core not yet,  please confirm again.', 'Close')
                    message_box.show()
                    return

            self.copy_file()
            message_box = self.get_message_box('Completed', 'All ROMs have moved to quest 2.', 'Close')
            message_box.show()
            reply = message_box.exec()
            if reply == QMessageBox.AcceptRole:
                reset_up()

    def copy_file(self):
        os.chdir(old_path + '/MyROMs')
        for i in range(len(self.combo_boxs)):
            src = self.old_path + '/MyROMs/' + self.current_dirs[i]
            dst = self.old_path + '/End/' + self.combo_boxs[i].currentText() + '/' + self.current_dirs[i]
            shutil.copyfile(src, dst)
            self.push_file_to_quest2(i)
            os.unlink(src)

    def push_file_to_quest2(self, index):
        command = 'adb push {0} /sdcard/{1} '.format(self.current_dirs[index],
                                                 'MyROMs/' + self.combo_boxs[index].currentText() + '/')
        os.system(command)

    def get_message_box(self, title, message, button_text):
        message_box = QMessageBox(self)
        message_box.setWindowTitle(title)
        message_box.setText(message)
        message_box.addButton(button_text, QMessageBox.AcceptRole)
        message_box.setStyleSheet("QLabel{min-width:500 px; font-size: 24px;} QPushButton{ width:500px; font-size: 18px; }")
        return message_box

    def reset(self):
        self.combo_boxs = []
        self.get_roms()


old_path = os.getcwd()
make_dirs()
app = QApplication([])
w = MainWindow()
w.show()
sys.exit(app.exec())
