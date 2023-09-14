import os
import pandas as pd
import argparse


def manifest_to_dbml(manifest_file: str, dbml_filename: str):
    # sheets in manifest excel workbook
    SYSTEM_SHEET = "sistema"
    TABLE_SHEET = "lentelės"
    COLUMNS_SHEET = "stulpeliai"

    # df_is = pd.read_excel(manifest_file, sheet_name=SYSTEM_SHEET)
    df_tables = pd.read_excel(manifest_file, sheet_name=TABLE_SHEET)
    df_columns = pd.read_excel(manifest_file, sheet_name=COLUMNS_SHEET)

    # columns column can be named "column" or "field"
    column_index = next(
        (i for i, item in enumerate(df_columns.columns) if item in ("field", "column")),
        None,
    )

    # columns type column can be named "type" or "column_type"
    type_index = next(
        (
            i
            for i, item in enumerate(df_columns.columns)
            if item in ("type", "column_type")
        ),
        None,
    )

    if column_index is None or type_index is None:
        raise ValueError("Both column_index and type_index must be specified and not None.") 

    # check where is table records count
    use_irasu_skaicius = True if "įrašų skaičius" in df_tables.columns else False

    # generate dbml lines
    dbml_lines = []
    for row_index, row in df_tables.iterrows():
        table_name = row["table"].replace("$", "_")
        header = f"Table {table_name} {{\n"

        columns = ""
        for col_index, col in (
            df_columns[df_columns["table"] == row["table"]]
        ).iterrows():
            col_name = col[column_index].replace("#", "_").replace("$", "_")

            columns += f"\t{col_name} {col[type_index]}"

            column_comment = str(col["comment"]).replace("'", '"')
            column_note = f"note: '{column_comment}'"
            primary_key = "primary key" if col["is_primary"] else False

            if primary_key and (column_note != "note: 'nan'"):
                details = f"[{primary_key}, {column_note}]"
            elif primary_key:
                details = f"[{primary_key}]"
            elif column_note != "note: 'nan'":
                details = f"[{column_note}]"
            else:
                details = False

            if details:
                columns += f" {details}"

            columns += "\n"

        n_records = row["įrašų skaičius"] if use_irasu_skaicius else col["n_records"]

        table_note = f"\tNote: '''\n\t\t{row['lenteles_paaiskinimas']}\n\t\tObjektas: {row['objektas']}\n\t\tĮrašų skaičius: {n_records} \n\t'''\n"
        footer = "}\n"
        dbml_line = header + columns + table_note + footer
        dbml_lines.append(dbml_line)

    #  dump dbml lines to dbml file
    with open(dbml_filename, "w", encoding="utf8") as dmbl:
        dmbl.writelines(dbml_lines)


def main() -> int:
    arg_parser = argparse.ArgumentParser(
        description="Generate DBML file from systems manifest"
    )
    arg_parser.add_argument("input", help="Input excel file")

    args = arg_parser.parse_args()
    manifest_file = args.input

    dbml_filename = os.path.splitext(os.path.basename(manifest_file))[0] + ".dbml"

    manifest_to_dbml(manifest_file, dbml_filename)


if __name__ == "__main__":
    main()
