from random import randint

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

CLOCKS_PER_BIT = 120

@cocotb.test()
async def uart_rx_test(dut):
    global CLOCKS_PER_BIT
    CLOCKS_PER_BIT = dut.CLOCKS_PER_BIT.value
    cocotb.start_soon(Clock(dut.clk, 2, units='ns').start())

    await reset_dut(dut)
    # Check reset works
    for _ in range(100):
        data = ''.join([str(randint(0, 1)) for _ in range(8)])
        await recv_rx_byte(dut, data)
        await Timer(10, units='ns')


async def wait_one_bit(dut):
    for _ in range(CLOCKS_PER_BIT):
        await RisingEdge(dut.clk)


async def reset_dut(dut):
    dut.resetn.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.resetn.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)


async def recv_rx_byte(dut, input_data):
    dut.serial_i.value = 1
    while True:
        if dut.busy_o.value == 0:
            break

    # Start bit
    dut.serial_i.value = 0
    await wait_one_bit(dut)

    for v in input_data:
        dut.serial_i.value = int(v)
        await wait_one_bit(dut)

    # Stop bit
    dut.serial_i.value = 1
    await wait_one_bit(dut)

    assert dut.recv_data_o.value == int(input_data[::-1], base=2)

