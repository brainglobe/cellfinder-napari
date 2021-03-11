import pandas as pd
from imlib.cells.cells import Cell
from imlib.IO.cells import cells_xml_to_df


def cells_df_as_np(cells_df, new_order=[2, 1, 0], type_column="type"):
    cells_df = cells_df.drop(columns=[type_column])
    cells = cells_df[cells_df.columns[new_order]]
    cells = cells.to_numpy()
    return cells


def cells_to_array(cells):
    df = pd.DataFrame([c.to_dict() for c in cells])
    points = cells_df_as_np(df[df["type"] == Cell.CELL])
    rejected = cells_df_as_np(df[df["type"] == Cell.UNKNOWN])
    return points, rejected


def get_cell_arrays(cells_file):
    df = cells_xml_to_df(cells_file)

    non_cells = df[df["type"] == Cell.UNKNOWN]
    cells = df[df["type"] == Cell.CELL]

    cells = cells_df_as_np(cells)
    non_cells = cells_df_as_np(non_cells)
    return cells, non_cells
