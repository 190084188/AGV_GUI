from pyModbusTCP.client import ModbusClient
c = ModbusClient('127.0.0.1',3001)
c.open()
regs = c.read_coils(9,1)
regs = c.read_input_registers(0,20)
regs = c.read_discrete_inputs(8,2)
print(regs)