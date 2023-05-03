import json, logging
import numpy as np
from casio_constants import CasioConstants
from utils import to_int_array, to_compact_string, to_hex_string

logger = logging.getLogger(__name__)

HOURLY_CHIME_MASK = 0b10000000
ENABLED_MASK = 0b01000000
ALARM_CONSTANT_VALUE = 0x40

CHARACTERISTICS = CasioConstants.CHARACTERISTICS

class Alarm:
  def __init__(self, hour, minute, enabled, hasHourlyChime):
    self.hour = hour
    self.minute = minute
    self.enabled = enabled
    self.hasHourlyChime = hasHourlyChime


class Alarms:
  alarms = []

  def clear(self):
     self.alarms.clear()

  def addAlarms(self, alarmJsonStrArr):
    for alarmJsonStr in alarmJsonStrArr:
      alarm = json.loads(alarmJsonStr)
      self.alarms.append(alarm)

  def fromJsonAlarmFirstAlarm(self, alarm): 
    return self.createFirstAlarm(alarm)

  def createFirstAlarm(self, alarm):
    flag = 0
    if alarm["enabled"]:
      flag = flag | ENABLED_MASK
    if alarm["hasHourlyChime"]:
      flag = flag | HOURLY_CHIME_MASK

    return bytearray([
      CHARACTERISTICS["CASIO_SETTING_FOR_ALM"],
      flag,
      ALARM_CONSTANT_VALUE,
      alarm["hour"],
      alarm["minute"]])
  
  def fromJsonAlarmSecondaryAlarms(self, alarmsJson):
    if len(alarmsJson) < 2:
      return []
    alarms = self.alarms[1:]
    return self.createSecondaryAlarm(alarms)
 
  def createSecondaryAlarm(self, alarms):
      allAlarms = bytearray([CHARACTERISTICS["CASIO_SETTING_FOR_ALM2"]])

      for alarm in alarms:
          flag = 0
          if alarm["enabled"]:
              flag = flag | ENABLED_MASK
          if alarm["hasHourlyChime"]:
              flag = flag | HOURLY_CHIME_MASK

          allAlarms += bytearray([flag, ALARM_CONSTANT_VALUE, alarm["hour"], alarm["minute"]])

      return allAlarms
  
alarmsInst = Alarms()

class AlarmDecoder:
    def toJson(self, command: str):
        jsonResponse = {}
        intArray = to_int_array(command)
        alarms = []

        if intArray[0] == CHARACTERISTICS["CASIO_SETTING_FOR_ALM"]:
            intArray.pop(0)
            alarms.append(self.createJsonAlarm(intArray))
            jsonResponse['ALARMS'] = alarms
        elif intArray[0] == CHARACTERISTICS["CASIO_SETTING_FOR_ALM2"]:
            intArray.pop(0)
            for item in np.array_split(intArray, 4):
                alarms.append(self.createJsonAlarm(item))
            jsonResponse['ALARMS'] = alarms
        else:
            logger.info("Unhandled Command {}".format(command))

        return jsonResponse
    
    def createJsonAlarm(self, intArray):
        alarm = Alarm(
            intArray[2],
            intArray[3],
            intArray[0] & ENABLED_MASK != 0,
            intArray[0] & HOURLY_CHIME_MASK != 0
        )
        return self.to_json(alarm)
    
    def to_json(self, alarm):
       return json.dumps({"enabled":bool(alarm.enabled), "hasHourlyChime":bool(alarm.hasHourlyChime), "hour": int(alarm.hour), "minute": int(alarm.minute)})
    
alarmDecoder = AlarmDecoder()
