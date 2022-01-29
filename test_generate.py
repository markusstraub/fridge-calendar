from calendar import month
from generate import Birthday
from generate import Month
from generate import Months
from datetime import date


def test_birthday():
    a = Birthday("1980-07-30", "Hubert")
    b = Birthday(date(1980, 7, 30), "Hubert")
    assert a.date == b.date


def test_birthday_parsing():
    birthdays = {b.name: b for b in Birthday.stream("birthdays_example.csv")}
    assert len(birthdays) == 4
    assert birthdays["Gustav Fröhlich"].nick == "Gusti"
    assert birthdays["Gustav Fröhlich"].date == date(9999, 1, 9)

    assert birthdays["Daniel Dekor"].nick == None
    assert birthdays["Daniel Dekor"].date == date(2000, 1, 1)


def test_month():
    january = Month(2020, 1)
    january_instance2 = Month(2020, 1)
    february = Month(2020, 2)

    assert january == january_instance2
    assert january <= january_instance2
    assert january < february


def test_months():
    months = list(Months("2022-01", "2022-01"))
    assert len(months) == 1
    assert months[0].year == 2022 and months[0].month == 1

    months = list(Months("2022-01", "2022-03"))
    assert len(months) == 3
    assert months[0].year == 2022 and months[0].month == 1
    assert months[2].year == 2022 and months[2].month == 3

    count = 0
    for _ in Months("2022-01", "2022-03"):
        count += 1
    assert count == 3
