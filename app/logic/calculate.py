import pandas as pd

def adjust_mark(row):
    grade = row['Grade']
    mark = row['Mark']

    if grade == 'FN':
        return 0
    elif grade == 'FC':
        return 48
    elif grade == 'PS':
        return 50
    elif grade in ['N', 'N+', 'P', 'CR', 'D', 'HD']:
        return mark
    else:
        return None

def choose_credit_points(row):
    mark = row['Adjusted_Mark']
    if mark is not None:
        if mark < 50:
            return row['Enrolled_Credit_Points']
        else:
            return row['Achievable_Credit_Points']
    return None

def assign_honours(row):
    eh_wam = row['EH-WAM']
    geng4412_mark = row['GENG4412 Mark']
    if eh_wam >= 80 and (not pd.isna(geng4412_mark) and geng4412_mark >= 80):
        return 'H1'
    elif eh_wam >= 70 and (not pd.isna(geng4412_mark) and geng4412_mark >= 70):
        return 'H2A'
    elif eh_wam >= 60:
        return 'H2B'
    else:
        return 'H3'

def major_units(conn, major, yr):

    units = handbook.select_all_major_units(conn, major, yr)

    core_units = []
    for unit in units:
        if unit[4] in ('3','4', '5'):
            core_units.append(unit)

    return core_units


def calculations(file):
    # Load the input data
    input_data = pd.read_excel(file)

    # Adjust marks and choose the correct credit points based on the provided rules
    input_data['Adjusted_Mark'] = input_data.apply(adjust_mark, axis=1)
    input_data['Relevant_Credit_Points'] = input_data.apply(choose_credit_points, axis=1)

    # Filter out rows with missing or None values and for Level 3/4/5 units
    relevant_data_adjusted = input_data.dropna(subset=['Adjusted_Mark', 'Relevant_Credit_Points'])
    relevant_units_adjusted = relevant_data_adjusted[relevant_data_adjusted['Unit_Code'].str[4].isin(['3', '4', '5'])]

    # Calculate the EH-WAM
    eh_wam_values_adjusted = relevant_units_adjusted.groupby('Person_ID').apply(
        lambda x: (x['Adjusted_Mark'] * x['Relevant_Credit_Points']).sum() / x['Relevant_Credit_Points'].sum()
    )
    eh_wam_adjusted = pd.DataFrame(eh_wam_values_adjusted, columns=['EH-WAM']).reset_index()
    eh_wam_adjusted['EH-WAM'] = eh_wam_adjusted['EH-WAM'].round(3)

    # Determine GENG4412 completion and mark for each student
    geng4412_data = input_data[input_data['Unit_Code'] == 'GENG4412'][['Person_ID', 'Mark']]
    merged_data_adjusted = pd.merge(eh_wam_adjusted, geng4412_data, on='Person_ID', how='left')
    merged_data_adjusted.rename(columns={'Mark': 'GENG4412 Mark'}, inplace=True)

    # Assign Honours classification
    merged_data_adjusted['Honours Class'] = merged_data_adjusted.apply(assign_honours, axis=1)

    # Save the processed data to an output Excel file (optional)
    merged_data_adjusted.to_excel("output_file.xlsx", index=False)