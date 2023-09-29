import pandas as pd

class Marks_processor():
    def __init__(self, handbookDB) -> None:
        self.handbookDB = handbookDB

    def adjust_mark(self, row):
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

    def choose_credit_points(self, row):
        mark = row['Adjusted_Mark']
        if mark is not None:
            if mark < 50:
                return row['Enrolled_Credit_Points']
            else:
                return row['Achievable_Credit_Points']
        return None

    def assign_honours(self, row):
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

    def major_units(self, conn, major, yr):

        units = self.handbookDB.select_all_major_units(major, yr)

        core_units = []
        for unit in units:
            if unit[4] in ('3','4', '5'):
                core_units.append(unit)

        return core_units


    def process_file(self, input_filepath, output_filepath):
        # Load the input data
        input_data = pd.read_excel(input_filepath)

        # Adjust marks and choose the correct credit points based on the provided rules
        input_data['Adjusted_Mark'] = input_data.apply(self.adjust_mark, axis=1)
        input_data['Relevant_Credit_Points'] = input_data.apply(self.choose_credit_points, axis=1)

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

        print(merged_data_adjusted)

        # 1. Take the Surname, Given Names, Course_Code, Course_Title, Major_Deg from the lowest row number for each Person_ID
        # Join on Person_ID
        personal_data = input_data.groupby('Person_ID').last().reset_index()[['Person_ID', 'Surname', 'Given Names', 'Course_Code', 'Course_Title', 'Major_Deg']]
        merged_data_adjusted = pd.merge(personal_data, merged_data_adjusted, on='Person_ID', how='left')

        merged_data_adjusted.rename(columns={'Mark': 'GENG4412 Mark'}, inplace=True)

        # Creates another column called 'Completed GENG4412 (Y/N)' and fills it with 'Y' if the student has completed GENG4412
        # Highlights with a 'N' if the student has not completed GENG4412 in red
        merged_data_adjusted['Completed GENG4412 (Y/N)'] = merged_data_adjusted['GENG4412 Mark'].apply(lambda x: 'Y' if not pd.isna(x) else 'N')
        merged_data_adjusted.style.apply(lambda x: ['color: red' if v == 'N' else '' for v in x], axis=1, subset=['Completed GENG4412 (Y/N)'])

        # Assign Honours classification
        merged_data_adjusted['Honours Class'] = merged_data_adjusted.apply(self.assign_honours, axis=1)

        # Turns Person_ID into a string
        merged_data_adjusted['Person_ID'] = merged_data_adjusted['Person_ID'].astype(str)

        # Adds two empty columns - 'Missing Information (Y/N)' - 'Comments (missing information)'
        merged_data_adjusted['Missing Information (Y/N)'] = ''
        merged_data_adjusted['Comments (missing information)'] = ''

        # Order of columns
        merged_data_adjusted = merged_data_adjusted[['Person_ID', 'Surname', 'Given Names', 'Course_Code', 'Course_Title', 'Major_Deg', 'Completed GENG4412 (Y/N)','GENG4412 Mark', 'EH-WAM',  'Honours Class', 'Missing Information (Y/N)', 'Comments (missing information)']]

        # Save the processed data to an output Excel file (optional)
        merged_data_adjusted.to_excel(output_filepath, index=False)

        return merged_data_adjusted