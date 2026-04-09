# Student Grade Tracker

**Author      :** Nesibe Kubra Cakir
**P-Number    :** P499632  
**Course Code :** IY499 – Introduction to Programming  
**GitHub      :** https://github.com/cakkirnesibe-byte/Student-Grade-Tracker 

---

## Declaration of Own Work

I confirm that this assignment is my own work.  
Where I have referred to online sources, I have provided comments detailing the reference and included a link to the source.

---

## Description

The **Student Grade Tracker** is a desktop application that allows a teacher to record, manage, and analyse student grades through a clean, tabbed graphical interface built with Python and Tkinter.

The application has four main sections:

1. **Students** – Add grades for existing or new students, view the full list (sorted by name or average using a custom *bubble sort* implementation), and remove students.
2. **Search** – Find students by name instantly using a *linear search* algorithm that supports partial, case-insensitive matching.
3. **Visualise** – Generate three types of Matplotlib charts embedded directly in the window: a bar chart of student averages, a pie chart showing the A/B/C/D/F grade-band split, and a histogram of all individual grades entered.
4. **Report** – View live class statistics (class average, pass rate, top/bottom student) and export a full sorted report to a `.txt` file.

All data is automatically saved to `students.json` so records persist between sessions. The JSON file is created automatically on first use.

---

## Libraries Used

| Library | Purpose | Install via pip |
|---------|---------|-----------------|
| `tkinter` | GUI framework – windows, tabs, buttons, treeviews | Built into Python |
| `matplotlib` | Data visualisation – bar, pie and histogram charts | `pip install matplotlib` |
| `json` | Saving and loading student data | Built into Python |
| `os` | Checking whether the data file exists | Built into Python |
| `datetime` | Timestamps for records and reports | Built into Python |
| `re` | Validating student name input | Built into Python |

---

## Installation Instructions

1. Ensure **Python 3.8 or higher** is installed.  
   Download: https://www.python.org/downloads/

2. Clone or download this repository and unzip it into a folder.

3. Open a terminal (Command Prompt / PowerShell / Terminal) inside that folder.

4. Install the required external package:

```bash
pip install -r requirements.txt
```

---

## How to Run

From the project folder, run:

```bash
python main.py
```

The application window will open immediately. No additional setup is needed.

---

## Project File Structure

```
StudentGradeTracker/
├── main.py          # Main application – Tkinter GUI
├── algorithms.py    # Bubble sort, linear search, helper functions
├── file_handler.py  # JSON file loading, saving, and report export
├── requirements.txt # External Python packages
├── README.md        # This file
└── students.json    # Created automatically when you first add a student
```

---

## How to Use

- **Add a grade:** Type a name and a numeric grade (0–100) in the *Students* tab, then click *Add Grade*. Pressing Enter in any field also submits.
- **Sort the list:** Use the radio buttons and *Descending* checkbox to re-order by name or average.
- **Remove a student:** Click a row in the list to select it, then click *Remove Selected Student*.
- **Search:** Switch to the *Search* tab, type part of a name, and press *Search* or *Show All*.
- **View charts:** Switch to the *Visualise* tab, choose a chart type, and click *Generate Chart*.
- **Export a report:** Switch to the *Report* tab and click *Export Report to File*. A `.txt` file is saved in the same directory.
