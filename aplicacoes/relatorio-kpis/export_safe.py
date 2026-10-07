"""Export copies only: untrusted text must not become an Excel formula."""
from io import BytesIO

import pandas as pd


def excel_text(value):
    if isinstance(value, str) and value and (value.lstrip().startswith(("=", "+", "-", "@")) or value[0] in ("\t", "\r", "\n")):
        return "'" + value
    return value


def dataframe_to_excel_bytes(frame):
    copy = frame.copy(deep=True)
    # map acts on every cell while preserving numeric inputs.
    copy = copy.map(excel_text)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        copy.to_excel(writer, index=False)
    return buffer.getvalue()
