import datetime
import calendar
import holidays
import locale
from collections import namedtuple


HTML_START = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>Alma Kalenderl</title>
    <link rel="stylesheet" href="./alma_calendar.css" />
</head>
<body>
"""

HTML_END = """
</body>
</html>
"""

TABLE_START = """
<table>
<thead>
    <tr>
        <th colspan="2"></th>
        <th colspan="2" class="month">##MONTH##</th>
    </tr>
</thead>
<tbody>
"""

TABLE_END = """
</tbody>
</table>
"""


def month_day_str(date):
    return f"{date.month}_{date.day}"


class Month:
    def __init__(self, year, month):
        self.year = int(year)
        self.month = int(month)

    def __lt__(self, other):
        return self.year < other.year or (
            self.year == other.year and self.month < other.month
        )

    def create_calendar_days(self):
        """returns a dict of month_day_str: CalendarDay"""
        date = datetime.date(self.year, self.month, 1)
        days_in_month = calendar.monthrange(self.year, self.month)[1]
        end_date = date.replace(day=days_in_month)

        delta = datetime.timedelta(days=1)
        days = {}
        while date <= end_date:
            days[month_day_str(date)] = CalendarDay(date)
            date += delta
        return days

    def month_string(self):
        return datetime.date(self.year, self.month, 1).strftime("%B %Y")

    def __repr__(self):
        return f"{self.year:04}-{self.month:02}"


class Months:
    def __init__(self, start, end):
        """start and end (both inclusive) given as yyyy-mm strings"""
        self.start = Month(*start.split("-"))
        self.end = Month(*end.split("-"))
        self.current = None

    def __iter__(self):
        return self

    def __next__(self):
        if self.current is None:
            self.current = self.start
            return self.current

        if not self.current < self.end:
            raise StopIteration

        new_year = self.current.year
        new_month = self.current.month + 1
        if new_month > 12:
            new_year += 1
            new_month = 1
        self.current = Month(new_year, new_month)
        return self.current


class Birthday:
    def __init__(self, name, date):
        self.name = name
        self.date = date

    def __repr__(self):
        return f"{self.name}: {self.date}"

    def calc_age(self, year):
        return year - self.date.year

    def stream(file):
        with open(file) as stream:
            for line in stream:
                name, birthday = line.strip().split(";")
                birthday = datetime.date.fromisoformat(birthday)
                yield Birthday(name, birthday)


class CalendarDay:
    def __init__(self, date):
        self.date = date
        self.birthdays = []
        self.holidays = []

    def is_holiday(self):
        return len(self.holidays) > 0

    def is_weekend(self):
        return self.date.weekday() >= 5

    def add_birthday(self, birthday):
        self.birthdays.append(birthday)

    def add_holiday(self, holiday):
        self.holidays.append(holiday)

    def day_string(self):
        return self.date.strftime("%a")

    def __repr__(self):
        return "|".join([repr(v) for v in [self.date, self.birthdays, self.holidays]])


def to_table_row(cal_day):
    extras = ""
    for holiday in cal_day.holidays:
        extras += f'<span class="holiday">{holiday}</span>'
    for birthday in cal_day.birthdays:
        extras += f'<span class="birthday">{birthday.name} {birthday.date.year} ({birthday.calc_age(cal_day.date.year)})</span>'
    html = "<tr>"
    if cal_day.is_holiday() or cal_day.is_weekend():
        html = '<tr class="no_work">'
    html += f"<td>{cal_day.day_string()}</td>"
    html += f"<td>{cal_day.date.day}</td>"
    html += f"<td>{extras}</td>"
    html += f"<td></td>"
    html += "</tr>\n"
    return html


if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, "de_AT.UTF-8")
    html_file = "alma_calendar.html"
    months = ["2022-01", "2022-02"]
    birthdays = "birthdays.csv"
    include_holidays = True
    include_birthdays = True
    enforce_31_rows = True

    with open(html_file, mode="w") as file:
        file.write(HTML_START)
        for month in Months(*months):
            cal_days = month.create_calendar_days()
            if include_birthdays:
                for birthday in Birthday.stream(birthdays):
                    if month_day_str(birthday.date) in cal_days.keys():
                        cal_days[month_day_str(birthday.date)].add_birthday(birthday)
            if include_holidays:
                for date, name in sorted(holidays.AT(years=month.year).items()):
                    if month_day_str(date) in cal_days.keys():
                        cal_days[month_day_str(date)].add_holiday(name)

            file.write(TABLE_START.replace("##MONTH##", month.month_string()))
            for cal_day in cal_days.values():
                file.write(to_table_row(cal_day))
            if enforce_31_rows and len(cal_days) < 31:
                for i in range(31 - len(cal_days)):
                    file.write("<tr><td>-</td><td>-</td><td></td><td></td></tr>\n")

            file.write(TABLE_END)
        file.write(HTML_END)
