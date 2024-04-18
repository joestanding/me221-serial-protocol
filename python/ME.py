from enum import Enum, auto
import serial
from serial.serialutil import SerialException
import time
import struct

# --------------------------------------------------------------------------- #
# Protocol Enums                                                              #
# --------------------------------------------------------------------------- #

class MEECU_ReportingType(Enum):
    FLOAT_4B = (0x00, 4, 'Float (4 Bytes)')
    INT_2B   = (0x01, 2, 'Signed Integer (2 Bytes)')
    UINT_2B  = (0x02, 2, 'Unsigned Integer (2 Bytes)')
    INT_1B   = (0x03, 1, 'Signed Integer (1 Byte)')
    UINT_1B  = (0x04, 1, 'Unsigned Integer (1 Byte)')
    BOOL_1B  = (0x05, 1, 'Boolean (1 Byte)')

    def __new__(cls, value, length, desc):
        obj = object.__new__(cls)
        obj._value_ = value
        obj._length = length
        obj.desc = desc
        return obj

# --------------------------------------------------------------------------- #

class MEECU_MessageType(Enum):
    REQUEST  = (0x00, 'Request')
    RESPONSE = (0x0F, 'Response')

    def __new__(cls, value, desc):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.desc = desc
        return obj

# --------------------------------------------------------------------------- #

class MEECU_MessageClass(Enum):
    REPORTING = (0x00, 'Reporting')
    TABLES    = (0x01, 'Tables')
    DRIVERS   = (0x02, 'Drivers')
    DATALINKS = (0x03, 'Datalinks')
    SYSTEM    = (0x04, 'System')
    FWUPDATE  = (0x05, 'Firmware Update')
    DATALOG   = (0x06, 'Data Log')
    TRIGLOG   = (0x07, 'Trigger Log')
    DBW       = (0x08, 'DBW')

    def __new__(cls, value, desc):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.desc = desc
        return obj

# --------------------------------------------------------------------------- #

class MEECU_SysCommands(Enum):
    GET_ECU_INFO     = (0x00, 'Get ECU Info')
    GET_HASH         = (0x01, 'Get Hash')
    SET_RTC          = (0x02, 'Set RTC')
    FACTORY_RESET    = (0x03, 'Factory Reset')
    PWLOCK_SET_STATE = (0x04, 'PWLock Set State')
    PWLOCK_GET_STATE = (0x05, 'PWLock Get State')
    RACE_UNLOCK      = (0x06, 'Race Unlock')

    def __new__(cls, value, desc):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.desc = desc
        return obj

# --------------------------------------------------------------------------- #

class MEECU_ReportingCommands(Enum):
    SEND_REPORT     = (0x00, 'Send Report')
    SEND_ACK        = (0x01, 'Send Ack')
    SET_STATE       = (0x02, 'Set State')
    SET_SPECIAL_CFG = (0x03, 'Set Special Config.')

    def __new__(cls, value, desc):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.desc = desc
        return obj

# --------------------------------------------------------------------------- #

class_to_command_enum = {
    MEECU_MessageClass.REPORTING: MEECU_ReportingCommands,
    MEECU_MessageClass.SYSTEM: MEECU_SysCommands
}

# --------------------------------------------------------------------------- #
# ECU Base Message Class                                                      #
# --------------------------------------------------------------------------- #

