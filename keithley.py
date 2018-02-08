from urllib.request import urlopen
from urllib.parse import quote_plus
from urllib.error import URLError
from time import sleep
from serial import Serial
from re import search

class KeithleyTimeout(Exception):
    pass

class KeithleyBadData(Exception):
    pass

class KeithleyNoConnection(Exception):
    pass

class KeithleyNoProtocol(Exception):
    pass

class KeithleyFeature():
   
  def __init__(self, parent, channel):
    self.parent = parent
    self._channel = channel
    self._slot = self.parent._slot

  def _getSlotAndChannel(self):
    return '(@%s%s)' % (str(self._slot).zfill(1), str(self._channel).zfill(2))

  def getVoltageDC(self):
    command = 'MEASure:VOLTage:DC? %s' % self._getSlotAndChannel()
    raw = self.parent._send(command)
    if type(raw) is str:
        try:
            return float(raw.split(',')[0][:-3])
        except (ValueError, IndexError):
            raise KeithleyBadData
    else:
        return raw
    

  def getVoltageAC(self):
    command = 'MEASure:VOLTage:AC? %s' % self._getSlotAndChannel()
    raw = self.parent._send(command)
    if type(raw) is str:
        try:
            return float(raw.split(',')[0][:-3])
        except (ValueError, IndexError):
            raise KeithleyBadData
    else:
        return raw

  def getTemperature(self):
    command = 'MEAS:TEMP? %s' % self._getSlotAndChannel()
    raw = self.parent._send(command)
    if type(raw) is str:
        try:
            raw_tu = raw.split(',')[0]
            temp = raw_tu[:-3]
            units = raw_tu[-3:]
            return float(temp)
        except (ValueError, IndexError):
            raise KeithleyBadData
    else:
        return raw

class Keithley():
    _ajax_url = "http://%s/scpi_response.html?cmd=%s"
    _reg_pattern = r"(?<=\<body\>)(.*)(?=\<\/body\>)"
    _error_timeout = "(Query time out)"
    _ip = None
    _comm = None
  
    def __init__(self, ip=None, comm=None, baud=9600, slot=1):
        if ip:
            self._ip = self._format_ip(ip)
        elif comm:
            self._serial = Serial(comm, baud, timeout=1)
        else:
            raise KeithleyNoProtocol

        self._slot = slot
        self.channel = [KeithleyFeature(self, ch) for ch in range(0,21)]
    
    def _format_ip(self, ip):
        return ".".join([str(int(o)) for o in ip.split('.')])

    def _send_ip(self, cmd):
        url = self._ajax_url % (self._ip, quote_plus(cmd))

        try:
            data_raw = urlopen(url).read()
        except URLError:
            raise KeithleyNoConnection

        data = search(self._reg_pattern, str(data_raw))[0]
        if (data == self._error_timeout):
            raise KeithleyTimeout
        else:
            return data
    
    def _send_comm(self, cmd):
        self._serial.flush()
        self._serial.write(b"%s\n" % cmd.encode('UTF-8'))
        sleep(0.5)
        rx = self._serial.read_all()
        rx = list(filter(lambda data: len(data), rx.split(b'\x13')))

        # Check we've recieved a packet
        if not len(rx):
            raise KeithleyBadData

        # Split up the packet
        try:
            data = rx[0].split(b',')
            try:
                value = float(data[0])
            except ValueError:
                value = str(data[0].decode("utf-8"))

        except ValueError:
            raise KeithleyBadData

        return value

    def _send(self, cmd):
        if self._ip:
            return self._send_ip(cmd)
        elif self._serial:
            return self._send_comm(cmd)
        else:
            raise KeithleyNoProtocol

if __name__ == '__main__':
    k = Keithley(comm="COM6")
    temp = k.channel[18].getTemperature()
    print(temp)