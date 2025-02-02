import re

text = r"""\n\n\n\n\n\n\n\n\n \n\n\n\n\n\n\nSoftware EngineerSoftware Engineer\n\n\n\n\nUmicas\n\n\n\n\n\n\nUnited States (Remote)\n\n\n \n\n\n\n\n\nUp to $310K/yr · Vision, 401(k), +3 benefits\n\n\n\n\n \n\n\n\n\n                      Viewed\n                    \n\n\nPromoted\n\n\n \n\n \n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"""
# Split on 2+ whitespace characters and filter out any empty entries
groups = [s for s in re.split(r'\s{2,}', text.strip()) if s]
print(groups)
