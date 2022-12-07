import pandas as pd
import re
from string import ascii_uppercase

filename = '20220822_CHERRYPICKING_LETICIA_4 plates.xlsx'
source_col_name = '384 concatenate'
target_col_name = 'NEW coordinate'

# load source and target columns from file
df = pd.read_excel(filename, usecols=[source_col_name, target_col_name]) \
    .rename({source_col_name: 'Source', target_col_name: 'Target'}, axis=1)

df.dropna(axis=0, how='any', inplace=True)

# split source and target columns to plate row and column
source_prc = pd.DataFrame(df["Source"].apply(lambda s: list(re.split('(\d+)', s))[1:4]).to_list(),
                          columns=['Source p', 'Source r', 'Source c'])
target_prc = pd.DataFrame(df["Target"].apply(lambda s: list(re.split('(\d+)', s))[1:4]).to_list(),
                          columns=['Target p', 'Target r', 'Target c'])
# concat all dataframes and convert numbers to int
df_prc = pd.concat([df, source_prc, target_prc], axis=1).astype(int, errors='ignore')
df_prc = df_prc.astype({'Source p': int, 'Source c': int, 'Target p': int, 'Target c': int})

# convert coordinates of wells to well number (column stack)
def conv2WellNum(row, col):
    # this function receives row (string) and column (int) of a well and
    # return the well number in column stack (in 384 plate)
    return 16 * (col - 1)  + ascii_uppercase.index(row) + 1

df_prc['Source num'] = df_prc.apply(lambda s: conv2WellNum(s['Source r'], s['Source c']), axis=1)
df_prc['Target num'] = df_prc.apply(lambda s: conv2WellNum(s['Target r'], s['Target c']), axis=1)

# split df_prc to even / odd rows in the target plate
odd_df_prc = df_prc[df_prc['Target r'].isin(['A', 'C', 'E', 'G', 'I', 'K', 'M', 'O'])].copy()
even_df_prc = df_prc[df_prc['Target r'].isin(['B', 'D', 'F', 'H', 'J', 'L', 'N', 'P'])].copy()

# filter df_prc to make sure it's in the right order
# order by source plate number, then by column, then by row
odd_df_prc.sort_values(by=['Source p', 'Source c', 'Source r'], inplace=True)
even_df_prc.sort_values(by=['Source p', 'Source c', 'Source r'], inplace=True)

# export files
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

    print(sp)




