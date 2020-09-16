from pycubed import cubesat
from transitions import LowPowerTransition
from state_machine import StateMachine
from states import IdleState, DetumbleState

MIN_VOLTAGE = 0.3

def initialize_state_machine():
    # create machine object of class StateMachine and add states
    machine = StateMachine(cubesat)
    lowPowerTransition = LowPowerTransition('lowpower', MIN_VOLTAGE)
    machine.add_state(IdleState([lowPowerTransition]))
    machine.add_state(DetumbleState([]))

    machine.cubesat = cubesat

    # start off the StateMachine object in idle
    machine.go_to_state('detumble')

if __name__ == "__main__":
    initialize_state_machine()
    # wait until an input from the computer before continuing
    # machine.cubesat.RGB = (255, 0, 0) # set LED to red
    # input()
    # machine.cubesat.RGB = (0, 255, 0) # set LED to green
