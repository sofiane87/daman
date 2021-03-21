import pandas as pd
from daman import daman as dm


def summary_command():
    max_rows = pd.get_option("display.max_rows")
    pd.set_option("display.max_rows", None)
    print(dm.summary)
    pd.set_option("display.max_rows", max_rows)
