import time


class State:
    """
    Generic state parent class for operational states
    """

    def __init__(self, transitions):
        self.transitions = transitions
        self.machine = None

    def set_machine(self, machine):
        self.machine = machine

    @property
    def name(self):
        return 'default'

    def enter(self):
        pass

    def exit(self):
        pass

    def get_next_state(self):
        for transition in self.transitions:
            if transition.isTriggered():
                return transition.end_state

        return self.name


class IdleState(State):
    """
    Default state for the satellite. Majority of actions occur via IdleState
    """

    @property
    def name(self):
        return 'idle'

    def enter(self):
        super().enter()

    def exit(self):
        super().exit()

    def update(self):
        tumbling = False  # TODO: need function to detect tumbling
        have_target = False  # TODO: need function to detect if have target to reach
        print("State: Idle")
        # TODO: determine attitude @GNC
        # TODO: Detumble @GNC
        # TODO: Send CW beacon (need continous beacon)
        # TODO: Send telemetry data package
        # TODO: Listen for commands

        pass


class LowPowerState(State):
    """
    Low-Power mode to conserve energy
    """

    @property
    def name(self):
        return 'lowpower'

    def enter(self):
        super().enter()

    def exit(self):
        super().enter()

    def update(self):
        print("State: Low power, Current Voltage", self.machine.cubesat.battery_voltage)


class ActuateState(State):
    """
    For all actuation purposes (using magnetorquers)
    """

    @property
    def name(self):
        return 'actuate'

    def update(self):
        '''
        Bold = np.array(machine.sensors_old[0:3])
        Bnew = np.array(machine.sensors[0:3])
        Bdot = detumble.get_B_dot(Bold, Bnew, .1) # this is a hardcoded tstep (for now)
        machine.cmd = list(detumble.detumble_B_dot(Bnew, Bdot))

        '''
        pass


class PayloadState(State):
    """
    For use of camera/radio/etc.
    """

    @property
    def name(self):
        return 'payload'

    def update(self):
        # TODO: determine attitude @GNC
        # TODO: Detumble @GNC
        # TODO: Send CW beacon (need continous beacon)
        # TODO: Send telemetry data package
        # TODO: Listen for all commands (not just one)
        # TODO: Check for RasPi messages
        # TODO: Send RasPi messages (what?)
        pass
