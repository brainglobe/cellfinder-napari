import pandas as pd
from imlib.cells.cells import Cell


def cells_df_as_np(cells_df, new_order=[2, 1, 0], type_column="type"):
    cells_df = cells_df.drop(columns=[type_column])
    cells = cells_df[cells_df.columns[new_order]]
    cells = cells.to_numpy()
    return cells


def cells_to_array(cells):
    df = pd.DataFrame([c.to_dict() for c in cells])
    cells = df[df["type"] == Cell.CELL]
    points = cells_df_as_np(cells)
    return points
