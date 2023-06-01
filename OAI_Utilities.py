import pandas as pd

visit_prefixes = ['P02', 'P01', 'V00', 'V01', 'V02', 'V03', 'V04', 'V05', 'V06', 'V07', 'V08', 'V09', 'V10', 'V11']
visit_prefixes_year = ['V00', 'V01', 'V03', 'V05', 'V06', 'V07', 'V08', 'V09', 'V10', 'V11']  # Drop pre-screening and half year visits
visit_cats_year = ['1: 12-month', '3: 24-month', '5: 36-month', '6: 48-month', '7: 60-month', '8: 72-month', '9: 84-month', '10: 96-month', '11: 108-month']

visit_prefix_to_month = {'V00':'0', 'V01':'12', 'V02':'18', 'V03':'24', 'V04':'30', 'V05':'36', 'V06':'48', 'V07':'60', 'V08':'72', 'V09':'84', 'V10':'96', 'V11':'108'}
visit_prefix_to_year = {'P01':-1, 'V00':0, 'V01':1, 'V02': 1.5, 'V03':2, 'V04': 2.5, 'V05':3, 'V06':4, 'V07':5, 'V08':6, 'V09':7, 'V10':8, 'V11':9}
visit_cat_to_prefix = {'1: 12-month' : 'V01', '3: 24-month': 'V03', '5: 36-month': 'V05', '6: 48-month': 'V06', '7: 60-month': 'V07', '8: 72-month': 'V08', '9: 84-month': 'V09', '10: 96-month': 'V10', '11: 108-month': 'V11'}
visit_cat_to_year = {'0: Baseline': 0, '1: 12-month' : 1, '2: 18-month' : 1.5, '3: 24-month': 2, '4: 30-month' : 2.5, '5: 36-month': 3, '6: 48-month': 4, '7: 60-month': 5, '8: 72-month': 6, '9: 84-month': 7, '10: 96-month': 8, '11: 108-month': 9, '12: 120-month': 10}

sides_cat = ['1: Right', '2: Left']

prior_post_visits = [str(i) + ' prior' for i in range(9,0,-1)] + [str(i) + ' post' for i in range(1,10)]

#  General Utilities

# Given one or more dataframes, print the wiki markdown for each table
def print_md_table(tables):
    if isinstance(tables, list):
        for table in tables:
            print(table.to_markdown(tablefmt='mediawiki'))
    else:
        print(tables.to_markdown(tablefmt='mediawiki'))
        
# Given a target index level and a dictionary of what values you wish to map to new values, apply to supplied dataframe
def rename_index_values(df, dct, level=0):
    df.index = df.index.set_levels([[dct.get(item, item) for item in names] if i==level else names for i, names in enumerate(df.index.levels)])
    return df

def flip_dict(dic):
    return {v:k for k,v in dic.items()}

# Fixes the annoyances of the default Pandas value_counts() method
def value_counts(ser, hidena=False):
    tmp = ser.value_counts(dropna=hidena) # Default to showing NA count
    return tmp[tmp > 0] # Drop the 0 counts that Categorical columns trigger

# This is handy when you are calling value_counts on a series of columns and want the results to print horizontally and be in the same order
def value_counts_list(ser):
    return sorted([(str(idx), val) for idx, val  in value_counts(ser).iteritems()])


#   OAI Specific 

# Given a dataframe, column/variable name and a desired value, return the set of all patient IDs that match the desired value
def get_ids(df, variable_name, match_value):
    return set(df[df[variable_name] == match_value].index.get_level_values(0))

# Return a list of visits where data was collected for the given column name
def get_visits(df, col):
    tmp = df[col]
    tmp = tmp.reset_index(level='Visit')
    return tmp[~tmp[col].isna()]['Visit'].unique().to_list()


# Pull the side name out of the categorical label
# Several categoricals state what side a measurement came from in the form '1: Right'
# This returns 'Right' in the former case
def get_side_name(side):
    return side.split(':')[1].strip()

# Take a dictionary of items, where each item has a list of which columns are true for each item, and turn it into a dataframe
def sets_into_dataframe(row_set_dict):
    # row_set_dict = {row_name : [cols to be True]}
    cols = list(set([item for sublist in row_set_dict.values() for item in sublist])) # Flatten lists, reduce to set, return as list of unique items
    cols.sort()
    # Create list of True/False values for each row's inclusion in a set
    for descript, row_set in row_set_dict.items():
        row_set_dict[descript] = [True if col in row_set else False for col in cols]
    df = pd.DataFrame(row_set_dict, index=cols).T
    df = df.replace(False, '-')  # Replacing False with - improves readability
    return df