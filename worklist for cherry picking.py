import pandas as pd
import re
from string import ascii_uppercase

filename = '20220822_CHERRYPICKING_LETICIA_4 plates.xlsx'
source_col_name = '384 concatenate'
target_col_name = 'NEW coordinate'

# load source and target columns from file
df = (pd.read_excel(filename, usecols=[source_col_name, target_col_name])
      .rename({source_col_name: 'Source', target_col_name: 'Target'}, axis=1)
      .dropna(axis=0, how='any'))

# check if there are duplicated wells
def check4duplicates (df):
    duplicated_source = list(df['Source'][df['Source'].duplicated()].unique())
    duplicated_target = list(df['Target'][df['Target'].duplicated()].unique())
    try:
        assert not duplicated_source
    except AssertionError:
        print(f'Warning - you have duplicated source wells: {duplicated_source}')
    try:
        assert not duplicated_target
    except AssertionError:
        print(f'Warning - you have duplicated target wells: {duplicated_target}')
    return None

check4duplicates(df)

# split source and target columns to plate row and column
df_prc = df.applymap(lambda s: list(re.split('(\d+)', s))[1:4])
# concat dataframes and convert numbers to int
df_prc = (pd.concat([pd.DataFrame(df_prc['Source'].to_list(), columns=['Source p', 'Source r', 'Source c']),
                     pd.DataFrame(df_prc['Target'].to_list(), columns=['Target p', 'Target r', 'Target c'])], axis=1)
          .astype({'Source p': int, 'Source c': int, 'Target p': int, 'Target c': int}))

# convert coordinates of wells to well number (column stack)
def conv2WellNum(row, col):
    # this function receives row (string) and column (int) of a well and
    # return the well number in column stack (in 384 plate)
    return 16 * (col - 1) + ascii_uppercase.index(row) + 1

df_prc['Source num'] = df_prc.apply(lambda s: conv2WellNum(s['Source r'], s['Source c']), axis=1)
df_prc['Target num'] = df_prc.apply(lambda s: conv2WellNum(s['Target r'], s['Target c']), axis=1)

# split df_prc to even / odd rows in the target plate
odd_df_prc = df_prc[df_prc['Target r'].isin(['A', 'C', 'E', 'G', 'I', 'K', 'M', 'O'])].copy()
even_df_prc = df_prc[df_prc['Target r'].isin(['B', 'D', 'F', 'H', 'J', 'L', 'N', 'P'])].copy()

# filter odd_df_prc and even_df_prc to make sure it's in the right order
# order by source plate number, then by well column, then by well row
odd_df_prc.sort_values(by=['Source p', 'Source c', 'Source r'], inplace=True)
even_df_prc.sort_values(by=['Source p', 'Source c', 'Source r'], inplace=True)

# write worklist files
source_plates = df_prc['Source p'].unique()
for sp in source_plates:

    # for the odd rows in source plate p
    odd_cur_df = odd_df_prc.loc[odd_df_prc['Source p'] == sp, ['Source num', 'Target num', 'Target p']]
    with open(f'C:/Users/zoharga/Desktop/Zohar/cherry picking/output/Source_plate_Odd_rows_{sp}.txt', 'w') as f:
        for s, t, tp in zip(odd_cur_df['Source num'], odd_cur_df['Target num'], odd_cur_df['Target p']):
            f.write(f'A;Source;;;{s};;50\nD;Target{tp};;;{t};;50\nW;\n')

    # for the even rows in source plate p
    even_cur_df = even_df_prc.loc[even_df_prc['Source p'] == sp, ['Source num', 'Target num', 'Target p']]
    with open(f'C:/Users/zoharga/Desktop/Zohar/cherry picking/output/Source_plate_Even_rows_{sp}.txt', 'w') as f:
        for s, t, tp in zip(even_cur_df['Source num'], even_cur_df['Target num'], even_cur_df['Target p']):
            f.write(f'A;Source;;;{s};;50\nD;Target{tp};;;{t};;50\nW;\n')

    print(f'Source plate {sp} done!')
