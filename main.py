import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow
from resource.UI import AGV_GUI, Main_GUI
from modbus_set import AGVController


class AGV_GUI(QMainWindow, AGV_GUI.Ui_AGV_GUI):
    def __init__(self):
        super(AGV_GUI, self).__init__()
        self.connected = 0
        self.setupUi(self)
        self.AGV = AGVController()
        self.ip = self.textEdit_IP.toPlainText().strip()
        self.port = int(self.textEdit_Port.toPlainText().strip())
        self.mytimer = QTimer(self)
        self.mytimer.start(1000)
        self.mytimer.timeout.connect(self.onTimer)
        self.pb_Connect.clicked.connect(self.connect_agv)
        self.pb_Sent.clicked.connect(self.sent_param)
        self.pb_Forward.clicked.connect(self.go_f)
        self.pb_Backward.clicked.connect(self.go_b)
        self.pb_Left.clicked.connect(self.go_l)
        self.pb_Right.clicked.connect(self.go_r)
        self.pb_Stop.clicked.connect(self.stop)

    def connect_agv(self):
        if self.connected == 0:
            self.ip = self.textEdit_IP.toPlainText().strip()
            self.port = int(self.textEdit_Port.toPlainText().strip())
            self.AGV.modbus_init(self.ip, self.port)
            self.label.setText(str(self.AGV.AGV_battery)+"%")
            self.textEdit_MorA.setPlainText("手动" if self.AGV.AGV_mannualorauto == 2 else "自动")
            self.connected = 1
            self.textEdit_Connect.setPlainText("断开连接")
        # ip = self.textEdit_IP.toPlainText()
        # port = int(self.textEdit_Port.toPlainText())
        # self.AGV.modbus_init(ip, port)
        # self.label.setText(str(self.AGV.AGV_battery))
        else:
            self.AGV.client.close()
            self.connected = 0
            self.textEdit_Connect.setPlainText("连接AGV")

    def sent_param(self):
        self.AGV.change_vx(float(self.textEdit_vX.toPlainText().strip()))
        self.AGV.change_vy(float(self.textEdit_vY.toPlainText().strip()))
        self.AGV.change_vw(float(self.textEdit_vW.toPlainText().strip()))

    def go_f(self):
        self.AGV.change_vx(0.1)
        self.AGV.change_vy(0)
        self.AGV.change_vw(0.1)

    def go_b(self):
        self.AGV.change_vx(-0.1)
        self.AGV.change_vy(0)
        self.AGV.change_vw(0.1)

    def go_l(self):
        self.AGV.change_vx(0)
        self.AGV.change_vy(0.1)
        self.AGV.change_vw(0.1)

    def go_r(self):
        self.AGV.change_vx(0)
        self.AGV.change_vy(-0.1)
        self.AGV.change_vw(0.1)

    def stop(self):
        self.AGV.change_vx(0)
        self.AGV.change_vy(0)
        self.AGV.change_vw(0)

    def onTimer(self):
        if self.connected == 1:
            if self.button_Heartbeat.isChecked():
                current_value = self.AGV.client.read_holding_registers(9, 1)[0]
                new_value = 1 if current_value != 1 else 2
                self.client.write_holding_register(9, new_value)
            self.AGV.readonly_status()
            self.textEdit_vX.setPlainText(self.AGV.AGV_vx)
            self.textEdit_vY.setPlainText(self.AGV.AGV_vy)
            self.textEdit_vW.setPlainText(self.AGV.AGV_vw)
            self.label.setText(str(self.AGV.AGV_battery)+"%")
            self.textEdit_MorA.setPlainText("手动" if self.AGV.AGV_mannualorauto == 2 else "自动")
            self.textEdit_posX.setPlainText(self.AGV.AGV_posx)
            self.textEdit_posY.setPlainText(self.AGV.AGV_posy)
            self.textEdit_angle.setPlainText(self.AGV.AGV_theta)
            self.textEdit_MovingStatus.setPlainText(self.AGV.AGV_movingstatus)
            self.textEdit_ESStatus.setPlainText("触发" if self.AGV_emergencystop == 1 else "未触发")

class MainWindow(QMainWindow, Main_GUI.Ui_Main_GUI):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.agv_gui = None
        self.setupUi(self)
        self.pb_AGVGUI.clicked.connect(self.open_agv_gui)

    def open_agv_gui(self):
        self.hide()
        self.agv_gui = AGV_GUI()
        self.agv_gui.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = AGV_GUI()
    main.show()
    sys.exit(app.exec_())
