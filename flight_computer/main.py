from pycubed import cubesat
from transitions import HighPowerTransition, LowPowerTransition
from state_machine import StateMachine
from states import IdleState, LowPowerState
import time

MIN_VOLTAGE = 5


def initialize_state_machine():
    # create machine object of class StateMachine and add states
    machine = StateMachine(cubesat)
    machine.cubesat = cubesat

    # Initialize Transitions
    low_power_transition = LowPowerTransition("lowpower", MIN_VOLTAGE)
    high_power_transition = HighPowerTransition("idle", MIN_VOLTAGE)

    # Add States
    machine.add_state(IdleState([low_power_transition]))
    machine.add_state(LowPowerState([high_power_transition]))

    # start off the StateMachine object in idle
    machine.go_to_state("idle")
    return machine


# Test in case we want to see if PYCUBED is working
def light_debugging_routine():
    while True:
        print("PyCubed Running")
        time.sleep(1)
        cubesat.RGB = (1, 0, 0)
        time.sleep(1)
        cubesat.RGB = (0, 0, 1)


if __name__ == "__main__":
    # Turn off light so grant can sleep
    cubesat.RGB = (0, 0, 0)
    machine = initialize_state_machine()
    while True:
        machine.update()
        time.sleep(1)
