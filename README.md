# ME221 Serial Protocol Format
This repository contains analysis and tooling for the serial protocol supported by the Motorsport Electronics series of automotive ECUs. The analysis and testing was performed against an ME221.

The serial protocol is used by the official tuning software, MEITE, to read information from the vehicle and configure its settings. It features a reporting function that sends all available diagnostic information and sensor readings to the connected device at high speed, and is useful for data logging and displaying with an external device.
## Protocol Format

| Field       | Size                         | Type       | Purpose                                                                               |
| ----------- | ---------------------------- | ---------- | ------------------------------------------------------------------------------------- |
| Magic Bytes | 2 bytes                      | `char[2]`  | All messages begin with `ME`.                                                         |
| Length      | 2 bytes                      | `ushort`   | Length of the `payload` field and CRC.                                                |
| Type        | 1 byte                       | `uchar`    | `0x00` if request, `0x0F` if response                                                 |
| Class       | 1 byte                       | `uchar`    | High-level category for the command (e.g. reporting, firmware update)                 |
| Command     | 1 byte                       | `uchar`    | The operation to be executed by the ECU. Documented later on.                         |
| Payload     | As defined by "Length" field | `char[]`   | A payload relevant to the command to be executed.                                     |
| CRC         | 2 bytes                      | `uint16_t` | Used to validate the integrity of the payload and all header values after the length. |
### Example Request Break-down

Sent data (from MEITE to ECU):
`    4d 45 00 00 00 04 00 04 08                        ME.......        

| Field       | Value (Hex) | **Meaning**    |
| ----------- | ----------- | -------------- |
| Magic Bytes | `4d 5d`     | 'ME'           |
| Length      | `00 00`     | 0 (no payload) |
| Type        | `00`        | Request        |
| Class       | `04`        | Sys            |
| Command     | `00`        | Get ECU Info   |
| CRC         | `04 08`     |                |

### Header Field Values

#### Type IDs
The type field indicates whether the message is a request to, or a response from, the ECU. No other types appear to be supported.

| **ID** | **Type**                   |
| ------ | -------------------------- |
| `0x00` | Request (to the ECU)       |
| `0x0F` | Response (from to the ECU) |

#### Class IDs
The class denotes the high-level category for the command. A unique command is identified through combination of both the class field and the command field.

| ID     | Class           |     |
| ------ | --------------- | --- |
| `0x00` | Reporting       |     |
| `0x01` | Tables          |     |
| `0x02` | Drivers         |     |
| `0x03` | DataLinks       |     |
| `0x04` | Sys             |     |
| `0x05` | Firmware Update |     |
| `0x06` | DataLog         |     |
| `0x07` | TriggerLogger   |     |
| `0x08` | DBW             |     |

#### Reporting Commands

| ID  | Command                   | Payload                                         |
| --- | ------------------------- | ----------------------------------------------- |
| 0   | Send Report               |                                                 |
| 1   | Send Ack                  | Appeared to be `00` in all examples I observed. |
| 2   | Set State                 | `00` to disable reporting, `01` to enable it.   |
| 3   | Set Special Configuration |                                                 |
#### Tables Commands

| ID  | Command                      |
| --- | ---------------------------- |
| 0   | Set Table                    |
| 1   | Get Table                    |
| 2   | Enable Table                 |
| 3   | Disable Table                |
| 4   | Set Data At Offsets          |
| 5   | Get Data At Offset           |
| 6   | Store in Non-volatile Memory |
| 7   | Set Table Reporting          |
#### Drivers Commands

| ID  | Command                      |
| --- | ---------------------------- |
| 0   | Set Driver                   |
| 1   | Get Driver                   |
| 2   | Store in Non-volatile Memory |
#### Sys Commands

| ID  | Command           |
| --- | ----------------- |
| 0   | Get ECU Info      |
| 1   | Get Hash          |
| 2   | Set RTC           |
| 3   | Factory Reset     |
| 4   | PW Lock Set State |
| 5   | PW Lock Get State |
| 6   | Race Unlock       |

#### Firmware Update Commands

| ID  | Command               |
| --- | --------------------- |
| 0   | Start Firmware Update |
| 1   | Region Info Get       |
| 2   | Data Get              |
| 3   | Status Report         |
| 4   | Enter BL Mode         |

#### Drivers Commands

| ID  | Command                      |
| --- | ---------------------------- |
| 0   | Set Driver                   |
| 1   | Get Driver                   |
| 2   | Store in Non-volatile Memory |
#### DataLog Commands

| ID  | Command        |
| --- | -------------- |
| 0   | Is Supported   |
| 1   | Get Config     |
| 2   | Set Config     |
| 3   | Start          |
| 4   | Stop           |
| 5   | Get Logs       |
| 6   | Get Log Detail |
| 7   | Get Log Region |
| 8   | Erase Log      |
| 9   | Format Memory  |

#### TriggerLogger Commands

| ID  | Command      |
| --- | ------------ |
| 0   | Is Supported |
| 1   | Set State    |
| 2   | Report       |
#### DBW Commands

| ID  | Command      |
| --- | ------------ |
| 0   | Set DBW Duty |

