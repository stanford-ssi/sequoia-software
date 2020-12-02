from adafruit_bus_device import i2c_device

# Can be one of four possible values
# This assumes we connect the ADDR pin to GND
# See 8.3.4.1 in the specification
DEVICE_DEFAULT_I2C_ADDR = 0x44

# MAIN REGISTERS FOR PROGRAMMING DEVICE
RESULT = 0x00
CONFIGURATION = 0x1

# FOR INTERRUPT MECHANISMS, UNUSED
LOW_LIMIT = 0x2
HIGH_LIMIT = 0x3

# CAN BE READ TO GET ID
MANUFACTURER_ID = 0x7E
DEVICE_ID = 0x7F

REGISTER_SIZE = 2


class Opt3001:
    """TODO: A better class description"""




    def __init__(self, i2c, address=DEVICE_DEFAULT_I2C_ADDR):
        # TODO: A better method description
        # Initialize i2c device from i2c passed in
        self.i2c = i2c_device.I2CDevice(i2c, address)
        # Initialize a fixed buffer to read and write from
        self.buf = bytearray(3)
        # DEVICE ID SHOULD BE 0x3001
        # Manufacturer ID should be 0x5449

        # Check device id (should be 0x3001)
        self.read_value(DEVICE_ID)
        if self.buf != bytes([0x30, 0x01]):
            raise Exception("ERROR: Could not read correct device ID from bus provided!")

        # TODO: Check manufacturer ID. Should be 0x5449

        self.configure()

    # Configure sun sensor on startup
    def configure(self):
        # TODO: These should be the correct values for the configuration we want
        # We probably want automatic range setting
        # and continuous conversions.
        self.buf[1] = 0x00
        self.buf[2] = 0x00
        self.write_value(CONFIGURATION)

        # TODO: Wait for conversion ready flag to be set

    # Writes value into self.buf[1:2]
    def read_value(self, register):
        with self.i2c as i2c:
            self.buf[0] = register
            i2c.write_then_readinto(self.buf, in_end = 1, out_start = 1)
        return self.buf[0]

    # Assumes Value is stored in the last two bytes of self.buf
    def write_value(self, register):
        with self.i2c as i2c:
            self.buf[0] = register
            # Not sure this is the right, we might need to send a stop bit
            # call i2c.write twice
            i2c.write(self.buf)

    @property
    def lux(self):
        # TODO: Wait for conversion ready bit?
        self.read_value(self, RESULT)
        # TODO: extract exponent and fractional result from self.buf
        exponent = 0
        fractional_result = 0
        lsb_size = 0.01 * 2**exponent
        lux = lsb_size * fractional_result
        return lux
