def calculate_average(grades):
 
    if not grades:
        return 0.0
    return round(sum(grades) / len(grades), 2)


def get_grade_letter(average):
 
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
 
    results = []
    query_lower = query.lower().strip()

    for student in students:
        # Partial, case-insensitive name match
        if query_lower in student['name'].lower():
            results.append(student)

    return results
