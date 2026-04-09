"""
algorithms.py – Searching and Sorting algorithms for the Student Grade Tracker.

Contains:
  - bubble_sort()  : Sorts a list of student dictionaries by name or average.
  - linear_search(): Searches for a student by name (partial match).
  - calculate_average(): Computes the mean of a list of grades.
  - get_grade_letter(): Converts a numeric average to a letter grade.

References:
  - Bubble Sort explanation: https://www.w3schools.com/python/python_intro.asp
  - Python list operations: https://docs.python.org/3/tutorial/datastructures.html
"""


def calculate_average(grades):
    """
    Calculate the average of a list of numeric grades.

    Args:
        grades (list[float]): A list of grade values.

    Returns:
        float: The average rounded to 2 decimal places, or 0.0 if the list is empty.
    """
    if not grades:
        return 0.0
    return round(sum(grades) / len(grades), 2)


def get_grade_letter(average):
    """
    Convert a numeric average into a letter grade using UK-style boundaries.

    Grade boundaries:
        A  >= 70
        B  >= 60
        C  >= 50
        D  >= 40
        F  < 40

    Args:
        average (float): The numeric average grade.

    Returns:
        str: A letter grade string ('A', 'B', 'C', 'D', or 'F').
    """
    if average >= 70:
        return 'A'
    elif average >= 60:
        return 'B'
    elif average >= 50:
        return 'C'
    elif average >= 40:
        return 'D'
    else:
        return 'F'


def bubble_sort(students, key='name', reverse=False):
    """
    Sort a list of student dictionaries using the Bubble Sort algorithm.

    Bubble Sort works by repeatedly comparing adjacent elements and swapping
    them if they are in the wrong order. The algorithm is O(n²) in the worst
    case but stops early if no swaps are made in a pass (optimised form).

    Args:
        students (list[dict]): List of student dictionaries.
        key (str): Sorting key – 'name' (alphabetical) or 'average' (numeric).
        reverse (bool): If True, sorts in descending order.

    Returns:
        list[dict]: A new sorted list (the original is not modified).
    """
    # Work on a shallow copy so the original list is unchanged
    arr = students.copy()
    n = len(arr)

    for i in range(n):
        swapped = False  # Optimisation: stop early if already sorted

        for j in range(0, n - i - 1):
            # Determine the comparison values for adjacent elements
            if key == 'average':
                val_a = calculate_average(arr[j]['grades'])
                val_b = calculate_average(arr[j + 1]['grades'])
            else:  # Default: sort by name (case-insensitive)
                val_a = arr[j]['name'].lower()
                val_b = arr[j + 1]['name'].lower()

            # Swap if the current element should come after the next one
            should_swap = (val_a > val_b) if not reverse else (val_a < val_b)
            if should_swap:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True

        # If no swaps were made, the list is already sorted
        if not swapped:
            break

    return arr


def linear_search(students, query):
    """
    Search for students whose name contains the given query string.

    Linear Search scans every element in the list sequentially. It is O(n)
    and supports partial, case-insensitive matching.

    Args:
        students (list[dict]): List of student dictionaries.
        query (str): The search string (can be a partial name).

    Returns:
        list[dict]: A list of student dictionaries whose name matches the query.
    """
    results = []
    query_lower = query.lower().strip()

    for student in students:
        # Partial, case-insensitive name match
        if query_lower in student['name'].lower():
            results.append(student)

    return results
