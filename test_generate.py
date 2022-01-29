from generate import Birthday
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
