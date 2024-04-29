import struct
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from pyModbusTCP.client import ModbusClient
from resource.UI import AGV_GUI, Main_GUI


class WriteThread(QThread):
    def __init__(self, controller):
        super(WriteThread, self).__init__()
        self.controller = controller
        self.heartbeat_active = False
        self.running = False
        self.vx = 0
        self.vy = 0
        self.vw = 0

    def run(self):
        self.running = True
        while True:
            if self.running:
                # print(self.heartbeat_active)
                if self.heartbeat_active:
                    current_heartbeat = 1 if self.controller.read_holding_registers(9, 1)[0] != 1 else 2
                    self.controller.write_single_register(9, current_heartbeat)
                self.write_float32(0, self.vx)
                self.write_float32(2, self.vy)
                self.write_float32(4, self.vw)
                self.msleep(50)
            else:
                break

    def update_vx(self, vx):
        self.vx = vx

    def update_vy(self, vy):
        self.vy = vy

    def update_vw(self, vw):
        self.vw = vw

    def toggle_heartbeat(self, state):
        self.heartbeat_active = state

    def read_holding_float32(self, address):
        try:
            # 从指定地址读取两个连续的寄存器
            registers = self.controller.read_holding_registers(address, 2)
            if registers is None:
                print(f"Failed to read holding registers at address {address}")
                return None
            # 合并寄存器值为32位整数
            # 适用于小端格式的设备（低地址寄存器在前）
            # 对于大端格式的设备，调整 registers[0] 和 registers[1] 的顺序
            raw_value = registers[0] + (registers[1] << 16)
            # 将32位整数解码为浮点数
            float_value = struct.unpack('f', struct.pack('I', raw_value))[0]
            float_value = "{:.4f}".format(float_value)
            return float_value
        except Exception as e:
            print(f"Error reading float from address {address}: {str(e)}")
            return None

    def read_input_float32_SE(self, address):
        try:
            # 从指定地址读取两个连续的寄存器
            registers = self.controller.read_input_registers(address, 2)
            # 合并寄存器值为32位整数
            # 适用于小端格式的设备（低地址寄存器在前）
            # 对于大端格式的设备，调整 registers[0] 和 registers[1] 的顺序
            raw_value = registers[0] + (registers[1] << 16)
            # 将32位整数解码为浮点数
            float_value = struct.unpack('f', struct.pack('I', raw_value))[0]
            float_value = "{:.4f}".format(float_value)
            return float_value
        except Exception as e:
            print(f"Error reading float from address {address}: {str(e)}")
            return None

    def write_float32(self, address, float_value):
        try:
            # 将float转换为4字节的二进制数据
            packed_float = struct.pack('f', float_value)
            # 将4字节数据转换为两个16位的整数
            low, high = struct.unpack('<HH', packed_float)  # '<HH' 表示小端模式
            # 将两个整数写入连续的寄存器
            self.controller.write_multiple_registers(address, [low, high])
        except Exception as e:
            print(f"Error writing to holding register at address {address}: {str(e)}")
            return False


class ReadThread(QThread):
    data_updated = pyqtSignal(dict)

    def __init__(self, controller):
        super(ReadThread, self).__init__()
        self.controller = controller
        self.running = False

    def run(self):
        self.running = True
        while True:
            if self.running:
                # 读取操作
                data = {
                    "vx": self.read_input_float32_SE(0),
                    "vy": self.read_input_float32_SE(2),
                    "vw": self.read_input_float32_SE(4),
                    "posx": self.read_input_float32_SE(6),
                    "posy": self.read_input_float32_SE(8),
                    "theta": self.read_input_float32_SE(10),
                    "MorA": self.controller.read_input_registers(18, 1)[0],
                    "battery": self.controller.read_input_registers(15, 1)[0],
                    "movingstatus": self.controller.read_discrete_inputs(8, 1)[0],
                    'ESStatus': self.controller.read_discrete_inputs(9, 1)[0]
                }
                self.data_updated.emit(data)
                self.msleep(499)
            else:
                break

    def read_holding_float32(self, address):
        try:
            # 从指定地址读取两个连续的寄存器
            registers = self.controller.read_holding_registers(address, 2)
            if registers is None:
                print(f"Failed to read holding registers at address {address}")
                return None
            # 合并寄存器值为32位整数
            # 适用于小端格式的设备（低地址寄存器在前）
            # 对于大端格式的设备，调整 registers[0] 和 registers[1] 的顺序
            raw_value = registers[0] + (registers[1] << 16)
            # 将32位整数解码为浮点数
            float_value = struct.unpack('f', struct.pack('I', raw_value))[0]
            float_value = "{:.4f}".format(float_value)
            return float_value
        except Exception as e:
            print(f"Error reading float from address {address}: {str(e)}")
            return None

    def read_input_float32_SE(self, address):
        try:
            # 从指定地址读取两个连续的寄存器
            registers = self.controller.read_input_registers(address, 2)
            # 合并寄存器值为32位整数
            # 适用于小端格式的设备（低地址寄存器在前）
            # 对于大端格式的设备，调整 registers[0] 和 registers[1] 的顺序
            raw_value = registers[0] + (registers[1] << 16)
            # 将32位整数解码为浮点数
            float_value = struct.unpack('f', struct.pack('I', raw_value))[0]
            float_value = "{:.4f}".format(float_value)
            return float_value
        except Exception as e:
            print(f"Error reading float from address {address}: {str(e)}")
            return None


