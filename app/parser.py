import asyncio
from dataclasses import dataclass


@dataclass(frozen=True)
class DataType:
    Array = b'*'
    Bulk_String = b'$'
    Simple_String = b'+'
    Simple_Error = b'-'
    Integer = b':'


@dataclass
class Constant:
    Null_Bulk_String = b'$-1\r\n'
    Terminator = b'\r\n'
    Empty_Byte = b''
    Space_Byte = b' '
    Pong = b'PONG'
    OK = b'OK'
    Invalid_Command = b'Invalid Command'
    FullResync = b'FULLRESYNC'

@dataclass
class Command:
    Ping = 'ping'
    Echo = 'echo'
    Set = 'set'
    Get = 'get'
    Info = 'info'
    Replconf = 'replconf'
    Ack = 'ack'
    GetAck = 'getack'
    Psync = 'psync'
    FullReSync = 'fullresync'
    Wait = 'wait'
    Config = 'config'





# Redis Parser
class RESPParser:
    def parse(self, data):

        """
        Parses RESP data based on the first byte.
        """

        if data.startswith(b"+"):
            return self._parse_simple_string(data)
        elif data.startswith(b"-"):
            return self._parse_error(data)
        elif data.startswith(b":"):
            return self._parse_integer(data)
        elif data.startswith(b"$"):
            return self._parse_bulk_string(data)
        elif data.startswith(b"*"):
            return self._parse_array(data)
        else:
            raise ValueError("Unknown RESP data type")
        
    def _parse_simple_string(self, data):
        return data[1:-2].decode()
    
    def _parse_error(self, data):
        return Exception(data[1:-2].decode())
    
    def _parse_integer(self, data):
        return int(data[1:-2])

    def _parse_bulk_string(self, data):
        lines = data.split(b"\r\n",2)
        length = int(lines[0][1:])
        if length == -1:
            return None
        return lines[1].decode()
    
    def _parse_array(self, data):
        lines = data.split(b"\r\n")
        num_elements = int(lines[0][1:])
        elements = []
        index = 1 
        for _ in range(num_elements):
            length = int(lines[index][1:])
            elements.append(lines[index + 1].decode())
            index += 2 
        return elements