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
    """A sun sensor!"""




    def __init__(self, i2c, address=DEVICE_DEFAULT_I2C_ADDR):
        self.i2c = i2c_device.I2CDevice(i2c, address)
        self.buf = bytearray(3)
        # DEVICE ID SHOULD BE 0x3001
        if (
            self.read_value(DEVICE_ID) != 0x3001
            or self.read_value(MANUFACTURER_ID) != 0x5449
        ):
            raise Exception(
                "ERROR: Could not read correct device ID from bus provided!"
            )

        # Start comparison

    # Configure sun sensor on startup
    def configure(self):
        # Automatically choose lux range of device (bits 15 - 12)
        self.write_value(CONFIGURATION, 0x1100, 12, 3)
        # 100ms or 800ms conversion time
        self.write_value(CONFIGURATION, 0x1, 11)
        # Continously be doing conversions (i.e. start the thing)
        self.write_value(CONFIGURATION, 0x2, 9, 2)

    def read_value(self, register):
        # With statement automatically locks and unlocks
        # I2C device
        with self.i2c as i2c:
            self.buf[0] = register
            i2c.write_then_readinto(self.buf)
        return self.buf[0]
        # with self.i2c_device as i2c:
        #     i2c.writeto(b"0x00")
        #     i2c.readfrom_into(self.buf)
        # return self.buf[0]

    def write_value(self, register, value):
        with self.i2c as i2c:
            self.buf[0] = register
            self.buf[1:2] = value
            i2c.write(self.buf[1:2])

    @property
    def lux(self):
        exponent = self.read_value(self, RESULT, 12, 3)
        fractional_result = self.read_value(self, RESULT, 0, 11)
        lsb_size = 0.01 * 2**exponent
        lux = lsb_size * fractional_result
        return lux
