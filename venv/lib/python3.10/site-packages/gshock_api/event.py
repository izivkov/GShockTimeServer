import json
import types
from datetime import datetime

class EventDate:
    def __init__(self, year: int, month: str, day: int):
        self.year = year
        self.month = month
        self.day = day

    def to_json(self):
        return json.loads(json.dumps(self, default=lambda o: o.__dict__))

    def equals(self, event_date):
        return (
            event_date.year == self.year
            and event_date.month == self.month
            and event_date.day == self.day
        )

    def __str__(self):
        return f"year: {self.year}, month: {self.month}, day: {self.day}"


class RepeatPeriod:
    NEVER = "NEVER"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"

    def __init__(self, period_duration):
        self.period_duration = period_duration


day_of_week = (
    "MONDAY",
    "TUESDAY",
    "WEDNESDAY",
    "THURSDAY",
    "FRIDAY",
    "SATURDAY",
    "SUNDAY",
)
month = [
    "JANUARY",
    "FEBRUARY",
    "MARCH",
    "APRIL",
    "MAY",
    "JUNE",
    "JULY",
    "AUGUST",
    "SEPTEMBER",
    "OCTOBER",
    "NOVEMBER",
    "DECEMBER",
]


def create_event_date(time_ms, zone):
    start = datetime.fromtimestamp(time_ms, zone).date()
    return EventDate(start.year, start.month, start.day)


class Event:
    def __init__(self):
        self.title = ""
        self.start_date = None
        self.end_date = None
        self.repeat_period = RepeatPeriod.NEVER
        self.days_of_week = None
        self.enabled = False
        self.incompatible = False
        self.selected = False

    def __str__(self):
        return f"""Title: {self.title}, 
        startDate: {self.start_date.__str__()}, 
        endDate: {self.end_date.__str__()}, 
        repeatPeriod: {self.repeat_period}, 
        daysOfWeek: {self.days_of_week}, 
        enabled: {self.enabled}, 
        incompatible: {self.incompatible}, 
        selected: {self.selected}"""

    def create_event(self, event_jsn: dict):
        def get_array_list_from_json_array(json_array: list):
            list = []

            def string_to_day_of_week(day_str: str):
                return day_str

            for i in range(len(json_array)):
                day_str = json_array[i]
                day_of_week = string_to_day_of_week(day_str)
                list.append(day_of_week)

            return list

        def string_to_month(month_str: str):
            return {
                "january": month.JANUARY,
                "february": month.FEBRUARY,
                "march": month.MARCH,
                "april": month.APRIL,
                "may": month.MAY,
                "june": month.JUNE,
                "july": month.JULY,
                "august": month.AUGUST,
                "september": month.SEPTEMBER,
                "october": month.OCTOBER,
                "november": month.NOVEMBER,
                "december": month.DECEMBER,
            }.get(month_str.lower(), month.JANUARY)

        def string_to_repeat_period(repeat_period_str: str) -> RepeatPeriod:
            if repeat_period_str.lower() == "daily":
                return RepeatPeriod.DAILY
            elif repeat_period_str.lower() == "weekly":
                return RepeatPeriod.WEEKLY
            elif repeat_period_str.lower() == "monthly":
                return RepeatPeriod.MONTHLY
            elif repeat_period_str.lower() == "yearly":
                return RepeatPeriod.YEARLY
            elif repeat_period_str.lower() == "never":
                return RepeatPeriod.NEVER

        time_obj = event_jsn.get("time")
        self.title = event_jsn.get("title")

        self.start_date = time_obj.get("start_date")
        self.end_date = time_obj.get("end_date")
        self.week_days = time_obj.get("days_of_week")
        self.enabled = time_obj.get("enabled") or False
        self.incompatible = time_obj.get("incompatible") or False
        self.selected = time_obj.get("selected") or True
        self.repeat_period = string_to_repeat_period(time_obj.get("repeat_period"))
        return self

    def to_json(
        self,
        title,
        start_date,
        end_date,
        repeat_period,
        days_of_week,
        enabled,
        incompatible,
        selected,
    ):
        time_obj = types.SimpleNamespace()
        time_obj.repeatPeriod = repeat_period
        time_obj.daysOfWeek = days_of_week
        time_obj.enabled = enabled
        time_obj.incompatible = incompatible
        time_obj.selected = selected

        time_json = json.loads(json.dumps(time_obj.__dict__))

        time_json["start_date"] = start_date.toJson()

        if end_date is None:
            end_date = start_date
        time_json["end_date"] = end_date.toJson()

        event_json = json.loads("{}")
        event_json["title"] = title
        event_json["time"] = time_json

        return event_json