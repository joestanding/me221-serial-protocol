#include "me.h"

/* ------------------------------------------------------------------------- */
/* MEMessage: Constructor/Destructor                                         */
/* ------------------------------------------------------------------------- */

MEMessage::MEMessage() {
    this->type    = 0;
    this->cls     = 0;
    this->command = 0;
    this->length  = 0;
}

/* ------------------------------------------------------------------------- */
/* MEMessage: Static Methods                                                 */
/* ------------------------------------------------------------------------- */

int MEMessage::validate(me_header_t * header) {
    if(header->magic_bytes[0] != 'M' || header->magic_bytes[1] != 'E')
        return ME_VALIDATE_MB;

    if(header->type != ME_TYPE_REQUEST && header->type != ME_TYPE_RESPONSE)
        return ME_VALIDATE_TYPE;

    if(!(header->cls >= ME_CLASS_REPORTING && header->cls <= ME_CLASS_DBW))
        return ME_VALIDATE_CLASS;

    uint16_t crc1 = *reinterpret_cast<const uint16_t*>((char*)header +
                                                       sizeof(me_header_t) +
                                                       header->length - 1);
    uint16_t crc2 = MEMessage::calc_crc((char*)header + 4, header->length + 3);

    if(crc1 != crc2)
        return ME_VALIDATE_CRC;

    return ME_VALIDATE_OK;
}

/* ------------------------------------------------------------------------- */

uint16_t MEMessage::calc_crc(const char * data, uint32_t length) {
    uint16_t crc = 0;
    uint8_t num = 0;
    uint8_t num2 = 0;
    for (uint32_t i = 0; i < length; ++i) {
        num = (num + data[i]) % 255;
        num2 = (num2 + num) % 255;
    }
    crc = (num2 << 8) | num;
    return crc;
}

/* ------------------------------------------------------------------------- */

MEMessage * MEMessage::get_class(uint16_t cls, uint16_t command) {
    MEMessage * message = NULL;

    if(cls == ME_CLASS_SYS) {
        if(command == ME_CMD_SYS_GET_ECU_INFO)
            message = new MESysGetECUInfo();
        if(command == ME_CMD_SYS_GET_HASH)
            message = new MESysGetHash();

    }

    if(cls == ME_CLASS_REPORTING) {
        if(command == ME_CMD_REP_SET_STATE)
            message = new MERepSetState();
        if(command == ME_CMD_REP_SEND_REPORT)
            message = new MERepSendReport();
        if(command == ME_CMD_REP_SEND_ACK)
            message = new MERepSendAck();
    }

    return message;
}

/* ------------------------------------------------------------------------- */

MEMessage * MEMessage::from_bytes(const char * buffer, uint32_t length) {
    me_header_t * header = (me_header_t*)buffer;

    int validation_result = MEMessage::validate(header);
    if(!validation_result) {
        printf("MEMessage::from_bytes(): Message failed validation! Err: ");
        switch(validation_result) {
            case ME_VALIDATE_MB:
                printf("Magic Bytes\n");
                break;
            case ME_VALIDATE_TYPE:
                printf("Type\n");
                break;
            case ME_VALIDATE_CLASS:
                printf("Class\n");
                break;
            case ME_VALIDATE_CRC:
                printf("CRC\n");
                break;
            default:
                printf("Unknown\n");
                break;
        return NULL;
        }
    }

    uint16_t crc = *reinterpret_cast<const uint16_t*>(buffer +
                                                      sizeof(me_header_t*) +
                                                      header->length - 1);

    MEMessage * message = MEMessage::get_class(header->cls, header->command);
    message->type = header->type;
    message->cls = header->cls;
    message->command = header->command;
    message->length = header->length;

    uint32_t payload_length = length - sizeof(me_header_t) - ME_CRC_LENGTH;
    message->payload = new char[payload_length];
    memset(message->payload, 0, payload_length);
    memcpy(message->payload, buffer + sizeof(me_header_t), payload_length);

    message->crc = crc;

    return message;
}