class MEECU_Message:

    _subclasses = []

    data    = None
    length  = None
    rtype   = None
    rclass  = None
    command = None
    payload = b''
    crc     = None

    # ----------------------------------------------------------------------- #

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        MEECU_Message._subclasses.append(cls)

    # ----------------------------------------------------------------------- #

    def __init__(self, data=None):
        # We can accept either bytes or a hex string, which we'll convert
        if isinstance(data, bytes):
            self.data = data
        if isinstance(data, str):
            self.data = self._convert_hex_str(data)

        # If we were provided a message to parse, do so now
        if self.data is not None:
            self._parse()

    # ----------------------------------------------------------------------- #

    @classmethod
    def from_data(cls, data):
        if isinstance(data, str):
            data = bytes.fromhex(data)

        if data[:2] != b'ME':
            print("Message does not start with magic bytes 'ME', malformed!")

        _, length, rtype_int, rclass_int, command_int = \
            struct.unpack('<2sHBBB', data[:7])

        rtype = next((m for m in MEECU_MessageType.__members__.values() if m.value == rtype_int), None)
        rclass = next((m for m in MEECU_MessageClass.__members__.values() if m.value == rclass_int), None)

        command_enum = class_to_command_enum.get(rclass, None)
        if command_enum:
            command = next((cmd for cmd in command_enum.__members__.values() if cmd.value == command_int), None)
        else:
            command = None
            print(f"Warning: No command enum mapping for message class {self.rclass}")

        for subclass in cls._subclasses:
            if hasattr(subclass, 'CLASS') and hasattr(subclass, 'COMMAND'):
                if subclass.CLASS.value == rclass_int and \
                   subclass.COMMAND.value == command_int:
                       return subclass(data)

        # ----------------------------------------------------------------------- #

    def _parse(self):

        if self.data[:2] != b'ME':
            print("Message does not start with magic bytes 'ME', malformed!")

        _, self.length, rtype_int, rclass_int, command_int = \
            struct.unpack('<2sHBBB', self.data[:7])

        self.rtype = next((m for m in MEECU_MessageType.__members__.values() if m.value == rtype_int), None)
        self.rclass = next((m for m in MEECU_MessageClass.__members__.values() if m.value == rclass_int), None)

        command_enum = class_to_command_enum.get(self.rclass, None)
        if command_enum:
            self.command = next((cmd for cmd in command_enum.__members__.values() if cmd.value == command_int), None)
        else:
            self.command = None
            print(f"Warning: No command enum mapping for message class {self.rclass}")

        payload_end = 7 + self.length
        self.payload = self.data[7:payload_end]

        if hasattr(self, '_process_payload'):
            self._process_payload()

        self._calc_crc()

    # ----------------------------------------------------------------------- #

    def _convert_hex_str(self, data_str):
        try:
            return bytes.fromhex(data_str)
        except ValueError as err:
            print("Provided string was not a valid hex string!")
            return False

    # ----------------------------------------------------------------------- #

    def _calc_crc(self):
        data = bytes([self.rtype.value,
                      self.rclass.value,
                      self.command.value]) + self.payload

        num = 0
        num2 = 0
        for byte in data:
            num = (num + byte) % 255
            num2 = (num2 + num) % 255
        self.crc = (num2 << 8) | num

    # ----------------------------------------------------------------------- #

    def __str__(self):
        return f"{self.__class__.__name__}(type: {self.rtype.desc}, " \
               f"class: {self.rclass.desc}, " \
               f"command: {self.command.desc}, " \
               f"len: {self.length})"

    # ----------------------------------------------------------------------- #

    def to_bytes(self):
        self._calc_crc()

        magic_bytes = b'ME'
        if self.payload is None:
            self.payload = b''

        length = len(self.payload)

        if self.crc is None:
            self._calc_crc()

        header = struct.pack('<2sHBBB', magic_bytes, length, self.rtype.value,
                             self.rclass.value, self.command.value)
        message = header + self.payload + self.crc.to_bytes(2,
                                                            byteorder='little')

        return message

    # ----------------------------------------------------------------------- #

    def to_hex(self):
        return self.to_bytes().hex()

# =========================================================================== #
# System Commands                                                             #
# =========================================================================== #

class MEECU_Sys_GetECUInfo(MEECU_Message):

    CLASS   = MEECU_MessageClass.SYSTEM
    COMMAND = MEECU_SysCommands.GET_ECU_INFO

    def __init__(self, data=None):
        super().__init__(data)

        if data is None:
            self.rtype = MEECU_MessageType.REQUEST
            self.rclass = self.CLASS
            self.command = self.COMMAND
            self._calc_crc()

# --------------------------------------------------------------------------- #

class MEECU_Sys_GetHash(MEECU_Message):

    CLASS   = MEECU_MessageClass.SYSTEM
    COMMAND = MEECU_SysCommands.GET_HASH

    MODE_OVERALL  = 0x00
    MODE_DETAILED = 0x01

    def __init__(self, data=None):
        super().__init__(data)

        if data is None:
            self.rtype = MEECU_MessageType.REQUEST
            self.rclass = MEECU_MessageClass.SYSTEM
            self.command = MEECU_SysCommands.GET_HASH
            self._calc_crc()

    def set_mode(self, mode):
        self.payload = mode.to_bytes(1, 'little')

# =========================================================================== #
# Reporting Commands                                                          #
# =========================================================================== #

