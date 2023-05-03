import json
import types
from datetime import datetime

class EventDate:
    def __init__(self, year: int, month: str, day: int):
        self.year = year
        self.month = month
        self.day = day

    def toJson(self):
        return json.loads(json.dumps(self, default=lambda o: o.__dict__))
    
    def equals(self, eventDate):
        return (eventDate.year == self.year 
                and eventDate.month == self.month 
                and eventDate.day == self.day)
    
    def __str__(self):
        return f"year: {self.year}, month: {self.month}, day: {self.day}"

    
class RepeatPeriod:
    NEVER = "NEVER"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"

    def __init__(self, periodDuration):
        self.periodDuration = periodDuration

DayOfWeek = ('MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY')
Month = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"]

def createEventDate(timeMs, zone):
    start = datetime.fromtimestamp(timeMs, zone).date()
    return EventDate(start.year, start.month, start.day)

class Event:
    def __init__ (self):
        self.title = ""
        self.startDate = None
        self.endDate = None
        self.repeatPeriod = RepeatPeriod.NEVER
        self.daysOfWeek = None
        self.enabled = False
        self.incompatible = False
        self.selected = False

    def __str__(self):
        return f"Title: {self.title}, startDate: {self.startDate.__str__()}, endDate: {self.endDate.__str__()}, repeatPeriod: {self.repeatPeriod}, daysOfWeek: {self.daysOfWeek}, enabled: {self.enabled}, incompatible: {self.incompatible}, selected: {self.selected}"

    def createEvent(self, eventJsn: dict):
        def getArrayListFromJSONArray(jsonArray: list): 
            list = []

            def stringToDayOfWeek(dayStr: str): 
                return dayStr

            for i in range(len(jsonArray)): 
                dayStr = jsonArray[i]
                dayOfWeek = stringToDayOfWeek(dayStr)
                list.append(dayOfWeek)

            return list

        def stringToMonth(monthStr: str):
            return {
                'january': Month.JANUARY,
                'february': Month.FEBRUARY,
                'march': Month.MARCH,
                'april': Month.APRIL,
                'may': Month.MAY,
                'june': Month.JUNE,
                'july': Month.JULY,
                'august': Month.AUGUST,
                'september': Month.SEPTEMBER,
                'october': Month.OCTOBER,
                'november': Month.NOVEMBER,
                'december': Month.DECEMBER
            }.get(monthStr.lower(), Month.JANUARY)
        
        def stringToRepeatPeriod(repeatPeriodStr: str) -> RepeatPeriod:
            if repeatPeriodStr.lower() == "daily":
                return RepeatPeriod.DAILY
            elif repeatPeriodStr.lower() == "weekly":
                return RepeatPeriod.WEEKLY
            elif repeatPeriodStr.lower() == "monthly":
                return RepeatPeriod.MONTHLY
            elif repeatPeriodStr.lower() == "yearly":
                return RepeatPeriod.YEARLY
            elif repeatPeriodStr.lower() == "never":
                return RepeatPeriod.NEVER

        timeObj = eventJsn.get("time")
        self.title = eventJsn.get("title")

        self.startDate = timeObj.get("startDate")
        self.endDate = timeObj.get("endDate")
        self.weekDays = timeObj.get("daysOfWeek")
        self.enabled = timeObj.get("enabled") or False
        self.incompatible = timeObj.get("incompatible") or False
        self.selected = timeObj.get("selected") or True
        self.repeatPeriod = stringToRepeatPeriod(timeObj["repeatPeriod"])
        return self

    def to_json(self, title, startDate, endDate, repeatPeriod, daysOfWeek, enabled, incompatible, selected):
        time_obj = types.SimpleNamespace()
        time_obj.repeatPeriod = repeatPeriod
        time_obj.daysOfWeek = daysOfWeek
        time_obj.enabled = enabled
        time_obj.incompatible = incompatible
        time_obj.selected = selected
        
        time_json = json.loads(json.dumps(time_obj.__dict__))

        time_json["startDate"] = startDate.toJson()

        if endDate is None:
            endDate = startDate
        time_json["endDate"] = endDate.toJson()

        event_json = json.loads("{}")
        event_json["title"] = title
        event_json["time"] = time_json

        return event_json

