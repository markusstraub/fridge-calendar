# Alma Calendar

Generate a monthly calendar including holidays and birthdays as printable HTML

1. Fill in `birthdays.csv` with rows in the form of `yyyy-mm-dd;name;nickname` where 9999 can be used as year if it is unknown and `nickname` can be omitted. Note, that lines containing `?` are omitted.
2. Adjust desired locale and date range in `generate.py`
3. Run `generate.py`
4. Open the generated file in Firefox and print it to pdf as desired (e.g. one or two months per page,..)
