#include "me.h"
#include <cassert>

int main(int argc, char * argv[]) {

    char raw_buf[512];
    uint32_t len;

    MEMessage * message = MEMessage::create(ME_TYPE_REQUEST,
                                            ME_CLASS_SYS,
                                            ME_CMD_SYS_GET_ECU_INFO,
                                            (char*)"", 0);

    memset(raw_buf, 0, sizeof(raw_buf));
    message->to_bytes((char*)&raw_buf, &len);
    assert(message != NULL);
    assert(message->type == ME_TYPE_REQUEST);
    assert(message->cls == ME_CLASS_SYS);
    assert(message->command == ME_CMD_SYS_GET_ECU_INFO);
    assert(message->length == 0);
    assert(message->crc == 0x0804);

    message = MEMessage::create(ME_TYPE_REQUEST,
                                ME_CLASS_SYS,
                                ME_CMD_SYS_GET_HASH,
                                (char*)"\x01", 1);
    memset(raw_buf, 0, sizeof(raw_buf));
    message->to_bytes((char*)&raw_buf, &len);
    assert(message != NULL);
    assert(message->type == ME_TYPE_REQUEST);
    assert(message->cls == ME_CLASS_SYS);
    assert(message->command == ME_CMD_SYS_GET_HASH);
    assert(message->length == 1);
    assert(message->crc == 0x0f06);

    message = MEMessage::create(ME_TYPE_REQUEST,
                                ME_CLASS_REPORTING,
                                ME_CMD_REP_SET_STATE,
                                (char*)"\x01", 1);
    memset(raw_buf, 0, sizeof(raw_buf));
    message->to_bytes((char*)&raw_buf, &len);
    assert(message != NULL);
    assert(message->type == ME_TYPE_REQUEST);
    assert(message->cls == ME_CLASS_REPORTING);
    assert(message->command == ME_CMD_REP_SET_STATE);
    assert(message->length == 1);
    assert(message->crc == 0x0503);

    message = MEMessage::create(ME_TYPE_REQUEST,
                                ME_CLASS_REPORTING,
                                ME_CMD_REP_SEND_ACK,
                                (char*)"\x00", 1);
    memset(raw_buf, 0, sizeof(raw_buf));
    message->to_bytes((char*)&raw_buf, &len);
    assert(message != NULL);
    assert(message->type == ME_TYPE_REQUEST);
    assert(message->cls == ME_CLASS_REPORTING);
    assert(message->command == ME_CMD_REP_SEND_ACK);
    assert(message->length == 1);
    assert(message->crc == 0x0201);


    printf("\nAll tests OK!\n\n");

    return 0;
}
