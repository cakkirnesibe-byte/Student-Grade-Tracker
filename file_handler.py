import json
import os
from datetime import datetime

from algorithms import bubble_sort, calculate_average, get_grade_letter

# Path to the persistent data file
DATA_FILE = 'students.json'


def load_students():
 
    try:
        if not os.path.exists(DATA_FILE):
            return []  # No data file yet – first run

        with open(DATA_FILE, 'r') as f:
            data = json.load(f)

        # Guard against a malformed file that is missing the 'students' key
        return data.get('students', [])

    except json.JSONDecodeError:
        # File exists but contains invalid JSON – treat as empty
        print(f"[Warning] '{DATA_FILE}' is corrupted and could not be read.")
        return []

    except IOError as e:
        print(f"[Error] Could not open '{DATA_FILE}': {e}")
        return []


def save_students(students):

    try:
        payload = {
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'students': students
        }

        with open(DATA_FILE, 'w') as f:
            json.dump(payload, f, indent=4)

        return True

    except IOError as e:
        print(f"[Error] Could not save data: {e}")
        return False


def export_report(students, filename=None):

    if filename is None:
        # Auto-generate a timestamped filename so reports don't overwrite each other
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'grade_report_{timestamp}.txt'

    try:
        # Sort students by average grade (highest first) for the report
        sorted_students = bubble_sort(students, key='average', reverse=True)

        with open(filename, 'w') as f:
            # Header section
            f.write('=' * 55 + '\n')
            f.write('         STUDENT GRADE TRACKER – FULL REPORT\n')
            f.write(f'  Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write('=' * 55 + '\n\n')

            # Class summary
            all_avgs = [calculate_average(s['grades']) for s in students]
            f.write(f'Total Students : {len(students)}\n')
            if all_avgs:
                f.write(f'Class Average  : {calculate_average(all_avgs):.2f}%\n')
                f.write(f'Highest Average: {max(all_avgs):.2f}%\n')
                f.write(f'Lowest Average : {min(all_avgs):.2f}%\n')
                pass_count = sum(1 for a in all_avgs if a >= 50)
                f.write(f'Pass Rate (≥50): {pass_count}/{len(all_avgs)}\n')
            f.write('\n' + '-' * 55 + '\n\n')

            # Individual student entries
            for rank, student in enumerate(sorted_students, start=1):
                avg = calculate_average(student['grades'])
                letter = get_grade_letter(avg)
                grades_str = ', '.join(str(g) for g in student['grades'])

                f.write(f'#{rank}  {student["name"]}\n')
                f.write(f'    Grades  : {grades_str}\n')
                f.write(f'    Average : {avg:.2f}%  ({letter})\n')
                f.write(f'    Added   : {student.get("added_date", "N/A")}\n\n')

            f.write('=' * 55 + '\n')
            f.write('               End of Report\n')
            f.write('=' * 55 + '\n')

        return filename

    except IOError as e:
        print(f"[Error] Could not write report '{filename}': {e}")
        return None
