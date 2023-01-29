# %%
# import libs
import logging
from configparser import ConfigParser
import glob
import re
import os
import csv
from openpyxl import load_workbook
import pandas as pd
from pandas.errors import ParserError
import pandas.io.formats.excel


# %%
# Read config.ini file
config_object = ConfigParser()
config_object.read(r"config/config.ini")


# %%
# function to detect csv delimiter
def function_find_csv_delimiter(filename):
    '''add docstring
    '''
    sniffer = csv.Sniffer()
    with open(filename) as file:
        delimiter = sniffer.sniff(file.read(100)).delimiter
    return delimiter


# %%
# setup log
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(
            filename=r"logs/log.log", mode="w"),
        logging.StreamHandler()]
)
logging.info(": Process start")


# setup csv delimiter
try:
    csv_delimiter = function_find_csv_delimiter(
        glob.glob(r"01_in/*.csv")[0])
    logging.info(": CSV_delimiter - %s", csv_delimiter)
except IndexError:
    csv_delimiter = ";"


# setup number of header rows
config_header_rows = config_object["USER_SETTINGS"]["header_rows"].strip()
if config_header_rows.replace(",", "").isnumeric():
    header_rows = [
        row-1 for row in list(map(int, config_header_rows.split(",")))]
else:
    header_rows = [0]
logging.info(": Header rows - %s", config_header_rows)


# setup encoding type for csv file
encoding = config_object["USER_SETTINGS"]["encoding"].strip()
if encoding == "":
    encoding = "utf-8"
logging.info(": Encoding is %s", encoding)


# %%
# change format excel_files to text
def function_change_format_to_text_in_excel():
    '''add docstring
    '''
    for excel_filename in glob.glob(r"01_in/*.xlsx"):
        workbook = load_workbook(excel_filename)

        # format to text
        for worksheet_name in workbook.sheetnames:
            for row in workbook[worksheet_name].iter_rows():
                for cell in row:
                    if cell.column_letter == "A" and cell.row > 1:
                        workbook[worksheet_name][cell.coordinate].number_format = "@"

        workbook.save(excel_filename)


function_change_format_to_text_in_excel()


# %%
# concat files into one
def function_concat_files_into_one():
    '''doctstring must add
    '''

    df = pd.DataFrame()

    for input_filename in glob.glob(r"01_in/*"):
        if input_filename[-4:] == ".csv":
            try:
                input_df = pd.read_csv(input_filename, sep=csv_delimiter,
                                       header=header_rows, encoding=encoding, dtype="string")
            except ParserError:
                logging.error(
                    ": Skipping incompatible file - %s", os.path.basename(input_filename))
        elif input_filename[-5:] == ".xlsx":
            input_df = pd.read_excel(
                input_filename, header=header_rows, dtype="string")
        else:
            logging.error(
                ": Incorrect data type - %s", os.path.basename(input_filename))
            continue

        input_df.rename(columns=lambda x: re.sub(
            "Unnamed: [0-9]*_level_[0-9]", "", str(x)), inplace=True)
        input_df.rename(columns=lambda x: str(x).strip(), inplace=True)

        duplicate_cols = input_df.columns[input_df.columns.duplicated()]
        if len(duplicate_cols) > 0:
            logging.info(
                ": Duplicate column(s) - %s found in file %s" % (list(duplicate_cols), os.path.basename(input_filename)))
            input_df.columns = pd.io.parsers.base_parser.ParserBase({"names": list(
                input_df.columns), "usecols": None})._maybe_dedup_names(list(input_df.columns))
        df = pd.concat([input_df, df])
    logging.info(": Concatenate file contains %s rows and %s columns",
                 df.shape[0], df.shape[1])

    if glob.glob(r"01_in/*")[0][-4:] == ".csv":
        df.to_csv(
            r"02_out/concat_file.csv", sep=csv_delimiter, index=False)

    else:
        try:
            with pd.ExcelWriter(r"02_out/concat_file.xlsx") as writer:
                pandas.io.formats.excel.ExcelFormatter.header_style = None
                df.to_excel(writer, index=False)
        except NotImplementedError:
            with pd.ExcelWriter(r"02_out/concat_file.xlsx") as writer:
                pandas.io.formats.excel.ExcelFormatter.header_style = None
                index_names = list(df.columns[0])
                df = df.set_index(df.columns[0]).rename_axis(
                    index_names, axis='columns')
                df.index.name = None
                df.to_excel(writer)

    logging.info(": Process end")


# %%
function_concat_files_into_one()
