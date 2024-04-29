import struct
import time
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from pyModbusTCP.client import ModbusClient


class AGVController:
    error_signal = pyqtSignal(str)

    def __init__(self):
        self.client = None
        self.AGV_battery = None
        self.AGV_mannualorauto = None
        self.AGV_theta = None
        self.AGV_posy = None
        self.AGV_posx = None
        self.AGV_vw = None
        self.AGV_vy = None
        self.AGV_vx = None
        self.AGV_emergencystop = None
        # self.AGV_presentnavigationpoint = None
        # self.AGV_stopreason = None
        # self.AGV_movingstatus = None
        # self.AGV_safelidarstatus = None
        # self.AGV_movingstop = None
        # self.AGV_fsafelidarareastatus = None
        # self.AGV_bsafelidarareastatus = None
        # self.AGV_fpointcloudlidarareastatus = None
        # self.AGV_bpointcloudlidarareastatus = None

    def modbus_init(self, ip, port):
        try:
            self.client = ModbusClient(host=ip, port=port, auto_open=False, auto_close=False)
            # self.client = ModbusClient(host=ip, port=port, auto_open=True, auto_close=False)
            self.client.open()
            self.readonly_status()
            # return self.client
        except Exception as e:
            self.error_signal.emit(f"Failed to initialize Modbus connection: {str(e)}")

    def read_holding_registers(self, address, count):
        try:
            return self.client.read_holding_registers(address, count)
        except Exception as e:
            print(f"Error reading holding registers: {e}")
            return None

    def read_discrete_inputs(self, address, count):
        try:
            return self.client.read_discrete_inputs(address, count)
        except Exception as e:
            print(f"Error reading holding registers: {e}")
            return None

    def read_input_registers(self, address, count):
        try:
            return self.client.read_input_registers(address, count)
        except Exception as e:
            print(f"Error reading input registers: {e}")
            return None

    def read_holding_float32(self, address):
        try:
            # 从指定地址读取两个连续的寄存器
            registers = self.client.read_holding_registers(address, 2)
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
            self.error_signal.emit(f"Error reading float from address {address}: {str(e)}")
            return None

    def read_input_float32_SE(self, address):
        try:
            # 从指定地址读取两个连续的寄存器
            registers = self.client.read_input_registers(address, 2)
            # 合并寄存器值为32位整数
            # 适用于小端格式的设备（低地址寄存器在前）
            # 对于大端格式的设备，调整 registers[0] 和 registers[1] 的顺序
            raw_value = registers[0] + (registers[1] << 16)
            # 将32位整数解码为浮点数
            float_value = struct.unpack('f', struct.pack('I', raw_value))[0]
            float_value = "{:.4f}".format(float_value)
            return float_value
        except Exception as e:
            self.error_signal.emit(f"Error reading float from address {address}: {str(e)}")
            return None

    def read_input_float32_BE(self, address):
        try:
            # 从指定地址读取两个连续的寄存器
            registers = self.client.read_input_registers(address, 2)
            if registers is None:
                print(f"Failed to read input registers at address {address}")
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
            self.error_signal.emit(f"Error reading float from address {address}: {str(e)}")
            return None

    def write_float32(self, address, float_value):
        try:
            # 将float转换为4字节的二进制数据
            packed_float = struct.pack('f', float_value)
            # 将4字节数据转换为两个16位的整数
            low, high = struct.unpack('<HH', packed_float)  # '<HH' 表示小端模式
            # 将两个整数写入连续的寄存器
            self.client.write_multiple_registers(address, [low, high])
        except Exception as e:
            self.error_signal.emit(f"Error writing to holding register at address {address}: {str(e)}")
            return False

    def write_holding_register(self, address, value):
        try:
            self.client.write_single_register(address, value)
        except Exception as e:
            print(f"Error writing to holding register: {e}")
            return False

    def readonly_status(self):
        self.AGV_vx = self.read_input_float32_BE(0)
        self.AGV_vy = self.read_input_float32_BE(2)
        self.AGV_vw = self.read_input_float32_BE(4)
        self.AGV_posx = self.read_input_float32_BE(6)
        self.AGV_posy = self.read_input_float32_BE(8)
        self.AGV_theta = self.read_input_float32_BE(10)
        self.AGV_battery = self.read_input_registers(15, 1)[0]
        self.AGV_mannualorauto = self.read_input_registers(18, 1)[0]
        ##########################################################################
        # self.AGV_movingstatus = self.read_input_registers(14, 1)[0]
        # self.AGV_fsafelidarareastatus = self.read_input_registers(19, 1)[0]
        # self.AGV_bsafelidarareastatus = self.read_input_registers(20, 1)[0]
        # self.AGV_fpointcloudlidarareastatus = self.read_input_registers(31, 1)[0]
        # self.AGV_bpointcloudlidarareastatus = self.read_input_registers(32, 1)[0]
        # self.AGV_safelidarstatus = self.read_input_registers(16, 1)[0]
        # self.AGV_presentnavigationpoint = self.read_input_registers(12, 1)[0]
        # self.AGV_stopreason = self.read_input_registers(13, 1)[0]
        # self.AGV_movingstop = self.read_input_registers(8, 1)[0]
        # self.AGV_emergencystop = self.read_input_registers(9, 1)[0]

    def change_vx(self, value):
        self.write_float32(0, value)

    def change_vy(self, value):
        self.write_float32(2, value)

    def change_vw(self, value):
        self.write_float32(4, value)


class Worker(QThread):
    def __init__(self):
        super().__init__()
        self.client = AGVController()
        self.client.modbus_init('127.0.0.1', 3001)

    def run(self):
        while True:
            print(self.client.AGV_vx)
            time.sleep(0.1)

class Controller(ModbusClient):
    def __init__(self, ip, port):
        super(Controller, self).__init__(host=ip, port=port, auto_open=False)
        self.open()

    def read_holding_float32(self, address):
        try:
            # 从指定地址读取两个连续的寄存器
            registers = self.read_holding_registers(address, 2)
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
            registers = self.read_input_registers(address, 2)
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
            self.write_multiple_registers(address, [low, high])
        except Exception as e:
            print(f"Error writing to holding register at address {address}: {str(e)}")
            return False

    def change_vx(self, value):
        self.write_float32(0, value)

    def change_vy(self, value):
        self.write_float32(2, value)

    def change_vw(self, value):
        self.write_float32(4, value)


if __name__ == "__main__":
    w = Worker()
    s = Worker()
    a = Worker()
    w.start()
    s.start()
    a.start()
