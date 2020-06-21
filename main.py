from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from re import split
import json
import win32api
import sys
import os
from datetime import date, datetime
import time
from my_math import *
from processor_class import *
from text_widget import *
from rejestr_class import *

let = ('A', 'B', 'C', 'D')
FUNCTIONS = ('ADD', 'SUB', 'MOV')
PRZERW = ('INT21', 'INT16', 'INT15', 'INT10')
STOS_FUNC = ('PUSH', 'POP')
STOS_REJ = ('AX', 'BX', 'CX', 'DX')
REJESTRY = []

for i in let:
    # REJESTRY.append(i+'X')
    REJESTRY.append(i+'XH')
    REJESTRY.append(i+'XL')


class gui(QWidget):
    def __init__(self, PROC):
        super().__init__()
        self.w = 800
        self.h = 480
        self.PROC = PROC
        self.setWindowTitle("Symulator mikroprocesora")
        self.initUI()
        self.press_now = False

    def initUI(self):
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.menubar = QMenuBar()
        self.layout.addWidget(self.menubar, 0, 0)
        load_action = QAction('&Load', self)
        save_action = QAction('&Save', self)
        self.menubar.addAction(load_action)
        self.menubar.addAction(save_action)
        load_action.triggered.connect(self.load_file)
        save_action.triggered.connect(self.save_file)

        self.editor_layout = QHBoxLayout()
        self.scroller = QScrollArea()
        self.scroller.setWidgetResizable(True)
        self.scroller.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.layout.addWidget(self.scroller, 1, 0)

        self.text_editor_widget = QWidget()
        self.text_editor_widget.setLayout(self.editor_layout)
        self.scroller.setWidget(self.text_editor_widget)

        self.line_numbers = GrowingTextEdit()
        self.line_numbers.setStyleSheet(
            "background-color: rgba(100,100,100,255); color:white;")
        self.editor_layout.addWidget(self.line_numbers)
        self.line_numbers.setReadOnly(True)
        self.editor_layout.setSpacing(0)
        self.line_numbers.setFixedWidth(40)
        self.line_numbers.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.terminal = GrowingTextEdit()
        self.terminal.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.terminal.textChanged.connect(self.analyze_text)
        self.editor_layout.addWidget(self.terminal)
        self.terminal.setFocus(True)
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFixedHeight(80)

        self.run_all_button = QPushButton('Praca całościowa - skrót[F2]')
        self.run_all_button.clicked.connect(self.run_all)
        self.run_all_button.setShortcut("F2")

        self.step_button = QPushButton('Praca krokowa - skrót[F3]')
        self.step_button.clicked.connect(self.run_step)
        self.step_line = 0

        self.line_counter = QLabel('Linia: {}'.format(self.step_line))
        self.line_counter.setStyleSheet("border: 1px solid black;")
        self.step_button.setShortcut('F3')

        sciaga = QLabel()
        sciaga.setText('Dozwolone konwencje:\nMOV|ADD|SUB REJESTR, REJESTR\nMOV|ADD|SUB REJESTR, LICZBA\nDostepne rejestry:\n{}\n\n Najechać na pole, a pokaże się informacja'.format(REJESTRY))
        self.side_panel_layout = QFormLayout()
        self.side_panel_layout.setVerticalSpacing(2)
        self.side_panel_layout.addWidget(sciaga)

        self.setStyleSheet("""QToolTip { 
                           background-color: white; 
                           color: black; 
                           border: 2px solid red;
                           border-radius: 3px;
                           font-size:14px;
                           padding:5px;
                           }
                          *[cssClass="tooltip_label"]
                          {border: 1px solid black; 
                                    padding: 1px; 
                                    margin: 0px 0px 1px 0px;
                                    background-color:white;
                                    font-size:12px;
                           }
                          *[cssClass="tooltip_label"]:hover
                          {
                               color:white;
                               background-color:rgba(100,100,100,255);
                            }
                            """)

        with open('tooltips.json') as f:
            data = json.load(f)
            for val in data["functions"]:
                self.side_panel_layout.addWidget(
                    self.label_with_tooltip(val["name"], val["text"]))

        self.side_panel_layout.addWidget(self.run_all_button)
        self.side_panel_layout.addWidget(self.step_button)
        self.side_panel_layout.addWidget(self.line_counter)
        self.prev_A = self.rejestr_preview('AX')
        self.side_panel_layout.addWidget(self.prev_A)
        self.prev_B = self.rejestr_preview('BX')
        self.side_panel_layout.addWidget(self.prev_B)
        self.prev_C = self.rejestr_preview('CX')
        self.side_panel_layout.addWidget(self.prev_C)
        self.prev_D = self.rejestr_preview('DX')
        self.side_panel_layout.addWidget(self.prev_D)
        self.side_panel_layout.setAlignment(self.prev_A, Qt.AlignHCenter)
        self.side_panel_layout.setAlignment(self.prev_B, Qt.AlignHCenter)
        self.side_panel_layout.setAlignment(self.prev_C, Qt.AlignHCenter)
        self.side_panel_layout.setAlignment(self.prev_D, Qt.AlignHCenter)
        self.layout.addWidget(
            QLabel('KONSOLA - Krótkie komunikaty o błędach'), 3, 0)
        self.layout.addWidget(self.console, 4, 0)
        self.layout.setColumnStretch(1, 2)
        self.layout.setColumnStretch(0, 4)
        self.layout.addLayout(self.side_panel_layout, 1, 1)
        self.setGeometry(100, 100, self.w, self.h)
        self.show()

    def load_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Load file", "", "TXT files (*.txt);;All Files (*)", options=options)
        if file_name:
            try:
                with open(file_name, 'r') as f:
                    self.terminal.setPlainText(f.read())
            except:
                self.console_print("Wybierz poprawny format")

    def lose_focus(self):
        self.setFocus(True)

    def keyPressEvent(self, keyEvent):
        if(self.press_now == True):
            asc = keyEvent.text()
            self.press_now = False
            print(asc)
            procek.AX.L = ord(asc)
            procek.update_rej()

    def save_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Load file", "", "TXT files (*.txt);;All Files (*)", options=options)
        if file_name:
            file_name = file_name + '.txt'
            try:
                with open(file_name, 'w') as f:
                    f.write(self.terminal.toPlainText())
            except:
                self.console_print("Problem z zapisaniem pliku")

    def analyze_text(self, reset=True):
        terminal_text = self.terminal.toPlainText()
        length = len(terminal_text.splitlines())
        line = ""
        cursor = self.terminal.textCursor()
        cursor_rect = self.terminal.cursorRect()

        self.scroller.ensureVisible(
            cursor_rect.x(), cursor_rect.y(), xMargin=0, yMargin=50)

        for i in range(length):
            if i == self.step_line:
                line += '>{}\n'.format(i)
            else:
                line += str(i) + "\n"
        self.line_numbers.setPlainText(line)
        if reset == True:
            self.step_line = 0
            self.line_counter.setText("Linia: {}".format(self.step_line))

    def error_check_return_command(self, command, i):
        mode = 0
        if command.isspace() or not command:
            print("Skip in: {}".format(i))
            return "None", 0

        else:
            words = split(' |,', command)
            words = list(map(str.strip, words))
            words = [x for x in words if x]
            # FUNKCJA:
            if not words[0] in FUNCTIONS and not words[0] in STOS_FUNC and not words[0] in PRZERW:
                self.console_print(
                    "LINIA: {}, FUNKCJA:{} NIE ISTNIEJE".format(i, words[0]))
                return 0

            if words[0] in PRZERW:
                return (words[0], 0, 0), 0
            if words[0] in STOS_FUNC:
                try:
                    words[1]
                except:
                    self.console_print("LINIA:{} BRAK ARGUMENTU".format(i))
                    return 0
                if not words[1] in STOS_REJ:
                    self.console_print(
                        "LINIA: {}, ZŁY REJESTR:{}".format(i, words[1]))
                    return 0
                return (words[0], words[1], 0), 0

            if words[0] in FUNCTIONS:
                try:
                    words[1]
                except:
                    self.console_print("LINIA:{} BRAK ARGUMENTU".format(i))
                    return 0

                if not words[1] in REJESTRY:
                    self.console_print(
                        "LINIA: {}, REJESTR:{} NIE ISTNIEJE".format(i, words[1]))
                    return 0

                try:
                    words[2]
                except:
                    self.console_print("LINIA:{} BRAK ARGUMENTU".format(i))
                    return 0
                else:
                    try:
                        words[2] = int(words[2])
                        mode = 1
                    except:
                        mode = 2

                    if mode == 2:
                        if not words[2] in REJESTRY:
                            self.console_print(
                                "LINIA: {}, REJESTR:{} NIE ISTNIEJE".format(i, words[2]))
                            return 0
                if len(words) > 3:
                    self.console_print(
                        "LINIA: {} - ZA DUŻO ARGUMENTÓW".format(i))
                    return 0

                return words, mode

    def run_all(self):
        self.step_line = 0
        self.line_counter.setText("Linia: {}".format(self.step_line))
        terminal_text = self.terminal.toPlainText().upper()
        commands = terminal_text.splitlines()

        self.console.clear()
        self.PROC.clear_rej()

        for i, command in enumerate(commands):
            try:
                w, mode = self.error_check_return_command(command, i)
                self.PROC.execute(w[0], w[1], w[2])
            except:
                pass

    def run_step(self):
        if(self.step_line == 0):
            self.console.clear()
            self.PROC.clear_rej()
            self.command_list = self.terminal.toPlainText().upper().splitlines()

        try:
            w, mode = self.error_check_return_command(
                self.command_list[self.step_line], self.step_line)
            if(w != "None"):
                self.PROC.execute(w[0], w[1], w[2], mode)
            self.step_line += 1
            self.line_counter.setText("Linia: {}".format(self.step_line))
        except:
            pass

        if(self.step_line == len(self.command_list)):
            self.step_line = 0
            self.line_counter.setText("Linia: {}".format(self.step_line))

        self.analyze_text(reset=False)

    def console_print(self, Text):
        print(Text)
        self.console.moveCursor(QTextCursor.End)
        self.console.insertPlainText("\n" + Text)

    class rejestr_preview(QWidget):
        def __init__(self, title):
            super().__init__()
            self.layout = QHBoxLayout()
            self.name = QLabel(title)

            self.high = QLabel()
            self.low = QLabel()
            self.high.setContentsMargins(0, 0, 0, 0)

            self.high.setStyleSheet(
                'background-color:rgb(230,230,230);border:1px solid black;margin:0;padding:0;')
            self.low.setStyleSheet(
                'background-color:rgb(230,230,230);border:1px solid black;margin:0;padding:0;')
            self.rej_layout = QGridLayout()
            self.rej_layout.setSpacing(0)

            self.rej_layout.addWidget(self.high, 0, 0)
            self.rej_layout.addWidget(self.low, 0, 1)
            self.layout.addWidget(self.name)
            self.layout.addLayout(self.rej_layout)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.setLayout(self.layout)

        def update(self, str_high, str_low):
            self.high.setText(" ".join(str_high))
            self.low.setText(" ".join(str_low))

    class label_with_tooltip(QLabel):
        def __init__(self, label_text, tip_text):
            super().__init__(label_text)
            self.setToolTip(tip_text)
            self.setProperty("cssClass", "tooltip_label")


app = QApplication([])
procek = procesor(app)

ex = gui(procek)
procek.AX.preview = ex.prev_A
procek.BX.preview = ex.prev_B
procek.CX.preview = ex.prev_C
procek.DX.preview = ex.prev_D
procek.update_rej()
app.exec_()
