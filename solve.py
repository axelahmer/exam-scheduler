import pandas as pd
import clingo
import os

# Load the enrolments data
enrolments_data = pd.read_csv(
    'nott/enrolements', sep=' ', header=None, names=['student_code', 'exam_code'])

# Load and process the exams data


def parse_exams_row(row):
    exam_code = row[:8].strip().lower()
    description = row[8:50].strip()
    # Adjusted slicing to capture the duration correctly
    duration_str = row[50:54].strip()
    department_code = row[54:].strip()

    # Convert duration to minutes
    hours, minutes = map(int, duration_str.split(':'))
    duration = hours * 60 + minutes

    return exam_code, description, duration, department_code


with open('nott/exams', 'r') as file:
    exams_data = [parse_exams_row(line) for line in file]

exams_df = pd.DataFrame(exams_data, columns=[
                        'exam_code', 'description', 'duration', 'department_code'])

# Define the timeslots and their durations
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
times = [("9:00", 180), ("13:30", 120), ("16:30", 120)]
day_ids = [1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13]

timeslots = []
timeslot_id = 1

for day_id, day in zip(day_ids, days * 2):
    if day == "Sat":
        timeslots.append((timeslot_id, day_id, f"{day} 9:00", 180))
        timeslot_id += 1
    else:
        for time, duration in times:
            timeslots.append((timeslot_id, day_id, f"{day} {time}", duration))
            timeslot_id += 1

# Generate Clingo data
clingo_data = []

# Add exam atoms with duration in minutes
for _, row in exams_df.iterrows():
    exam_code = row['exam_code']
    duration = row['duration']
    clingo_data.append(f"exam({exam_code},{duration}).")

# Add student atoms
students = enrolments_data['student_code'].unique()
for student in students:
    clingo_data.append(f"student({student.lower()}).")

# Add enrolled atoms
for _, row in enrolments_data.iterrows():
    student_code = row['student_code'].lower()
    exam_code = row['exam_code'].lower()
    clingo_data.append(f"enrolled({student_code},{exam_code}).")

# Add timeslot atoms
for timeslot_id, day_id, timeslot_name, timeslot_duration in timeslots:
    clingo_data.append(
        f"timeslot({timeslot_id},{day_id},{timeslot_duration}).")

# Write Clingo data to file
with open('clingo_data.lp', 'w') as file:
    file.write("\n".join(clingo_data))

print("Clingo data file 'clingo_data.lp' has been created.")

# Run Clingo solver
ctl = clingo.Control(["-t 8"])
ctl.load("solve.lp")
ctl.load("clingo_data.lp")
ctl.ground([("base", [])])

# Solve and print the results


with ctl.solve(yield_=True) as handle:
    for model in handle:
        cost = model.cost[0] if model.cost else 0
        print("Optimization result:", cost)
        assignments = []
        for atom in model.symbols(shown=True):
            if atom.name == "assign":
                exam, timeslot = atom.arguments
                assignments.append((timeslot.number, exam.name))

        # Save the assignments
        os.makedirs('results', exist_ok=True)
        result_file = f'results/result_{cost}.csv'
        with open(result_file, 'w') as f:
            f.write("timeslot,exam\n")
            for timeslot, exam in assignments:
                f.write(f"{timeslot},{exam}\n")
        print(f"Assignments saved to {result_file}")
