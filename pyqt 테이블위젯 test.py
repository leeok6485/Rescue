import sys
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QHeaderView


class MianWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 윈도우 설정
        self.setGeometry(400, 200, 1000, 600)
        self.setWindowTitle('연습용')
        # 테이블위젯
        self.tablewidget = QTableWidget(self)
        self.tablewidget.resize(1200, 600)
        self.tablewidget.setRowCount(50)
        self.tablewidget.setColumnCount(3)
        # self.tablewidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 테이블위젯에 데이터 추가
        self.insert_data()
        # 수정 가능한 필드
        self.tablewidget.setEditTriggers(QAbstractItemView.AllEditTriggers)
        # 데이터 조회
        rowcount = self.tablewidget.rowCount()
        colcount = self.tablewidget.columnCount()

        for i in range(0, rowcount):
            for j in range(0, colcount):
                data = self.tablewidget.item(i, j)
                if data is not None:
                    print(data.text())
                else:
                    print('공백')
        # 테이블 이벤트 지정
        self.tablewidget.cellChanged.connect(self.cellchange_event)
        self.tablewidget.currentCellChanged.connect(self.currentcellchanged_event)
        self.tablewidget.cellClicked.connect(self.cellclicked_event)
        self.tablewidget.cellDoubleClicked.connect(self.celldoubleclicked_event)
        # header1 = self.tablewidget.horizontalHeader()
        # header1.resizeSection(0, 10)
        header1 = self.tablewidget.horizontalHeader()
        header1.resizeSection(0, 50)
        header2 = self.tablewidget.horizontalHeader()
        header2.resizeSection(1, 300)
        header3 = self.tablewidget.horizontalHeader()
        header3.resizeSection(2, 700)

    # 셀 더블클릭시 이벤트
    def celldoubleclicked_event(self, row, col):
        data = self.tablewidget.item(row, col)
        print("셀 더블클릭 셀 값 : ", data.text())

    # 셀 선택시 이벤트
    def cellclicked_event(self, row, col):
        data = self.tablewidget.item(row, col)
        print("셀 클릭 셀 값 : ", data.text())

    # 선택한 셀의 값이 바뀌면 발생하는 이벤트
    def currentcellchanged_event(self, row, col, pre_row, pre_col):
        current_data = self.tablewidget.item(row, col) # 현재 선택 셀값값
        pre_data = self.tablewidget.item(pre_row, pre_col)
        if pre_data is not None:
            print("이전 선택 셀 값 : ", pre_data.text())
        else:
            print("이전 선택 셀 값 : 없음")
        print("현재 선택 셀 값 : ", current_data.text())

    # 셀의 내용이 바뀌었을 때 이벤트
    def cellchange_event(self, row, col):
        data = self.tablewidget.item(row, col)
        print("셀 변경 이벤트 발생 : ", data.text())

    def insert_data(self):
        self.tablewidget.setItem(0, 0, QTableWidgetItem("학생 이름"))
        self.tablewidget.setItem(0, 1, QTableWidgetItem("질문 내용"))
        self.tablewidget.setItem(1, 0, QTableWidgetItem("학생 이름"))
        self.tablewidget.setItem(1, 1, QTableWidgetItem(" "))
        self.tablewidget.setItem(0, 2, QTableWidgetItem("답변"))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MianWindow()
    mainWindow.show()
    sys.exit(app.exec_())
