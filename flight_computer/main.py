#from pycubed import cubesat
from opt3001 import Opt3001
import busio
import board
from microcontroller import Pin
import time
# from transitions import HighPowerTransition, LowPowerTransition
# from state_machine import StateMachine
# from states import IdleState, LowPowerState
# import time
#
# MIN_VOLTAGE = 5
#
#
# def initialize_state_machine():
#     # create machine object of class StateMachine and add states
#     machine = StateMachine(cubesat)
#     machine.cubesat = cubesat
#
#     # Initialize Transitions
#     low_power_transition = LowPowerTransition("lowpower", MIN_VOLTAGE)
#     high_power_transition = HighPowerTransition("idle", MIN_VOLTAGE)
#
#     # Add States
#     machine.add_state(IdleState([low_power_transition]))
#     machine.add_state(LowPowerState([high_power_transition]))
#
#     # start off the StateMachine object in idle
#     machine.go_to_state("idle")
#     return machine


# Test in case we want to see if PYCUBED is working
def light_debugging_routine():
    while True:
        print("PyCubed Running")
        time.sleep(1)
        cubesat.RGB = (1, 0, 0)
        time.sleep(1)
        cubesat.RGB = (0, 0, 1)

def is_hardware_I2C(scl, sda):
    try:
        p = busio.I2C(scl, sda)
        p.deinit()
        return True
    except ValueError:
        return False
    except RuntimeError:
        return True


def get_unique_pins():
    exclude = []
    pins = [pin for pin in [
        getattr(board, p) for p in dir(board) if p not in exclude]
            if isinstance(pin, Pin)]
    unique = []
    for p in pins:
        if p not in unique:
            unique.append(p)
    return unique

def scan_for_i2c_pins():
    for scl_pin in get_unique_pins():
        for sda_pin in get_unique_pins():
            if scl_pin is sda_pin:
                continue
            if is_hardware_I2C(scl_pin, sda_pin):
                print("SCL pin:", scl_pin, "\t SDA pin:", sda_pin)

def test_light_sensor():
    print("---Testing Light Sensor Driver---")
    print("Scanning for I2C pins")
    scan_for_i2c_pins()
    print("Initializing I2C Bus")
    i2c = busio.I2C(board.PB17, board.PB16)
    print("Initializing Driver")
    sun_sensor = Opt3001(i2c)
    print("Driver Initialized")
    print("Reading driver values")
    print("Received value of " + str(sun_sensor.lux))



if __name__ == "__main__":
    # Turn off light so grant can sleep
    test_light_sensor()
