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
    lowPowerTransition = LowPowerTransition('lowpower', MIN_VOLTAGE)
    highPowerTransition = HighPowerTransition('idle', MIN_VOLTAGE)

    # Add States
    machine.add_state(IdleState([lowPowerTransition]))
    machine.add_state(LowPowerState([highPowerTransition]))

    # start off the StateMachine object in idle
    machine.go_to_state('idle')
    return machine


# Test in case we want to see if PYCUBED is working
def LightDebuggingRoutine():
    while True:
        print("PyCubed Running")
        time.sleep(1)
        cubesat.RGB(255, 0, 0)
        time.sleep(1)
        cubesat.RGB(0, 0, 255)


if __name__ == "__main__":
    machine = initialize_state_machine()
    while True:
        machine.update()
        time.sleep(1)
