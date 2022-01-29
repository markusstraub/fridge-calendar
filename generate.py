import datetime
import calendar
import holidays
import locale


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
        <th></th>
        <th></th>
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

    def __eq__(self, other):
        return self.year == other.year and self.month == other.month

    def __lt__(self, other):
        return self.year < other.year or (
            self.year == other.year and self.month < other.month
        )

    def __le__(self, other):
        return self == other or self < other

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

    def __iter__(self):
        current = self.start
        while current <= self.end:
            yield current

            new_year = current.year
            new_month = current.month + 1
            if new_month > 12:
                new_year += 1
                new_month = 1
            current = Month(new_year, new_month)


class Birthday:
    def __init__(self, date, name, nick=None):
        self.date = date
        if not isinstance(date, datetime.date):
            self.date = datetime.date.fromisoformat(date)
        self.name = name
        self.nick = nick if nick is not None and len(nick) > 0 else None

    def __repr__(self):
        return f"{self.name} ({self.nick}): {self.date}"

    def get_print_name(self):
        return self.name if self.nick is None else self.nick

    def calc_age(self, year):
        return year - self.date.year

    @classmethod
    def stream(cls, file):
        with open(file) as stream:
            for line in stream:
                if len(line) == 0:
                    continue
                values = [v.strip() for v in line.strip().split(";")]
                if "?" in line or len(values) < 2:
                    print(f"skipping invalid line {line}")
                    continue
                yield cls(*values)


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
        if birthday.date.year == 9999:
            extras += f'<span class="birthday">{birthday.get_print_name()}</span>'
        else:
            extras += f'<span class="birthday">{birthday.get_print_name()} {birthday.date.year} ({birthday.calc_age(cal_day.date.year)})</span>'
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
    html_file = "alma_calendar_example.html"
    months = ["2022-01", "2022-02"]
    birthday_file = "birthdays_example.csv"
    include_holidays = True
    include_birthdays = True
    enforce_31_rows = True

    with open(html_file, mode="w") as file:
        file.write(HTML_START)
        birthdays = list(Birthday.stream(birthday_file))
        for month in Months(*months):
            cal_days = month.create_calendar_days()
            if include_birthdays:
                for birthday in birthdays:
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
