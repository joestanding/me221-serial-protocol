import unittest
from ME import *

VALID_GETECUINFO = '4d4500000004000408'
VALID_GETHASH_DETAILED = '4d45010000040101060f'
VALID_GETHASH_OVERALL = '4d45010000040100050e'
VALID_REP_SETSTATE_ENABLE = '4d450100000002010305'
VALID_REP_SETSTATE_DISABLE = '4d450100000002000204'
VALID_REP_SEND_ACK = '4d450100000001000102'

class TestECUMessages(unittest.TestCase):

    # ----------------------------------------------------------------------- #
    # System Commands: Creating new messages from scratch                     #
    # ----------------------------------------------------------------------- #

    def test_MEECU_Sys_GetECUInfo_new(self):
        message = MEECU_Sys_GetECUInfo()
        self.assertEqual(message.to_hex(), VALID_GETECUINFO,
            "Sys_GetECUInfo() generated incorrect message!")

    def test_MEECU_Sys_GetHash_detailed_new(self):
        message = MEECU_Sys_GetHash()
        message.set_mode(MEECU_Sys_GetHash.MODE_DETAILED)
        self.assertEqual(message.to_hex(), VALID_GETHASH_DETAILED,
            "Sys_GetHash_detailed() generated incorrect message!")

    def test_MEECU_Sys_GetHash_overall_new(self):
        message = MEECU_Sys_GetHash()
        message.set_mode(MEECU_Sys_GetHash.MODE_OVERALL)
        self.assertEqual(message.to_hex(), VALID_GETHASH_OVERALL,
            "Sys_GetHash_overall() generated incorrect message!")

    # ----------------------------------------------------------------------- #
    # System Commands: Parsing existing messages                              #
    # ----------------------------------------------------------------------- #

    def test_MEECU_Sys_GetECUInfo_parse(self):
        message = MEECU_Message.from_data(VALID_GETECUINFO)
        self.assertEqual(message.__class__, MEECU_Sys_GetECUInfo,
            "Failed to create Sys_GetECUInfo message from valid data!")
        self.assertEqual(message.to_hex(), VALID_GETECUINFO,
            "Parsed Sys_GetECUInfo did not reproduce the same hex!")

    def test_MEECU_Sys_GetHash_detailed_parse(self):
        message = MEECU_Message.from_data(VALID_GETHASH_DETAILED)
        self.assertEqual(message.__class__, MEECU_Sys_GetHash,
            "Failed to create Sys_GetHash message from valid data!")
        self.assertEqual(message.to_hex(), VALID_GETHASH_DETAILED,
            "Parsed GetHash_Detailed did not reproduce the same hex!")

    def test_MEECU_Sys_GetHash_overall_parse(self):
        message = MEECU_Message.from_data(VALID_GETHASH_OVERALL)
        self.assertEqual(message.__class__, MEECU_Sys_GetHash,
            "Failed to create Sys_GetHash message from valid data!")
        self.assertEqual(message.to_hex(), VALID_GETHASH_OVERALL,
            "Parsed GetHash_Detailed did not reproduce the same hex!")

    # ----------------------------------------------------------------------- #
    # Reporting Commands: Creating new messages from scratch                  #
    # ----------------------------------------------------------------------- #

    def test_MEECU_Reporting_SetState_enable_new(self):
        message = MEECU_Reporting_SetState()
        message.set_state(True)
        self.assertEqual(message.to_hex(), VALID_REP_SETSTATE_ENABLE,
            "Reporting_SetState_enable() generated incorrect message!")

    def test_MEECU_Reporting_SetState_disable_new(self):
        message = MEECU_Reporting_SetState()
        message.set_state(False)
        self.assertEqual(message.to_hex(), VALID_REP_SETSTATE_DISABLE,
            "Reporting_SetState_disable() generated incorrect message!")

    def test_MEECU_Reporting_SendAck_new(self):
        message = MEECU_Reporting_SendAck()
        self.assertEqual(message.to_hex(), VALID_REP_SEND_ACK,
            "Reporting_SendAck() generated incorrect message!")

    # ----------------------------------------------------------------------- #
    # Reporting Commands: Parsing existing messages                           #
    # ----------------------------------------------------------------------- #

    def test_MEECU_Reporting_SetState_enable_parse(self):
        message = MEECU_Message.from_data(VALID_REP_SETSTATE_ENABLE)
        self.assertEqual(message.__class__, MEECU_Reporting_SetState,
            "Failed to create Reporting_SetState message from valid data!")
        self.assertEqual(message.to_hex(), VALID_REP_SETSTATE_ENABLE,
            "Parsed Reporting_SetState did not reproduce the same hex!")

    def test_MEECU_Reporting_SetState_disable_parse(self):
        message = MEECU_Message.from_data(VALID_REP_SETSTATE_DISABLE)
        self.assertEqual(message.__class__, MEECU_Reporting_SetState,
            "Failed to create Reporting_SetState message from valid data!")
        self.assertEqual(message.to_hex(), VALID_REP_SETSTATE_DISABLE,
            "Parsed Reporting_SetState did not reproduce the same hex!")

    def test_MEECU_Reporting_SendAck_parse(self):
        message = MEECU_Message.from_data(VALID_REP_SEND_ACK)
        self.assertEqual(message.__class__, MEECU_Reporting_SendAck,
            "Failed to create Reporting_SendAck message from valid data!")
        self.assertEqual(message.to_hex(), VALID_REP_SEND_ACK,
            "Parsed Reporting_SendAck did not reproduce the same hex!")


if __name__ == '__main__':
    unittest.main()

