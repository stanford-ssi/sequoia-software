from pycubed import cubesat

# create machine object of class StateMachine and add states
machine = StateMachine()
machine.add_state(IdleState())
machine.add_state(DetumbleState())

machine.cubesat = cubesat

# start off the StateMachine object in idle
machine.go_to_state('detumble')

# wait until an input from the computer before continuing
machine.cubesat.RGB = (255, 0, 0) # set LED to red
input()
machine.cubesat.RGB = (0, 255, 0) # set LED to green