class AGV_GUI(QMainWindow, AGV_GUI.Ui_AGV_GUI):
    vx_changed = pyqtSignal(float)
    vy_changed = pyqtSignal(float)
    vw_changed = pyqtSignal(float)
    heartbeat_changed = pyqtSignal(bool)

    def __init__(self):
        super(AGV_GUI, self).__init__()
        ############################################################
        self.setupUi(self)
        ############################################################
        self.connected = False
        self.ip = self.lineEdit_ip.text()
        self.port = int(self.lineEdit_port.text())
        self.vx = 0
        self.vy = 0
        self.vw = 0
        self.client_read = None
        self.client_write = None
        ############################################################
        self.read_thread = ReadThread(self.client_read)
        self.write_thread = WriteThread(self.client_write)
        # ------------------------------------------------------- #
        # self.read_thread.data_updated.connect(self.update_display)
        # self.vx_changed.connect(self.write_thread.update_vx)
        # self.vy_changed.connect(self.write_thread.update_vy)
        # self.vw_changed.connect(self.write_thread.update_vw)
        # self.heartbeat_changed.connect(self.write_thread.toggle_heartbeat)
        ############################################################
        self.pb_Connect.clicked.connect(self.connect_agv)
        # ------------------------------------------------------- #
        self.button_Heartbeat.clicked.connect(self.heartbeat_state_changed)
        self.doubleSpinBox_vx.valueChanged.connect(self.set_vx)
        self.doubleSpinBox_vy.valueChanged.connect(self.set_vy)
        self.doubleSpinBox_vw.valueChanged.connect(self.set_vw)
        self.pb_Sent.clicked.connect(self.sent_param)
        # ------------------------------------------------------- #
        self.pb_Forward.clicked.connect(self.go_f)
        self.pb_Backward.clicked.connect(self.go_b)
        self.pb_Left.clicked.connect(self.go_l)
        self.pb_Right.clicked.connect(self.go_r)
        # ------------------------------------------------------- #
        self.pb_Stop.clicked.connect(self.stop)

    def connect_agv(self):
        if not self.connected:
            self.ip = self.lineEdit_ip.text()
            self.port = int(self.lineEdit_port.text())
            connected = False  # 追踪连接状态
            try:
                self.client_read = ModbusClient(self.ip, self.port, auto_open=False, timeout=3.0)
                self.client_write = ModbusClient(self.ip, self.port, auto_open=False, timeout=3.0)
                if self.client_read.open() and self.client_write.open():
                    self.read_thread = ReadThread(self.client_read)
                    self.write_thread = WriteThread(self.client_write)
                    self.read_thread.data_updated.connect(self.update_display)
                    self.vx_changed.connect(self.write_thread.update_vx)
                    self.vy_changed.connect(self.write_thread.update_vy)
                    self.vw_changed.connect(self.write_thread.update_vw)
                    self.heartbeat_changed.connect(self.write_thread.toggle_heartbeat)
                    self.pb_Connect.setText("断开连接")
                    self.lineEdit_connect.setText("连接成功")
                    self.connected = True
                    self.read_thread.start()
                    self.write_thread.start()
                    connected = True
            except Exception as e:
                QMessageBox.warning(None, "警告", f"连接失败，请检查设备是否开启或网络配置！\n错误信息: {str(e)}",
                                    QMessageBox.Ok)
            finally:
                if not connected:
                    # 如果连接不成功，确保关闭所有可能已打开的连接
                    if self.client_read:
                        self.client_read.close()
                    if self.client_write:
                        self.client_write.close()
                    QMessageBox.warning(None, "错误警告", "连接失败，请检查设备或网络配置",
                                        QMessageBox.Ok)
                    self.lineEdit_connect.setText("连接失败")
        else:
            self.disconnect_agv()  # 分离断开连接的逻辑到单独的方法

    def disconnect_agv(self):
        if self.connected:
            # 用于断开连接并清理资源
            self.connected = False
            self.read_thread.running = False
            self.write_thread.running = False
            self.read_thread.wait()
            self.write_thread.wait()
            self.client_read.close()
            self.client_write.close()
            self.pb_Connect.setText("连接AGV")
            self.lineEdit_connect.setText("未连接")
        else:
            pass

    def heartbeat_state_changed(self):
        if self.button_Heartbeat.isChecked():
            self.heartbeat_changed.emit(self.button_Heartbeat.isChecked())
        else:
            self.heartbeat_changed.emit(self.button_Heartbeat.isChecked())

    def set_vx(self):
        # 发射改变后的vx值信号
        self.vx = self.doubleSpinBox_vx.value()
        self.vx_changed.emit(self.vx)

    def set_vy(self):
        # 发射改变后的vy值信号
        self.vy = self.doubleSpinBox_vy.value()
        self.vy_changed.emit(self.vy)

    def set_vw(self):
        # 发射改变后的vw值信号
        self.vw = self.doubleSpinBox_vw.value()
        self.vw_changed.emit(self.vw)

    def sent_param(self):
        # 从GUI获取参数并发送到写入线程
        self.vx_changed.emit(self.doubleSpinBox_vx.value())
        self.vy_changed.emit(self.doubleSpinBox_vy.value())
        self.vw_changed.emit(self.doubleSpinBox_vw.value())

    def update_display(self, data):
        # 更新GUI显示
        if data['vx'] is not None:
            self.lineEdit_vx.setText(str(data['vx']))
        if data['vy'] is not None:
            self.lineEdit_vy.setText(str(data['vy']))
        if data['vw'] is not None:
            self.lineEdit_vw.setText(str(data['vw']))
        if data['battery'] is not None:
            self.lineEdit_Battery.setText(str(data['battery']) + "%")
        if data['MorA'] is not None:
            self.lineEdit_MorA.setText("手动" if int(data['MorA']) == 2 else "自动")
        if data['posx'] is not None:
            self.lineEdit_posx.setText(data['posx'])
        if data['posy'] is not None:
            self.lineEdit_posy.setText(data['posy'])
        if data['theta'] is not None:
            self.lineEdit_angle.setText(data['theta'])
        if data['movingstatus'] is not None:
            self.lineEdit_MovingStatus.setText("移动遇阻" if data['movingstatus'] else "移动无阻")
        if data['ESStatus'] is not None:
            self.lineEdit_ESStatus.setText("急停触发" if data['ESStatus'] else "急停未触发")

    def go_f(self):
        if self.vx != 0:
            self.vx_changed.emit(abs(self.vx))
            self.vy_changed.emit(0)
            self.vw_changed.emit(0)
        else:
            self.vx_changed.emit(0.01)
            self.vy_changed.emit(0)
            self.vw_changed.emit(0)

    def go_b(self):
        if self.vx != 0:
            self.vx_changed.emit(-abs(self.vx))
            self.vy_changed.emit(0)
            self.vw_changed.emit(0)
        else:
            self.vx_changed.emit(-0.01)
            self.vy_changed.emit(0)
            self.vw_changed.emit(0)

    def go_l(self):
        if self.vw != 0:
            self.vx_changed.emit(0)
            self.vy_changed.emit(0)
            self.vw_changed.emit(abs(self.vw))
        else:
            self.vx_changed.emit(0)
            self.vy_changed.emit(0)
            self.vw_changed.emit(0.05)

    def go_r(self):
        if self.vw != 0:
            self.vx_changed.emit(0)
            self.vy_changed.emit(0)
            self.vw_changed.emit(-abs(self.vw))
        else:
            self.vx_changed.emit(0)
            self.vy_changed.emit(0)
            self.vw_changed.emit(-0.05)

    def stop(self):
        self.vx = 0
        self.vy = 0
        self.vw = 0
        self.vx_changed.emit(0)
        self.vy_changed.emit(0)
        self.vw_changed.emit(0)

    def closeEvent(self, event):
        msgBox = QtWidgets.QMessageBox(self)
        msgBox.setWindowTitle(u'温馨提示')
        msgBox.setText(u'确认退出?')
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msgBox.button(QtWidgets.QMessageBox.Yes).setText('确认')
        msgBox.button(QtWidgets.QMessageBox.No).setText('取消')
        msgBox.setDefaultButton(QtWidgets.QMessageBox.No)
        reply = msgBox.exec_()
        # QtWidgets.QMessageBox.question(self,u'弹窗名',u'弹窗内容',选项1,选项2)
        if reply == QtWidgets.QMessageBox.Yes:
            self.disconnect_agv()
            event.accept()  # 关闭窗口
        else:
            event.ignore()  # 忽视点击X事件


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
