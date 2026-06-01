"""
Creates sample members.xlsx with Previous Balance column.
"""
import os
import pandas as pd

DATA = {
    "Name":             ["Rahul Sharma", "Priya Nair", "Arjun Menon", "Divya Rao"],
    "Phone Number":     ["9591584551",   "9380494294", "9988776655",  "9001234567"],
    "Monthly Fee":      [30,  50, 30, 40],
    "Previous Balance": [150,  0,  75,  0],
    "January":          [30,  50, 30,  0],
    "February":         [30,  50, 10,  0],
    "March":            [30,   0, 30, 40],
    "April":            [ 0,   0,  0,  0],
    "May":              [ 0,   0,  0,  0],
    "June":             [ 0,   0,  0,  0],
    "July":             [ 0,   0,  0,  0],
    "August":           [ 0,   0,  0,  0],
    "September":        [ 0,   0,  0,  0],
    "October":          [ 0,   0,  0,  0],
    "November":         [ 0,   0,  0,  0],
    "December":         [ 0,   0,  0,  0],
}

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "members.xlsx")
pd.DataFrame(DATA).to_excel(out, index=False, sheet_name="Sheet1")
print(f"Created: {out}")