import pandas as pd
import re
from string import ascii_uppercase

def check_df(df):
    # check if there are duplicated wells
    duplicated = list(df['Source'][df['Source'].duplicated()].unique())
    try:
        assert not duplicated
    except AssertionError:
        print(f'Warning - you have duplicated source wells: {duplicated}')
    duplicated = list(df['Target'][df['Target'].duplicated()].unique())
    try:
        assert not duplicated
    except AssertionError:
        print(f'Warning - you have duplicated target wells: {duplicated}')

    # check for typos
    split_df = df.applymap(lambda p: list(re.split('(\d+)', p))[1:4])
    split_df = pd.concat([pd.DataFrame(split_df['Source'].to_list(), columns=['SP', 'SR', 'SC']),
                pd.DataFrame(split_df['Target'].to_list(), columns=['TP', 'TR', 'TC'])], axis=1)
    try:  # check target plate
        assert set(split_df['TP'].unique()).issubset(['1', '2', '3', '4'])
    except AssertionError:
        print(f'Warning - Check your target plates are 1-4, you have {split_df["TP"].unique()}')
    try:  # check target rows
        assert set(split_df['TR'].unique()).issubset([*ascii_uppercase[0:16]])
    except AssertionError:
        print(f'Warning - Check your target row are in A-P, you have {split_df["TR"].unique()}')
    try:  # check source rows
        assert set(split_df['SR'].unique()).issubset([*ascii_uppercase[0:16]])
    except AssertionError:
        print(f'Warning - Check your source row are in A-P, you have {split_df["SR"].unique()}')
    try:  # check target plate
        assert set(split_df['TC'].unique()).issubset(list(map(str, range(1, 25))))
    except AssertionError:
        print(f'Warning - Check your target column in 1-24, you have {split_df["TC"].unique()}')
    try:  # check source plate
        assert set(split_df['SC'].unique()).issubset(list(map(str, range(1, 25))))
    except AssertionError:
        print(f'Warning - Check your source column are in 1-24, you have {split_df["SC"].unique()}')

    return None

def conv2WellNum(row, col):
    # this function receives row (string) and column (int) of a well and
    # return the well number in column stack (in 384 plate)
    return 16 * (col - 1) + ascii_uppercase.index(row) + 1
