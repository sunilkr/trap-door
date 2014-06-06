import struct

CMD_STOP    = 1
CMD_ADD     = 2
CMD_UPDATE  = 3
CMD_DELETE  = 4

CMD_FILTER_ADD_CHAIN    = 5
CMD_LOGGER_SET_FILTER   = 6



STATUS_OK = 0

ERR_NO_SUCH_ITEM    = -1
ERR_TYPE_MISMATCH   = -2
ERR_CONFLICT        = -3
ERR_CREATE_OBJECT   = -4
ERR_APPLY_ATTRS     = -5
ERR_SEE_LOG         = -100


def to_bool(value):
    """
        Converts 'something' to boolean. Raises exception if it gets a string it doesn't handle.
        Case is ignored for strings. These string values are handled:
        True: 'True', "1", "TRue", "yes", "y", "t"
        False: "", "0", "faLse", "no", "n", "f"
        Non-string values are passed to bool.
    """
    if type(value) == type(''):
        if value.lower() in ("yes", "y", "true",  "t", "1"):
            return True
        if value.lower() in ("no",  "n", "false", "f", "0", ""):
            return False
        raise Exception('Invalid value for boolean conversion: ' + value)
    return bool(value)

def ip4_to_bytes(ip):
    if ip is not None:
        arr = [int(x) for x in ip.split(".")]
        return str(bytearray(arr))
    else:
        return None

def bytes_to_ip4(value):
    if value is not None:
        return ".".join(str(x) for x in struct.unpack("BBBB",value))    
    else:
        return None

