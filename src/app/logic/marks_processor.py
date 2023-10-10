import pandas as pd
from pandas import ExcelWriter

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
    
    def passed(self, grade):
        # HD,D,CR,P,UP,PS,PA 
        if grade in ['HD', 'D', 'CR', 'P', 'UP', 'PS', 'PA']:
            return True
        else:
            return False


    def process_file(self, input_filepath, output_filepath):
        # Load the input data
        input_data = pd.read_excel(input_filepath)

        # Adjust marks and choose the correct credit points based on the provided rules
        input_data['Adjusted_Mark'] = input_data.apply(self.adjust_mark, axis=1)
        input_data['Relevant_Credit_Points'] = input_data.apply(self.choose_credit_points, axis=1)

        # Calculate Eligability before WAM
        # 1. Get all students by unique Person_ID and their major (person_id,major,list of [unit_code,grade,mark,credit_points])
        # 2. only include units that have passed - use the passed function
        eligability_data = input_data[input_data.apply(lambda x: self.passed(x['Grade']), axis=1)]
        eligability_data = eligability_data.groupby(['Person_ID', 'Major_Deg']).apply(
            lambda x: x[['Unit_Code','Grade','Relevant_Credit_Points']].values.tolist()
        )

        comments = {}
        student_eligable = {}
        # For each person id x major, get all the major_id for all years
        for index, row in eligability_data.items():
            eligable = False
            # turns their unit_codes into a set
            unit_codes = set([unit[0] for unit in row])
            major_ids = self.handbookDB.get_major_ids(index[1])
            # for each major id, get the rules
            # comments is user_id : {major_id: ['comment']}
            for major_id in major_ids:
                major_eligable = True
                rules = self.handbookDB.fetch_major_rules_verbose_by_id(major_id)
                for rule in rules:
                    required_credit_points = rule[1]
                    current_credit_points = 0

                    # Zero credit point unit check
                    zero_cp_units = [unit[0] for unit in rule[2] if unit[1] == 0]
                    for z_unit in zero_cp_units:
                        if z_unit not in unit_codes:
                            if index[0] not in comments:
                                comments[index[0]] = {}
                            if major_id not in comments[index[0]]:
                                comments[index[0]][major_id] = []
                            comments[index[0]][major_id].append(f'Student has not completed 0 credit point unit: {z_unit}')
                            major_eligable = False

                    for unit in rule[2]:
                        if unit[0] in unit_codes:
                            current_credit_points += unit[1]
                    if current_credit_points < required_credit_points:
                        if index[0] not in comments:
                            comments[index[0]] = {}
                        if major_id not in comments[index[0]]:
                            comments[index[0]][major_id] = []
                        # Missing [number of missing credit points] credit points for [rule id]
                        comments[index[0]][major_id].append(f'Missing {required_credit_points - current_credit_points} credit points for rule {rule[0]}')
                        major_eligable = False

                    # Find all the units that are 0 credit points
                    # Check that the student has completed it
                    # Otherwise major_eligable = False, and add a comment 


                if major_eligable:
                    eligable = True
                    if index[0] not in student_eligable:
                        student_eligable[index[0]] = []
                    student_eligable[index[0]].append(major_id)
            if not eligable:
                if index[0] not in student_eligable:
                    student_eligable[index[0]] = []
                student_eligable[index[0]].append('Not Eligable')

        print(comments)
        print(student_eligable)

        # Filter out rows with missing or None values and for Level 3/4/5 units
        relevant_data_adjusted = input_data.dropna(subset=['Adjusted_Mark', 'Relevant_Credit_Points'])
        relevant_units_adjusted = relevant_data_adjusted[relevant_data_adjusted['Unit_Code'].str[4].isin(['3', '4', '5'])]

        # Get the major - make sure that the unitcode is in the major
        # Filter out units that are not in the major
        relevant_units_adjusted = relevant_units_adjusted[relevant_units_adjusted.apply(lambda x: self.handbookDB.unit_in_major(x['Unit_Code'], x['Major_Deg']), axis=1)]

        # Calculate the EH-WAM
        eh_wam_values_adjusted = relevant_units_adjusted.groupby('Person_ID').apply(
            lambda x: (x['Adjusted_Mark'] * x['Relevant_Credit_Points']).sum() / x['Relevant_Credit_Points'].sum()
        )

        # TESTING
        # For 23001000, print the calculation of the EH-WAM with each row
        user = relevant_units_adjusted[relevant_units_adjusted['Person_ID'] == 23002002]
        user['Mark x Credit Points'] = user['Adjusted_Mark'] * user['Relevant_Credit_Points']
        # prints each row with the calculation
        # for index, row in user.iterrows():
            # print(f'{row["Unit_Code"]} - {row["Mark x Credit Points"]} / {row["Relevant_Credit_Points"]}')

        eh_wam_adjusted = pd.DataFrame(eh_wam_values_adjusted, columns=['EH-WAM']).reset_index()
        eh_wam_adjusted['EH-WAM'] = eh_wam_adjusted['EH-WAM'].round(3)

        # Determine GENG4412 completion and mark for each student
        geng4412_data = input_data[input_data['Unit_Code'] == 'GENG4412'][['Person_ID', 'Mark']]
        merged_data_adjusted = pd.merge(eh_wam_adjusted, geng4412_data, on='Person_ID', how='left')

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

        print(f"\033[91m{merged_data_adjusted}\033[00m")

        # Add in comments only if the student is not eligable
        for index, row in merged_data_adjusted.iterrows():
            person_id = int(row['Person_ID'])
            if person_id in comments:
                if student_eligable[person_id][0] == 'Not Eligable':
                    merged_data_adjusted.at[index, 'Missing Information (Y/N)'] = 'Y'
                    comment_string = ''
                    for major_id in comments[person_id]:
                        comment_string += ', '.join(comments[person_id][major_id])
                        comment_string += '\n'
                    merged_data_adjusted.at[index, 'Comments (missing information)'] = comment_string
            else:
                merged_data_adjusted.at[index, 'Missing Information (Y/N)'] = 'N'
                merged_data_adjusted.at[index, 'Comments (missing information)'] = ''

        # Order of columns
        merged_data_adjusted = merged_data_adjusted[['Person_ID', 'Surname', 'Given Names', 'Course_Code', 'Course_Title', 'Major_Deg', 'Completed GENG4412 (Y/N)','GENG4412 Mark', 'EH-WAM',  'Honours Class', 'Missing Information (Y/N)', 'Comments (missing information)']]
        # Save the processed data to an output Excel file (optional)
        with ExcelWriter(output_filepath, engine='openpyxl') as writer:
            merged_data_adjusted.to_excel(writer, index=False, sheet_name='Sheet1')

            # Access the workbook and worksheet to set the auto-filter
            worksheet = writer.sheets['Sheet1']
            worksheet.auto_filter.ref = worksheet.dimensions


        return merged_data_adjusted
    
    # Need to implement handbook db into wam calculations
    # Eligability checks and process into comments
    '''
    We want
    Eligability checks:
    - For each rule, check that the student has enough credit points to satisfy the rule

    We need:
    1. way to get unit rules from a major using the handbook db
    2. way to get a students units from the input data
    
    only level 3,4,5 units in their major
    other units are ignored - different levels and broadening units
    SUM[unit mark x credit points] / sum(credit points) = eh-wam
    additional requirements - geng >= 80, geng >= 70, must have geng
    all attempts are included - except UP/UF ignored

    1. Time
    2. Majors

    # Get every unique person id x major
    # For each person id x major, get all the units they have done
    '''