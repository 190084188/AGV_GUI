import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow
from resource.UI import AGV_GUI,Main_GUI
import modbus_set


class AGV_GUI(QMainWindow, AGV_GUI.Ui_AGV_GUI,modbus_set.AGVController):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.mytimer = QTimer(self)
        self.mytimer.timeout.connect(self.onTimer)
        self.mytimer.start(100)
        self.pb_Connect.clicked.connect(self.connect_agv)
        self.pb_Sent.clicked.connect(self.sent_param)
        self.pb_Forward.clicked.connect(self.go_f)
        self.pb_Backward.clicked.connect(self.go_b)
        self.pb_Left.clicked.connect(self.go_l)
        self.pb_Right.clicked.connect(self.go_r)
        self.pb_Stop.clicked.connect(self.stop)
    def connect_agv(self):
        ip = self.textEdit_IP.toPlainText()
        port = self.textEdit_Port.toPlainText()
        self.init(ip, port)
        if self.connected == 1:
            self.textEdit_Connect.setText("已连接")
        else:
            self.textEdit_Connect.setText("未连接")

    def onTimer(self):
        if self.connected == 1:
            if self.button_Heartbeat.isChecked():
                current_value = self.client.read_holding_registers(40010, 1)[0]
                new_value = 1 if current_value != 1 else 2
                self.client.write_single_register(40010, new_value)
            else:
                pass
            self.textEdit_Connect.setText("已连接")
            self.readonly_status()
            self.textEdit_vX.setText(self.AGV_vx)
            self.textEdit_vY.setText(self.AGV_vy)
            self.textEdit_vW.setText(self.AGV_vw)
            self.textEdit_battery.setText(self.AGV_battery)
            self.textEdit_posX.setText(self.AGV_posx)
            self.textEdit_posY.setText(self.AGV_posy)
            self.textEdit_angle.setText(self.AGV_theta)
            self.textEdit_MovingStatus.setText(self.AGV_movingstatus)
            self.textEdit_MorA.setText("手动" if self.AGV_mannualorauto == 1 else "自动")
            self.textEdit_ESStatus.setText("触发" if self.AGV_emergencystop == 1 else "未触发")
        else:
            self.textEdit_Connect.setText("未连接")

    def sent_param(self):
        self.change_vx(self.textEdit_vX.toPlainText())
        self.change_vy(self.textEdit_vY.toPlainText())
        self.change_vw(self.textEdit_vW.toPlainText())

    def go_f(self):
        self.change_vx(0.1)
        self.change_vy(0)
        self.change_vw(0.1)

    def go_b(self):
        self.change_vx(-0.1)
        self.change_vy(0)
        self.change_vw(0.1)

    def go_l(self):
        self.change_vx(0)
        self.change_vy(0.1)
        self.change_vw(0.1)

    def go_r(self):
        self.change_vx(0)
        self.change_vy(-0.1)
        self.change_vw(0.1)

    def stop(self):
        self.change_vx(0)
        self.change_vy(0)
        self.change_vw(0)


class Main_window(QMainWindow, Main_GUI.Ui_Main_GUI):
    def __init__(self):
        super(Main_window, self).__init__()
        self.agv_gui = None
        self.setupUi(self)
        self.pb_AGVGUI.clicked.connect(self.open_agv_gui)

    def open_agv_gui(self):
        self.hide()
        self.agv_gui = AGV_GUI()
        self.agv_gui.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = Main_window()
    main.show()
    sys.exit(app.exec_())
