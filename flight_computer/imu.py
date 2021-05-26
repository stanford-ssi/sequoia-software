# -*- coding: utf-8 -*-
"""IMU.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1k5ksGkrnZP0Jqf5XC27Pk5SEVVcehPVR
"""

import board
import adafruit_lsm9ds1
import time

i2c = board.I2C() # uses board.SCL and board.SDA sensor = adafruit_lsm9ds1.LSM9DS1_I2C(i2c)
sensor = adafruit_lsm9ds1.LSM9DS1_I2C(i2c)

# acc_x, acc_y, acc_z = sensor.acceleration
# mag_x, mag_y, mag_z = sensor.magnetic
# gyro_x, gyro_y, gyro_z = sensor.gyro
# temp = sensor.temperature

# we want to validate via sun sensor luminosity
# to apply the torque, 
# validate using GPS data

def detumble(delT = 20):

  B_0X, B_0Y, B_OZ = sensor.magnetic
  currtime = time.time

  if (currtime + delT):
    B_1X, B_1Y, B_1Z = sensor.magnetic
    BdotX, BdotY, BdotZ = derivative(B_0X, B_1X, delT),  derivative(B_0Y, B_1Y, delT),  derivative(B_0Z, B_1Z, delT)

  magnetorquers.setmoment(BdotX, BdotY, BdotZ)

def dydt(y1, y2, dt):
  return (y2 - y1)/dt