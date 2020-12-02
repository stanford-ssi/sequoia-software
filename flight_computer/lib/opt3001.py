import time

from adafruit_bus_device.i2c_device import I2CDevice

# Can be one of four possible values
# This assumes we connect the ADDR pin to GND
# See 8.3.4.1 in the specification
DEVICE_DEFAULT_I2C_ADDR = 0x44

# MAIN REGISTERS FOR PROGRAMMING DEVICE
RESULT = 0x00
CONFIGURATION = 0x1

# CONFIGURATION SETTINGS
AUTO_RANGE_SETTING = 0b1100
CONTINUOUS_CONVERSIONS = 0b11
DEFAULT_CONVERSION_TIME = 800
MAX_CONVERSION_TIME = 800

# FOR INTERRUPT MECHANISMS, UNUSED
LOW_LIMIT = 0x2
HIGH_LIMIT = 0x3

# CAN BE READ TO GET ID
MANUFACTURER_ID = 0x7E
DEVICE_ID = 0x7F

REGISTER_SIZE = 2


# EXTRACT k bits from and including pos p
# using n ... 0 indexing
def extract_bits(bits, pos, k):
    # first chop off everything exclusively after pos
    # then get k inclusive least significant bits from the 0 index
    return (bits >> pos) & ((1 << k) - 1)


class Opt3001:
    """OPT3001 Sun Sensor Driver"""

    def __init__(self, i2c_bus, address=DEVICE_DEFAULT_I2C_ADDR, conversion_time=DEFAULT_CONVERSION_TIME):
        # Initialize and Configure the sun sensor

        # Initialize i2c device from i2c passed in
        self.i2c_device = I2CDevice(i2c_bus, address)

        # Initialize a fixed buffer to read and write from
        self.buf = bytearray(3)

        # DEVICE ID SHOULD BE 0x3001
        self.read_value(DEVICE_ID)
        if self.buf != bytes([DEVICE_ID, 0x30, 0x01]):
            raise Exception("ERROR: Could not read correct device ID from bus provided")

        # MANUFACTURER ID Should be 0x5449
        self.read_value(MANUFACTURER_ID)
        if self.buf != bytes([MANUFACTURER_ID, 0x54, 0x49]):
            raise Exception("ERROR: Could not read correct manufacturer ID from bus provided")

        self.configure(conversion_time)

    # DeInitialize the sun sensor
    def __del__(self):
        # put sensor in low power mode since we are done using it
        # specifically, low power is M[1:0] set to 0b00,
        # but we can just reset everything
        self.buf[1] = 0x00
        self.buf[2] = 0x00
        self.write_value(CONFIGURATION)

        # TODO: is there anything else we should do? is the buffer automatically deallocated?

    # CONFIGURE sun sensor on startup
    # sets conversion time equal to chosen value (800ms or 100ms)
    # currently automatic range setting & continuous conversions
    def configure(self, conversion_time=DEFAULT_CONVERSION_TIME):
        # automatic range setting and continuous conversions.

        # configuration register fields:
        # RN3 RN2 RN1 RN0 CT  M1 M0  OVF
        # CRF FH  FL  L   POL ME FC1 FC0

        # automatically set range RN[3:0] for best results
        # Conversion time (CT) 800ms is 1, 100ms is 0
        # to set continuous conversions: M[1:0] is set to 0b11
        self.buf[1] = (AUTO_RANGE_SETTING << 4) \
                      + ((conversion_time == MAX_CONVERSION_TIME) << 3) \
                      + CONTINUOUS_CONVERSIONS << 1
        self.buf[2] = 0x00
        self.write_value(CONFIGURATION)

        # TODO: Check to make sure all other values in both buf[1] and buf[2] are desirable

        # TODO: Wait for conversion ready flag to be set

    # READ value into last two bytes
    def read_value(self, register):
        # 'with' handles locking and unlocking the i2c
        with self.i2c as i2c:
            self.buf[0] = register
            i2c.write_then_readinto(self.buf, self.buf, out_end=1, in_start=1)
            # partial write so that we are reading from correct register field, (out_end = 1)
            # should automatically be generating a start bit before reading,
            # which is all we need (sending a stop bit is also fine according to opt3001 docs)
            # then read but don't overwrite current register field (in_start = 1)
            i2c.stop()

    # WRITE value from last two bytes
    def write_value(self, register):
        # 'with' handles locking and unlocking the i2c
        with self.i2c as i2c:
            self.buf[0] = register
            i2c.write(self.buf)
            # automatically writes a stop bit

    # CHECK whether sensor measurement is ready
    @property
    def conversion_ready(self):
        # configuration register fields:
        # RN3 RN2 RN1 RN0 CT  M1 M0  OVF
        # CRF FH  FL  L   POL ME FC1 FC0

        self.read_value(self, CONFIGURATION)
        # CRF (conversion ready flag, see registers below)
        # first most significant bit (last most position)
        # in the second value byte equals 1 when ready
        return extract_bits(self.buf[2], len(self.buf[2]) - 1, 1)

    # LUX value of sun-sensor
    # could have delay of 100ms or 800ms
    @property
    def lux(self):
        # wait until the lux measurement is ready
        while not self.conversion_ready:
            time.sleep(0.1)

        # read and process the lux measurement
        self.read_value(self, RESULT)

        # result register fields:
        # E3 E2 E1 E0 R12 R11 R10 R9
        # R8 R7 R6 R5 R4  R3  R2  R1
        # E is exponent, R is mantissa

        # Extract exponent and fractional result from self.buf
        exponent = extract_bits(self.buf[1], 4, 4)  # E[3:0]
        fractional_result = extract_bits(self.buf[1], 0, 4)  # R[12:9]
        fractional_result << 8  # pad in order to add the rest of the mantissa
        fractional_result += self.buf[2]  # R[8:1]

        # Formulas used below are from opt3001 datasheet
        lsb_size = 0.01 * 2 ** exponent
        lux = lsb_size * fractional_result

        return lux
