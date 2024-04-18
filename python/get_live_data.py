#!/usr/bin/env python3
from ME import *
import serial
import time
import struct
from serial.serialutil import SerialException

# --------------------------------------------------------------------------- #

def main():
    entity_map = None

    conn = MEECU_Connection('/dev/ttyUSB0', 115200)
    if conn.connect():
        print("Connected to ECU successfully!")
    else:
        print("Failed to connect to ECU!")
        return

    # Get ECU Info
    response = conn.send_message(MEECU_Sys_GetECUInfo())
    print(response)

    # Get Hash Table
    message = MEECU_Sys_GetHash()
    message.set_mode(MEECU_Sys_GetHash.MODE_DETAILED)
    response = conn.send_message(message)
    print(response)

    # Set Reporting State
    message = MEECU_Reporting_SetState()
    message.set_state(True)
    response = conn.send_message(message)
    print(response)
    if response is not None:
        print(f"Received info on {len(response.entities)} entities")
        entity_map = response.entities

    # Receive Reports
    while(True):
        rx_bytes = conn.receive_message()
        if rx_bytes is not None:
            message = MEECU_Message.from_data(rx_bytes)
            message.parse_report(entity_map)

            for entity in message.entities:
                if entity['id'] == 1:
                    print(f"RPM:           {entity['value']}")

                if entity['id'] == 14:
                    print(f"Coolant Temp.: {entity['value']}")


            # Send an ack or it'll eventually stop sending us data
            conn.send_message(MEECU_Reporting_SendAck())

# --------------------------------------------------------------------------- #

if __name__ == '__main__':
    main()
