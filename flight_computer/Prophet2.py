import numpy as np
import random as rand
from math import pi

class God(object):

    def __init__(self):
        self.sig_phi = .1
        self.sig_theta = .1
        self.sig_psi = .1

        self.dt = .1

        self.state = State()

        self.state_hist = []
        self.times = [0]

    # get exact (omniscient) angle measurement
    # returns state object
    # For example:	"god.get_state.phi"  gives the exact value of phi according to the
    def get_state(self):
        return self.state

    # take a noisy angle measurement
    def ang_measure(self):
        theta = rand.gauss(self.state.theta, self.sig_theta)
        phi = rand.gauss(self.state.phi, self.sig_phi)
        psi = rand.gauss(self.state.psi, self.sig_psi)

        return theta, phi, psi

    def vel_measure(self):
        theta_v = rand.gauss(self.state.theta_dot)

    # evolve state of system forward in time
    def timestep(self, dt=0):
        if dt == 0:
            dt = self.dt

        self.times.append(self.times[-1] + dt)

        self.state_hist.append(self.state)
        self.state.timestep(dt)

    # return a tuple:
    #	first element is a list of the times at which we have
    #	second element is a list of state objects at each of those times
    def get_history(self):
        return self.times, self.state_hist


class State(object):

    def __init__(self, td_range=1, psd_range=1, phd_range=1):
        self.theta = rand.uniform(0, 2 * pi)
        self.phi = rand.uniform(0, 2 * pi)
        self.psi = rand.uniform(0, pi)

        self.theta_dot = rand.uniform(-td_range, td_range)
        self.phi_dot = rand.uniform(-phd_range, phd_range)
        self.psi_dot = rand.uniform(-psd_range, psd_range)

    def timestep(self, dt):
        self.theta = (self.theta + dt * self.theta_dot) % (2 * pi)
        self.phi = (self.phi + dt * self.phi_dot) % (2 * pi)
        self.psi = (self.psi + dt * self.psi_dot) % pi

    def __str__(self):
        return str(self.theta) + " " + str(self.phi) + " " + str(self.psi) + "\n" + str(self.theta_dot) + " " + str(
            self.phi_dot) + " " + str(self.psi_dot)


# Will change to theta dots and make whole thing 3 variables
THETAVEL = .1
PHIVEL = .2
PSIVEL = .3

bigG = God()

def predictState(observedState, stateAMatrix, stateBMatrix):
    # what is the standard deviation here supposed to be?
    noisyMatrix = np.random.normal(0, bigG.sig_theta ** 2) * stateBMatrix
    newState = np.matmul(stateAMatrix, observedState) + noisyMatrix
    return newState

# Kinda wack because I don't know errors
def predictCovMat(covMatrix, AMatrix):
    return np.matmul(np.matmul(AMatrix, covMatrix), AMatrix.transpose())

def getKalmanGain(covMatrix, observationErrorMatrix):
    # What is our observation errors?
    denMat = covMatrix + observationErrorMatrix
    gainMat = covMatrix
    for i in range(len(gainMat)):
        for j in range(len(gainMat[0])):
            if(denMat[i, j] != 0):
                gainMat[i, j] = covMatrix[i, j] / denMat[i, j]
            else:
                gainMat[i, j] = 0
    return gainMat

def newObservation(godObject):
    godObject.timestep()
    return np.array([[bigG.ang_measure()[0]], [bigG.ang_measure()[1]], [bigG.ang_measure()[2]],
                    [THETAVEL], [PHIVEL], [PSIVEL]])

def getStateMatrix(predictedState, kalmainGain, newMeasurements):
    return predictedState + np.matmul(kalmainGain, newMeasurements - predictedState)

def updateCovMatrix(predictedCovMatrix, kalmanGain):
    return np.matmul(np.eye(len(kalmanGain)) - kalmanGain, predictedCovMatrix)

stateAMatrix = np.eye(6)
# How to do this without knowing rotational velocity
stateBMatrix = np.array([[THETAVEL * bigG.dt], [PHIVEL * bigG.dt], [PSIVEL * bigG.dt], [0], [0], [0]])
# covariance matrix is ones for now, need to fix later
covMatrix = np.array([[bigG.sig_theta ** 2, 0, 0, 0, 0, 0],
                      [0, bigG.sig_phi ** 2, 0, 0, 0, 0],
                      [0, 0, bigG.sig_psi ** 2, 0, 0, 0],
                      [0, 0, 0, 1, 0, 0],
                      [0, 0, 0, 0, 1, 0],
                      [0, 0, 0, 0, 0, 1]])

# change parameters to include covMatrix into godObject
def prophesize(godObject, covMatrix):
    for p in range(10):
        observationMatrix = np.array([[bigG.ang_measure()[0]], [bigG.ang_measure()[1]], [bigG.ang_measure()[2]],
                                      [THETAVEL], [PHIVEL], [PSIVEL]])
        predictedCovMatrix = predictCovMat(covMatrix, stateAMatrix)
        # What is observation error matrix for this
        kalmanGain = getKalmanGain(predictedCovMatrix, covMatrix)
        predictedState = predictState(observationMatrix, stateAMatrix, stateAMatrix)
        observationMatrix = newObservation(godObject)
        stateMatrix = getStateMatrix(predictedState, kalmanGain, observationMatrix)
        covMatrix = updateCovMatrix(predictedCovMatrix, kalmanGain)
        print(godObject.get_state())
        print(stateMatrix[:, 0])
        print()
        print(godObject.get_state().theta)
        print(stateMatrix[0, 0])
        print((godObject.get_state().theta - stateMatrix[0, 0]) / godObject.get_state().theta * 100)
        print()

prophesize(bigG, covMatrix)