class MEECU_Reporting_SetState(MEECU_Message):

    CLASS   = MEECU_MessageClass.REPORTING
    COMMAND = MEECU_ReportingCommands.SET_STATE

    REPORTING_V1 = 0x01
    REPORTING_V2 = 0x02


    def __init__(self, data=None):
        self.entities = []
        self.version = 0
        self.link_count = 0
        super().__init__(data)

        if data is None:
            self.rtype = MEECU_MessageType.REQUEST
            self.rclass = MEECU_MessageClass.REPORTING
            self.command = MEECU_ReportingCommands.SET_STATE
            self._calc_crc()


    def set_state(self, state):
        if state:
            self.payload = b'\x01'
        else:
            self.payload = b'\x00'


    def _process_payload(self):
        if self.rtype != MEECU_MessageType.RESPONSE:
            return

        if len(self.payload) == 1:
            self.version = self.REPORTING_V1
        else:
            self.version = self.REPORTING_V2

        self.link_count, = struct.unpack_from('<H', self.payload, 1)
        offset = 3
        for _ in range(self.link_count):
            entity_id, = struct.unpack_from('<H', self.payload, offset)
            offset += 2
            entity_type, = struct.unpack_from('B', self.payload, offset)
            offset += 1
            self.entities.append({
                'id': entity_id,
                'type': entity_type
            })

# --------------------------------------------------------------------------- #

class MEECU_Reporting_SendAck(MEECU_Message):

    CLASS   = MEECU_MessageClass.REPORTING
    COMMAND = MEECU_ReportingCommands.SEND_ACK

    def __init__(self, data=None):
        super().__init__(data)
        self.rtype = MEECU_MessageType.REQUEST
        self.rclass = MEECU_MessageClass.REPORTING
        self.command = MEECU_ReportingCommands.SEND_ACK
        self.payload = b'\x00'
        self._calc_crc()

# --------------------------------------------------------------------------- #

class MEECU_Reporting_SendReport(MEECU_Message):

    CLASS   = MEECU_MessageClass.REPORTING
    COMMAND = MEECU_ReportingCommands.SEND_REPORT

    def __init__(self, data=None):
        self.entities = []
        super().__init__(data)

        if data is None:
            self.rtype = MEECU_MessageType.REQUEST
            self.rclass = MEECU_MessageClass.REPORTING
            self.command = MEECU_ReportingCommands.SEND_REPORT
            self.payload = b'\x00'

    def parse_report(self, entities):
        offset = 1
        for entity in entities:

            etype = next((m for m in MEECU_ReportingType.__members__.values() if m.value == entity['type']), None)

            value_format = {
                MEECU_ReportingType.FLOAT_4B: ('f', 4),
                MEECU_ReportingType.INT_2B: ('h', 2),
                MEECU_ReportingType.UINT_2B: ('H', 2),
                MEECU_ReportingType.INT_1B: ('b', 1),
                MEECU_ReportingType.UINT_1B: ('B', 1),
                MEECU_ReportingType.BOOL_1B: ('?', 1),
            }[etype]

            format_string, _ = value_format
            value, = struct.unpack_from(format_string, self.payload, offset)
            self.entities.append({
                'id': entity['id'],
                'type': entity['type'],
                'value': value
            })
            offset += etype._length

# --------------------------------------------------------------------------- #
# Serial Interface                                                            #
# --------------------------------------------------------------------------- #

class MEECU_Connection:
    device_path = None
    baud_rate   = None
    handle      = None


    def __init__(self, device_path, baud_rate):
        self.device_path = device_path
        self.baud_rate = baud_rate


    def connect(self):
        try:
            self.handle = serial.Serial(self.device_path, self.baud_rate)
        except SerialException as err:
            print(f"Exception when connecting: {err}")
            return False

        if not self.handle.is_open:
            print("Failed to open serial port!")
            return False

        return True


    def send_message(self, message, recv=True):
        self.handle.write(message.to_bytes())
        time.sleep(0.1)

        if recv:
            rx = self.receive_message()
            if rx is not None:
                return MEECU_Message.from_data(rx)
            else:
                return None


    def receive_message(self):
        buffer = b''

        if self.handle.in_waiting > 0:
            buffer = self.handle.read(7)
            _, hlen, htype, hclass, hcmd = struct.unpack('<2sHBBB', buffer)
            buffer += self.handle.read(hlen + 2)
            return buffer
        else:
            return None
