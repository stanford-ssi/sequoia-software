import pycubed


class Transition:
    """
    Transition parent class for operational state transitions
    """

    def __init__(self, end_state):
        self.end_state = end_state

    def is_triggered(self):
        return False


class LowPowerTransition(Transition):
    def __init__(self, end_state, min_voltage):
        super().__init__(end_state)
        self.min_voltage = min_voltage

    def is_triggered(self):
        vbatt = pycubed.cubesat.battery_voltage
        return vbatt < self.min_voltage


class HighPowerTransition(Transition):
    def __init__(self, end_state, min_voltage):
        super().__init__(end_state)
        self.min_voltage = min_voltage

    def is_triggered(self):
        vbatt = pycubed.cubesat.battery_voltage
        return vbatt >= self.min_voltage
