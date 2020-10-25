
class StateMachine():
    """
    State Machine class
    """
    def __init__(self, cubesat):
        self.state = None # the current state
        self.states = {} # dict containing all the states
        self.sensors_old = [0,0,0,0,0,0,0,0,0] # previous sensor measurements
        self.sensors = self.sensors_old # current sensor measurements
        self.cmd = [0,0,0] # current commanded dipole
        self.cubesat = cubesat

    def add_state(self, state):
        self.states[state.name] = state

    def go_to_state(self, state_name):
        if self.state:
            self.state.exit(self)
        self.state = self.states[state_name]
        self.state.enter(self)

    def update(self):
        # publish command input to magnetorquers and poll sensors
        self.sensors_old = self.sensors
        #self.sensors = sim_communicate(self.cmd)

        if self.state:
            self.state.update(self)
            self.state.transition(self)

        # passthrough_msg("free heap space: {}".format(gc.mem_free()))
        # if gc.mem_free() < 10000:
        #     gc.collect()