/* ------------------------------------------------------------------------- */

MEMessage * MEMessage::create(uint16_t type, uint16_t cls, uint16_t command,
                              char * payload, uint16_t length) {
    MEMessage * message = MEMessage::get_class(cls, command);

    if(message == NULL)
        return NULL;

    message->type    = type;
    message->cls     = cls;
    message->command = command;
    message->payload = payload;
    message->length  = length;

    return message;
}

/* ------------------------------------------------------------------------- */
/* MEMessage: Regular Methods                                                */
/* ------------------------------------------------------------------------- */

void MEMessage::to_bytes(char * buffer, uint32_t * length) {
    uint32_t index = 0;

    buffer[index++] = 'M';
    buffer[index++] = 'E';

    buffer[index++] = static_cast<char>(this->length & 0xFF);
    buffer[index++] = static_cast<char>((this->length >> 8) & 0xFF);

    buffer[index++] = static_cast<char>(this->type);
    buffer[index++] = static_cast<char>(this->cls);
    buffer[index++] = static_cast<char>(this->command);

    if(this->payload != nullptr && this->length > 0) {
        memcpy(buffer + index, this->payload, this->length);
        index += this->length;
    }

    this->crc = MEMessage::calc_crc(buffer + 4, this->length + 3);

    buffer[index++] = static_cast<char>(crc & 0xFF);
    buffer[index++] = static_cast<char>((crc >> 8) & 0xFF);

    *length = index;
}

/* ------------------------------------------------------------------------- */

void MEMessage::print() {
    printf("ME Message\n");
    printf("type:    0x%02x\n", this->type);
    printf("cls:     0x%02x\n", this->cls);
    printf("command: 0x%02x\n", this->command);
    printf("length:  0x%02x\n", this->length);
    printf("crc:     0x%02x\n", this->crc);
}

/* ------------------------------------------------------------------------- */
/* Reporting Commands                                                        */
/* ------------------------------------------------------------------------- */

int MERepSetState::parse_response(uint16_t * count, me_entity_t * map) {
    *count = *((uint16_t*)(this->payload + 1));

    char * data = this->payload + 3;
    me_entity_t * map_entity = (me_entity_t*)map;

    for(int i = 0; i < *count; i++) {
        me_entity_t * entity = (me_entity_t*)data;

        map_entity->id = entity->id;
        map_entity->type = entity->type;

        map_entity++;
        data = ((char*)data + sizeof(me_entity_t));
    }

    return 1;
}

/* ------------------------------------------------------------------------- */

int MERepSendReport::parse_response(uint16_t count, me_entity_t * map,
                                    me_value_t * values) {
    if(this->type != ME_TYPE_RESPONSE)
        return 0;

    char * payload = this->payload + 1;
    me_entity_t * curr_entity = (me_entity_t*)map;
    for(int i = 0; i < count; i++) {
        values->id = curr_entity->id;
        values->type = curr_entity->type;

        switch(curr_entity->type) {
            case ME_DATA_FLOAT_4B:
                values->value = (int32_t)*payload;
                payload += 4;
                break;
            case ME_DATA_INT_2B:
                values->value = (int16_t)*payload;
                payload += 2;
                break;
            case ME_DATA_UINT_2B:
                values->value = (uint16_t)*payload;
                payload += 2;
                break;
            case ME_DATA_INT_1B:
                values->value = (char)*payload;
                payload += 1;
                break;
            case ME_DATA_UINT_1B:
                values->value = (unsigned char)*payload;
                payload += 1;
                break;
            case ME_DATA_BOOL_1B:
                values->value = (unsigned char)*payload;
                payload += 1;
                break;
        }

        values++;
        curr_entity++;
    }

    return 1;
}

/* ------------------------------------------------------------------------- */
/* System Commands                                                           */
/* ------------------------------------------------------------------------- */


/* ------------------------------------------------------------------------- */
