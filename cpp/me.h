#include <stdio.h>
#include <stddef.h>
#include <stdint.h>
#include <iostream>
#include <memory>
#include <cstring>

/* ------------------------------------------------------------------------- */
/* Defines                                                                   */
/* ------------------------------------------------------------------------- */

#define ME_HEADER_LENGTH 7
#define ME_CRC_LENGTH    2
#define ME_MAX_ENTITIES  256
#define ME_LENGTH_OFFSET 4
#define ME_TYPE_LEN      1
#define ME_CLASS_LEN     1
#define ME_COMMAND_LEN   1

#define ME_TYPE_REQUEST    0x00
#define ME_TYPE_RESPONSE   0x0F

#define ME_CLASS_REPORTING 0x00
#define ME_CLASS_TABLES    0x01
#define ME_CLASS_DRIVERS   0x02
#define ME_CLASS_DATALINKS 0x03
#define ME_CLASS_SYS       0x04
#define ME_CLASS_FWUPDATE  0x05
#define ME_CLASS_DATALOG   0x06
#define ME_CLASS_TRIGLOG   0x07
#define ME_CLASS_DBW       0x08

#define ME_CMD_REP_SEND_REPORT  0x00
#define ME_CMD_REP_SEND_ACK     0x01
#define ME_CMD_REP_SET_STATE    0x02
#define ME_CMD_REP_SET_SPEC_CFG 0x03

#define ME_CMD_SYS_GET_ECU_INFO 0x00
#define ME_CMD_SYS_GET_HASH     0x01
#define ME_CMD_SYS_SET_RTC      0x02
#define ME_CMD_SYS_RESET        0x03
#define ME_CMD_SYS_PWLOCK_SET   0x04
#define ME_CMD_SYS_PWLOCK_GET   0x05
#define ME_CMD_SYS_RACE_UNLOCK  0x06

#define ME_DATA_FLOAT_4B 0x00
#define ME_DATA_INT_2B   0x01
#define ME_DATA_UINT_2B  0x02
#define ME_DATA_INT_1B   0x03
#define ME_DATA_UINT_1B  0x04
#define ME_DATA_BOOL_1B  0x05

#define ME_VALIDATE_OK    0
#define ME_VALIDATE_MB    -1
#define ME_VALIDATE_TYPE  -2
#define ME_VALIDATE_CLASS -3
#define ME_VALIDATE_CRC   -4

/* ------------------------------------------------------------------------- */
/* Macros                                                                    */
/* ------------------------------------------------------------------------- */

#define SWAP_U16(x) (((x) >> 8) | ((x) << 8))

/* ------------------------------------------------------------------------- */
/* Structs                                                                   */
/* ------------------------------------------------------------------------- */

typedef struct {
    char     magic_bytes[2]; /* Always set to 'ME' */
    uint16_t length;         /* Length of the payload field (not inc. CRC */
    uint8_t  type;           /* Whether this is a request or response */
    uint8_t  cls;          /* Category of the command */
    uint8_t  command;        /* The specific command to execute/executed */
} __attribute__((packed)) me_header_t;

typedef struct {
    uint16_t id;
    uint8_t  type;
} __attribute__((packed)) me_entity_t;

typedef struct {
    uint16_t id;
    uint8_t  type;
    uint32_t value;
} __attribute__((packed)) me_value_t;

/* ------------------------------------------------------------------------- */

class MEMessage {
    public:
        MEMessage();
        virtual ~MEMessage() {}

        static int validate(me_header_t * header);
        static uint16_t calc_crc(const char * data, uint32_t length);
        static MEMessage * get_class(uint16_t cls, uint16_t command);
        static MEMessage * from_bytes(const char * buffer, uint32_t length);
        static MEMessage * create(uint16_t type, uint16_t cls,
                                  uint16_t command, char * payload,
                                  uint16_t length);

        void to_bytes(char * buffer, uint32_t * length);
        void print();

        uint8_t  type;
        uint8_t  cls;
        uint8_t  command;
        uint16_t length;
        char *   payload;
        uint16_t crc;
};

/* ------------------------------------------------------------------------- */

class MERepSetState : public MEMessage {
    public:
        virtual ~MERepSetState() {}
        int parse_response(uint16_t * count, me_entity_t * map);
};

class MERepSendReport : public MEMessage {
    public:
        virtual ~MERepSendReport() {}
        int parse_response(uint16_t count, me_entity_t * map,
                           me_value_t * values);
};

class MERepSendAck : public MEMessage {
    public:
        virtual ~MERepSendAck() {}
};

/* ------------------------------------------------------------------------- */

class MESysGetECUInfo: public MEMessage {
    public:
        virtual ~MESysGetECUInfo() {}
};

class MESysGetHash: public MEMessage {
    public:
        virtual ~MESysGetHash() {}
};

/* ------------------------------------------------------------------------- */
