"""
file_handler.py – File handling for the Student Grade Tracker.

Responsibilities:
  - load_students()   : Read student records from a JSON file.
  - save_students()   : Write student records to a JSON file.
  - export_report()   : Write a plain-text summary report to disk.

All functions include error handling so that file corruption or permission
problems do not crash the application.

References:
  - Python json module: https://docs.python.org/3/library/json.html
  - Python open() / file modes: https://docs.python.org/3/library/functions.html#open
  - os.path module: https://docs.python.org/3/library/os.path.html
"""

import json
import os
from datetime import datetime

from algorithms import bubble_sort, calculate_average, get_grade_letter

# Path to the persistent data file
DATA_FILE = 'students.json'


def load_students():
    """
    Load student records from the JSON data file.

    If the file does not exist, an empty list is returned so the application
    can start fresh without raising an exception.

    Returns:
        list[dict]: A list of student dictionaries, or [] on failure.
    """
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
    """
    Save the full list of student records to the JSON data file.

    The file is overwritten on each save. A 'last_updated' timestamp is
    included in the JSON for auditing purposes.

    Args:
        students (list[dict]): The student records to persist.

    Returns:
        bool: True if saved successfully, False if an error occurred.
    """
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
    """
    Export a sorted, human-readable grade report to a plain-text file.

    Students are sorted by average grade (highest first) using bubble_sort.

    Args:
        students (list[dict]): The student records to include in the report.
        filename (str | None): Output filename. Defaults to a timestamped name.

    Returns:
        str | None: The filename that was written, or None on failure.
    """
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
