from modbus_set import AGVController
class AGVGUITest:
    def __init__(self):
        self.AGV = AGVController()
        self.AGV.modbus_init('192.168.2.2',3001)

if __name__ == '__main__':
    agv = AGVGUITest()
    print(agv.AGV.AGV_battery)
