import pandas as pd
import re
from string import ascii_uppercase
from helper_functions_for_cherry_picking import check_df, conv2WellNum

filename = 'CP test.xlsx'
source_col_name = 'S P_R_C'
target_col_name = 'T P_R_C'
output_folder = 'worklist output files'

# load source and target columns from file
df = (pd.read_excel(filename, usecols=[source_col_name, target_col_name])
      .rename({source_col_name: 'Source', target_col_name: 'Target'}, axis=1)
      .dropna(axis=0, how='any'))

# check input df
check_df(df)

# split source and target columns to plate row and column
df_prc = df.applymap(lambda s: list(re.split('(\d+)', s))[1:4])
# concat dataframes and convert numbers to int
df_prc = (pd.concat([pd.DataFrame(df_prc['Source'].to_list(), columns=['Source p', 'Source r', 'Source c']),
                     pd.DataFrame(df_prc['Target'].to_list(), columns=['Target p', 'Target r', 'Target c'])], axis=1)
          .astype({'Source p': int, 'Source c': int, 'Target p': int, 'Target c': int}))

# convert coordinates of wells to well number (column stack)
df_prc['Source num'] = df_prc.apply(lambda s: conv2WellNum(s['Source r'], s['Source c']), axis=1)
df_prc['Target num'] = df_prc.apply(lambda s: conv2WellNum(s['Target r'], s['Target c']), axis=1)

# split df_prc to even / odd rows in the target plate
odd_df_prc = df_prc[df_prc['Target r'].isin([*ascii_uppercase[0:16:2]])].copy()
even_df_prc = df_prc[df_prc['Target r'].isin([*ascii_uppercase[1:16:2]])].copy()

# filter odd_df_prc and even_df_prc to make sure it's in the right order
# order by source plate number, then by target plate number, then by target well column, then by target well row
odd_df_prc.sort_values(by=['Source p', 'Target p', 'Target c', 'Target r'], inplace=True)
even_df_prc.sort_values(by=['Source p', 'Target p', 'Target c', 'Target r'], inplace=True)

# write worklist files
source_plates = df_prc['Source p'].unique()
for sp in source_plates:

    # for the odd rows in source plate p
    odd_cur_df = odd_df_prc.loc[odd_df_prc['Source p'] == sp, ['Source num', 'Target num', 'Target p']]
    with open(f'./{output_folder}/Source_plate_Odd_rows_{sp}.gwl', 'w') as f:
        for s, t, tp in zip(odd_cur_df['Source num'], odd_cur_df['Target num'], odd_cur_df['Target p']):
            f.write(f'A;Source;;;{s};;50\nD;Target{tp};;;{t};;50\nW;\n')

    # for the even rows in source plate p
    even_cur_df = even_df_prc.loc[even_df_prc['Source p'] == sp, ['Source num', 'Target num', 'Target p']]
    with open(f'./{output_folder}/Source_plate_Even_rows_{sp}.gwl', 'w') as f:
        for s, t, tp in zip(even_cur_df['Source num'], even_cur_df['Target num'], even_cur_df['Target p']):
            f.write(f'A;Source;;;{s};;50\nD;Target{tp};;;{t};;50\nW;\n')

    print(f'Source plate {sp} done!')