import re

record = r"(\|\d{1,2}\|\d{1,2}:\d{1,2}:\d{1,2}\|\d{1,2}:\d{1,2}:\d{1,2}\|)"

string = '|1|09:55:32|09:55:38|'
m = re.search(record, string)
print(m.group(0))
print(m)
