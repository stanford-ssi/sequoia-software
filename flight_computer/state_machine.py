class StateMachine:
    """
    State Machine class
    """

    def __init__(self, cubesat):
        self.state = None  # the current state
        self.states = {}  # dict containing all the states
        self.sensors_old = [0, 0, 0, 0, 0, 0, 0, 0, 0]  # previous sensor measurements
        self.sensors = self.sensors_old  # current sensor measurements
        self.cmd = [0, 0, 0]  # current commanded dipole
        self.cubesat = cubesat
        self.max_volts = 5

    def add_state(self, state):
        self.states[state.name] = state
        state.set_machine(self)

    def go_to_state(self, state_name):
        if self.state:
            self.state.exit()
        self.state = self.states[state_name]
        self.state.enter()

    def update(self):
        # TODO: Implement sensors

        self.state.update()
        next_state_name = self.state.get_next_state()
        if next_state_name is None or next_state_name not in self.states:
            print("ERROR: Received none from state machine")
        else:
            self.state = self.states[next_state_name]
