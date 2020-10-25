from datetime import time
class State:
    """
    Generic state parent class for operational states
    """
    def __init__(self, transitions):
        self.transitions = transitions

    @property
    def name(self):
        print("ENTERING STATE ", self.name)

    def enter(self, machine):
        pass

    def exit(self, machine):
        pass


    def transition(self, machine):
        for transition in self.transitions:
            if transition.isTriggered():
                self.machine.go_to_state(transition.end_state)




class IdleState(State):
    """
    Default state for the satellite. Majority of actions occur via IdleState
    """
    ENTER_VOLT = 0.8 # volt > 0.8 lowpower -> idle
    EXIT_VOLT =  0.3 # volt < 0.3 idle -> lowpower
    @property
    def name(self):
        return 'idle'

    def enter(self, machine):
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):

        tumbling = False # TODO: need function to detect tumbling
        have_target = False # TODO: need function to detect if have target to reach
        take_photo = False # TODO: need function to decide when to turn on payload function

        # TODO: determine attitude @GNC
        # TODO: Detumble @GNC
        # TODO: Send CW beacon (need continous beacon)
        # TODO: Send telemetry data package
        # TODO: Listen for commands

        if machine.get_curr_vlot_pct() < self.EXIT_VOLT:
            machine.go_to_state('lowpower')
        elif machine.get_curr_vlot_pct() > machine.states['actuate'].ENTER_VOLT and tumbling:
            machine.go_to_state('actuate')
        # TODO: check if iLQR state is needed
        # elif machine.get_curr_vlot_pct() > machine.states['iLQR'].ENTER_VOLT and have_target:
        #     machine.go_to_state('iLQR')
        elif machine.get_curr_vlot_pct() > machine.states['payload'].ENTER_VOLT and take_photo:
            machine.go_to_state('payload') # state which deal with radio and photo
        else:
            pass


class LowPowerState(State):
    """
    Low-Power mode to conserve energy
    """
    ENTER_VOLT = 0.3
    EXIT_VOLT =  0.8
    @property
    def name(self):
        return 'lowpower'

    def enter(self, machine):
        State.enter(self, machine)

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        while machine.get_curr_vlot_pct() < self.EXIT_VOLT:
            time.sleep(0.5) # check battery voltage every 0.5 second
        if machine.get_curr_vlot_pct() > self.EXIT_VOLT:
            machine.go_to_state('idle')
        else:
            pass

class ActuateState(State):
    """
    For all actuation purposes (using magnetorquers)
    """
    ENTER_VOLT = 0.7
    EXIT_VOLT = 0.2
    @property
    def name(self):
        return 'actuate'

    def enter(self, machine):
        State.enter(self, machine)

    def exit(self, machine):
        State.exitwhen (self, machine)

    def update(self, machine):
        '''
        Bold = np.array(machine.sensors_old[0:3])
        Bnew = np.array(machine.sensors[0:3])
        Bdot = detumble.get_B_dot(Bold, Bnew, .1) # this is a hardcoded tstep (for now)
        machine.cmd = list(detumble.detumble_B_dot(Bnew, Bdot))

        '''
        while machine.get_curr_vlot_pct() > self.EXIT_VOLT:
            # TODO：calculate state estimate, dipole, actuate magnetorquer
            target_reached = True # TODO: need function to determine if target is reached
            time.sleep(0.1) # update battery information & perform operation in 10 Hz
        if machine.get_curr_vlot_pct() < self.EXIT_VOLT or target_reached:
            machine.go_to_state('idle')

class PayloadState(State):
    """
    For use of camera/radio/etc.
    """
    ENTER_VOLT = 0.7
    EXITState = 0.2

    @property
    def name(self):
        return 'payload'

    def enter(self, machine):
        State.enter(self, machine)

    def update(self, machine):
        # TODO: determine attitude @GNC
        # TODO: Detumble @GNC
        # TODO: Send CW beacon (need continous beacon)
        # TODO: Send telemetry data package
        # TODO: Listen for all commands (not just one)
        # TODO: Check for RasPi messages
        # TODO: Send RasPi messages (what?)

        while machine.get_curr_vlot_pct() > self.EXIT_VOLT:
            #TODO: use radio, take photos
            Done = True # TODO: need some function to determing if task finished in the payload mode
            tumbling = False # TODO: need function to detect tumbling
            time.sleep(0.1) # update battery information & perform operation in 10 Hz
        if machine.get_curr_vlot_pct() < self.EXIT_VOLT or Done or tumbling:
            machine.go_to_state('idle')
        else:
            pass