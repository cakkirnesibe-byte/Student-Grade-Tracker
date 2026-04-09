import tkinter as tk
from tkinter import ttk, messagebox
import re
from datetime import datetime

import matplotlib
matplotlib.use('TkAgg')  # Use the Tkinter backend for Matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Local modules
from algorithms import bubble_sort, linear_search, calculate_average, get_grade_letter
from file_handler import load_students, save_students, export_report


# ──────────────────────────────────────────────────────────────────────────────
#  Application Class
# ──────────────────────────────────────────────────────────────────────────────

class StudentTrackerApp:

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Student Grade Tracker – IY499")
        self.root.geometry("960x680")
        self.root.minsize(860, 600)
        self.root.configure(bg='#ecf0f1')

        # Load existing student data from the JSON file on disk
        self.students = load_students()

        # Chart canvas reference (kept so we can destroy it before redrawing)
        self._chart_canvas = None

        self._apply_styles()
        self._build_notebook()
        self._build_tab_students()
        self._build_tab_search()
        self._build_tab_visualise()
        self._build_tab_report()

        # Populate the student list immediately on startup
        self._refresh_student_list()
        self._update_stats()

    # ── Styles ────────────────────────────────────────────────────────────────

    def _apply_styles(self) -> None:
        style = ttk.Style()
        style.theme_use('clam')

        # Notebook tabs
        style.configure('TNotebook.Tab',
                         padding=[14, 6],
                         font=('Helvetica', 10, 'bold'))

        # Buttons
        style.configure('TButton',
                         padding=[10, 5],
                         font=('Helvetica', 9))

        # Labels
        style.configure('Header.TLabel',
                         font=('Helvetica', 13, 'bold'),
                         foreground='#2c3e50')

        # Treeview rows – alternating colours set via tags later
        style.configure('Treeview',
                         rowheight=24,
                         font=('Helvetica', 9))
        style.configure('Treeview.Heading',
                         font=('Helvetica', 9, 'bold'))

    # ── Notebook ──────────────────────────────────────────────────────────────

    def _build_notebook(self) -> None:
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=12, pady=12)

    # ── Tab 1 : Students ──────────────────────────────────────────────────────

    def _build_tab_students(self) -> None:
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='📋  Students')

        # ── Left panel: input form ─────────────────────────────────────────
        form = ttk.LabelFrame(tab, text='Add Grade for Student', padding=12)
        form.pack(side='left', fill='y', padx=(10, 5), pady=10)

        fields = [
            ('Student Name:', 'entry_name'),
            ('Grade  (0 – 100):', 'entry_grade'),
            ('Subject (optional):', 'entry_subject'),
        ]
        for row_idx, (label_text, attr) in enumerate(fields):
            ttk.Label(form, text=label_text).grid(row=row_idx, column=0,
                                                   sticky='w', pady=5)
            entry = ttk.Entry(form, width=22)
            entry.grid(row=row_idx, column=1, pady=5, padx=(8, 0))
            setattr(self, attr, entry)

        # Bind Enter key to add_grade for faster data entry
        for attr in ('entry_name', 'entry_grade', 'entry_subject'):
            getattr(self, attr).bind('<Return>', lambda _e: self.add_grade())

        ttk.Separator(form, orient='horizontal').grid(
            row=3, column=0, columnspan=2, sticky='ew', pady=10)

        ttk.Button(form, text='✚  Add Grade',
                   command=self.add_grade).grid(
            row=4, column=0, columnspan=2, sticky='ew', pady=3)

        ttk.Button(form, text='✖  Remove Selected Student',
                   command=self.remove_student).grid(
            row=5, column=0, columnspan=2, sticky='ew', pady=3)

        ttk.Button(form, text='⌫  Clear Fields',
                   command=self.clear_fields).grid(
            row=6, column=0, columnspan=2, sticky='ew', pady=3)

        # ── Sort controls ──────────────────────────────────────────────────
        ttk.Separator(form, orient='horizontal').grid(
            row=7, column=0, columnspan=2, sticky='ew', pady=10)

        ttk.Label(form, text='Sort By:', font=('Helvetica', 9, 'bold')).grid(
            row=8, column=0, sticky='w')

        self._sort_key = tk.StringVar(value='name')
        for col_idx, (label_text, val) in enumerate(
                [('Name', 'name'), ('Average', 'average')]):
            ttk.Radiobutton(form, text=label_text,
                            variable=self._sort_key, value=val,
                            command=self._refresh_student_list).grid(
                row=8 + col_idx, column=1, sticky='w')

        self._sort_desc = tk.BooleanVar(value=False)
        ttk.Checkbutton(form, text='Descending',
                        variable=self._sort_desc,
                        command=self._refresh_student_list).grid(
            row=10, column=0, columnspan=2, pady=6)

        # ── Right panel: student treeview ──────────────────────────────────
        list_frame = ttk.LabelFrame(tab, text='All Students', padding=10)
        list_frame.pack(side='right', fill='both', expand=True,
                        padx=(5, 10), pady=10)

        cols = ('Name', 'Recent Grades', 'Average', 'Grade')
        self._tree = ttk.Treeview(list_frame, columns=cols,
                                   show='headings', height=20)
        widths = (180, 220, 100, 80)
        for col, w in zip(cols, widths):
            self._tree.heading(col, text=col)
            self._tree.column(col, width=w, anchor='center')
        self._tree.column('Name', anchor='w')

        # Alternating row colours (tag-based)
        self._tree.tag_configure('odd',  background='#ffffff')
        self._tree.tag_configure('even', background='#eaf4fb')

        vsb = ttk.Scrollbar(list_frame, orient='vertical',
                             command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')

        # Clicking a row pre-fills the name field
        self._tree.bind('<<TreeviewSelect>>', self._on_row_select)

    # ── Tab 2 : Search ────────────────────────────────────────────────────────

    def _build_tab_search(self) -> None:
        """Build the Search tab (linear search by name)."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='🔍  Search')

        # ── Search bar ─────────────────────────────────────────────────────
        bar = ttk.LabelFrame(tab, text='Search Students by Name', padding=10)
        bar.pack(fill='x', padx=10, pady=10)

        self._search_var = tk.StringVar()
        ttk.Entry(bar, textvariable=self._search_var, width=35,
                  font=('Helvetica', 10)).pack(side='left', padx=(0, 8))

        ttk.Button(bar, text='Search',
                   command=self.search_students).pack(side='left', padx=4)
        ttk.Button(bar, text='Show All',
                   command=self.show_all_in_search).pack(side='left', padx=4)

        # Pressing Enter triggers the search
        self._search_var.trace_add('write',
                                    lambda *_: None)  # placeholder for live search
        bar.bind('<Return>', lambda _e: self.search_students())

        # ── Results treeview ───────────────────────────────────────────────
        res_frame = ttk.LabelFrame(tab, text='Results', padding=10)
        res_frame.pack(fill='both', expand=True, padx=10, pady=5)

        cols = ('Name', 'All Grades', 'Average', 'Grade', 'Date Added')
        self._search_tree = ttk.Treeview(res_frame, columns=cols,
                                          show='headings', height=16)
        widths = (160, 240, 100, 80, 160)
        for col, w in zip(cols, widths):
            self._search_tree.heading(col, text=col)
            self._search_tree.column(col, width=w, anchor='center')
        self._search_tree.column('Name', anchor='w')

        vsb2 = ttk.Scrollbar(res_frame, orient='vertical',
                              command=self._search_tree.yview)
        self._search_tree.configure(yscrollcommand=vsb2.set)
        self._search_tree.pack(side='left', fill='both', expand=True)
        vsb2.pack(side='right', fill='y')

        # Status label below results
        self._search_status = ttk.Label(tab, text='', font=('Helvetica', 9))
        self._search_status.pack(pady=4)

    # ── Tab 3 : Visualise ─────────────────────────────────────────────────────

    def _build_tab_visualise(self) -> None:
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='📊  Visualise')

        # ── Chart type selector ────────────────────────────────────────────
        ctrl = ttk.Frame(tab)
        ctrl.pack(fill='x', padx=10, pady=8)

        ttk.Label(ctrl, text='Chart Type:',
                  font=('Helvetica', 9, 'bold')).pack(side='left', padx=(0, 8))

        self._chart_type = tk.StringVar(value='bar')
        chart_options = [
            ('Bar Chart (averages)', 'bar'),
            ('Pie  (A/B/C/D/F split)', 'pie'),
            ('Histogram (all grades)', 'hist'),
        ]
        for label_text, val in chart_options:
            ttk.Radiobutton(ctrl, text=label_text,
                            variable=self._chart_type, value=val).pack(
                side='left', padx=6)

        ttk.Button(ctrl, text='Generate Chart ▶',
                   command=self.generate_chart).pack(side='right', padx=10)

        # ── Canvas area for the embedded chart ────────────────────────────
        self._chart_frame = ttk.Frame(tab)
        self._chart_frame.pack(fill='both', expand=True, padx=10, pady=5)

    # ── Tab 4 : Report ────────────────────────────────────────────────────────

    def _build_tab_report(self) -> None:
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='📄  Report')

        stats_lf = ttk.LabelFrame(tab, text='Class Statistics', padding=12)
        stats_lf.pack(fill='x', padx=10, pady=10)

        # Read-only text widget for statistics
        self._stats_box = tk.Text(
            stats_lf, height=12, width=62,
            state='disabled',
            font=('Courier New', 10),
            bg='#f4f6f7', relief='flat',
            wrap='none'
        )
        self._stats_box.pack(fill='x')

        # Action buttons
        btn_row = ttk.Frame(tab)
        btn_row.pack(pady=8)

        ttk.Button(btn_row, text='🔄  Refresh Statistics',
                   command=self._update_stats).pack(side='left', padx=6)
        ttk.Button(btn_row, text='💾  Export Report to File',
                   command=self.do_export_report).pack(side='left', padx=6)

    # ──────────────────────────────────────────────────────────────────────────
    #  Event Handlers / Business Logic
    # ──────────────────────────────────────────────────────────────────────────

    def add_grade(self) -> None:
        name      = self.entry_name.get().strip()
        grade_str = self.entry_grade.get().strip()
        subject   = self.entry_subject.get().strip() or 'General'

        # ── Input validation ───────────────────────────────────────────────
        if not name:
            messagebox.showerror("Input Error", "Please enter a student name.")
            self.entry_name.focus()
            return

        # Name may only contain letters and spaces
        if not re.match(r'^[A-Za-z\s\-]+$', name):
            messagebox.showerror(
                "Input Error",
                "Student name must contain only letters, spaces, or hyphens.")
            return

        if not grade_str:
            messagebox.showerror("Input Error", "Please enter a grade.")
            self.entry_grade.focus()
            return

        try:
            grade = float(grade_str)
            if not (0.0 <= grade <= 100.0):
                raise ValueError("Out of range")
        except ValueError:
            messagebox.showerror(
                "Input Error", "Grade must be a number between 0 and 100.")
            return

        grade = round(grade, 1)

        # ── Find or create the student ─────────────────────────────────────
        student = self._find_student(name)

        if student:
            student['grades'].append(grade)
            student.setdefault('grade_details', []).append({
                'grade': grade,
                'subject': subject,
                'date': datetime.now().strftime('%Y-%m-%d')
            })
        else:
            self.students.append({
                'name': name.title(),
                'grades': [grade],
                'grade_details': [{
                    'grade': grade,
                    'subject': subject,
                    'date': datetime.now().strftime('%Y-%m-%d')
                }],
                'added_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

        # ── Persist and refresh ────────────────────────────────────────────
        if save_students(self.students):
            self._refresh_student_list()
            self._update_stats()
            self.clear_fields()
            messagebox.showinfo(
                "Grade Added",
                f"Grade {grade} added for {name.title()} ({subject}).")
        else:
            messagebox.showerror(
                "Save Error", "Grade was added in memory but could not be saved to file.")

    def remove_student(self) -> None:
        selection = self._tree.selection()
        if not selection:
            messagebox.showwarning(
                "No Selection", "Please click on a student in the list first.")
            return

        name = self._tree.item(selection[0])['values'][0]

        confirmed = messagebox.askyesno(
            "Confirm Removal",
            f"Permanently remove '{name}' and all their grades?\n"
            "This action cannot be undone.")
        if not confirmed:
            return

        self.students = [s for s in self.students if s['name'] != name]

        if save_students(self.students):
            self._refresh_student_list()
            self._update_stats()
            messagebox.showinfo("Removed", f"'{name}' has been removed.")
        else:
            messagebox.showerror("Save Error", "Student removed from memory but file could not be updated.")

    def clear_fields(self) -> None:
        """Clear all input fields in the Students tab."""
        for attr in ('entry_name', 'entry_grade', 'entry_subject'):
            getattr(self, attr).delete(0, 'end')
        self.entry_name.focus()

    def search_students(self) -> None:
        query = self._search_var.get().strip()

        if not query:
            messagebox.showwarning("Empty Query", "Please type a name to search for.")
            return

        # Linear search (from algorithms.py)
        results = linear_search(self.students, query)

        self._populate_search_tree(results)

        count = len(results)
        self._search_status.config(
            text=f"  Found {count} student(s) matching '{query}'.",
            foreground='#27ae60' if count > 0 else '#e74c3c')

    def show_all_in_search(self) -> None:
        self._search_var.set('')
        self._populate_search_tree(self.students)
        self._search_status.config(
            text=f"  Showing all {len(self.students)} student(s).",
            foreground='#2980b9')

    def generate_chart(self) -> None:
        if not self.students:
            messagebox.showwarning(
                "No Data", "Add some students first before generating a chart.")
            return

        # Destroy the previous chart widget if one exists
        if self._chart_canvas is not None:
            self._chart_canvas.get_tk_widget().destroy()
            self._chart_canvas = None

        fig, ax = plt.subplots(figsize=(8.5, 4.8))
        fig.patch.set_facecolor('#ecf0f1')
        ax.set_facecolor('#fdfefe')

        chart = self._chart_type.get()

        try:
            if chart == 'bar':
                # Bar chart – students sorted by average (highest first)
                sorted_s = bubble_sort(self.students, key='average', reverse=True)
                names    = [s['name'].split()[0] for s in sorted_s]  # first name only
                avgs     = [calculate_average(s['grades']) for s in sorted_s]
                colours  = ['#2ecc71' if a >= 50 else '#e74c3c' for a in avgs]

                bars = ax.bar(names, avgs, color=colours, edgecolor='white',
                              linewidth=0.8, zorder=3)

                # Grade labels on top of each bar
                for bar, val in zip(bars, avgs):
                    ax.text(bar.get_x() + bar.get_width() / 2,
                            bar.get_height() + 1.2,
                            f'{val:.1f}%',
                            ha='center', va='bottom',
                            fontsize=8, fontweight='bold', color='#2c3e50')

                ax.axhline(y=50, color='#e67e22', linestyle='--',
                           linewidth=1.2, alpha=0.8, label='Pass mark (50%)', zorder=2)
                ax.set_ylim(0, 115)
                ax.set_xlabel('Student', fontsize=10)
                ax.set_ylabel('Average Grade (%)', fontsize=10)
                ax.set_title('Student Average Grades', fontsize=12, fontweight='bold')
                ax.legend(fontsize=9)
                ax.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
                plt.xticks(rotation=30, ha='right', fontsize=8)

            elif chart == 'pie':
                # Pie chart – distribution across letter grades
                counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
                for s in self.students:
                    counts[get_grade_letter(calculate_average(s['grades']))] += 1

                labels = [k for k, v in counts.items() if v > 0]
                sizes  = [counts[k] for k in labels]
                pal    = ['#2ecc71', '#3498db', '#f39c12', '#e67e22', '#e74c3c']
                cols   = [pal[['A', 'B', 'C', 'D', 'F'].index(l)] for l in labels]

                ax.pie(sizes, labels=labels, colors=cols,
                       autopct='%1.1f%%', startangle=90,
                       textprops={'fontsize': 10})
                ax.set_title('Grade Band Distribution (A / B / C / D / F)',
                             fontsize=12, fontweight='bold')

            elif chart == 'hist':
                # Histogram – all individual grades entered
                all_grades = [g for s in self.students for g in s['grades']]

                ax.hist(all_grades, bins=10, range=(0, 100),
                        color='#3498db', edgecolor='white',
                        linewidth=0.8, zorder=3)
                ax.axvline(x=50, color='#e74c3c', linestyle='--',
                           linewidth=1.2, label='Pass mark (50)', zorder=4)
                ax.set_xlabel('Grade (%)', fontsize=10)
                ax.set_ylabel('Number of Grades', fontsize=10)
                ax.set_title('Grade Frequency Distribution',
                             fontsize=12, fontweight='bold')
                ax.legend(fontsize=9)
                ax.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)

            plt.tight_layout()

            # Embed the Matplotlib figure inside the Tkinter frame
            self._chart_canvas = FigureCanvasTkAgg(fig, master=self._chart_frame)
            self._chart_canvas.draw()
            self._chart_canvas.get_tk_widget().pack(fill='both', expand=True)

        except Exception as exc:
            messagebox.showerror("Chart Error",
                                 f"Could not render chart:\n{exc}")
        finally:
            # Always close the figure to free memory
            plt.close(fig)

    def do_export_report(self) -> None:
        if not self.students:
            messagebox.showwarning("No Data", "No student records to export.")
            return

        filename = export_report(self.students)

        if filename:
            messagebox.showinfo(
                "Export Successful",
                f"Report saved as:\n{filename}")
        else:
            messagebox.showerror(
                "Export Failed",
                "The report could not be written.\n"
                "Check you have write permission in this directory.")

    # ──────────────────────────────────────────────────────────────────────────
    #  Internal / Helper Methods
    # ──────────────────────────────────────────────────────────────────────────

    def _find_student(self, name: str):
        target = name.lower().strip()
        for s in self.students:
            if s['name'].lower() == target:
                return s
        return None

    def _refresh_student_list(self) -> None:
        # Remove all existing rows
        for row in self._tree.get_children():
            self._tree.delete(row)

        # Sort using our bubble_sort implementation
        sorted_students = bubble_sort(
            self.students,
            key=self._sort_key.get(),
            reverse=self._sort_desc.get()
        )

        for idx, student in enumerate(sorted_students):
            avg    = calculate_average(student['grades'])
            letter = get_grade_letter(avg)

            # Show last 5 grades to keep the column readable
            recent = student['grades'][-5:]
            grades_str = ', '.join(str(g) for g in recent)
            if len(student['grades']) > 5:
                grades_str = '… ' + grades_str

            tag = 'even' if idx % 2 == 0 else 'odd'
            self._tree.insert('', 'end', tags=(tag,), values=(
                student['name'],
                grades_str,
                f'{avg:.1f}%',
                letter
            ))

    def _populate_search_tree(self, results: list) -> None:
        for row in self._search_tree.get_children():
            self._search_tree.delete(row)

        for student in results:
            avg        = calculate_average(student['grades'])
            letter     = get_grade_letter(avg)
            grades_str = ', '.join(str(g) for g in student['grades'])

            self._search_tree.insert('', 'end', values=(
                student['name'],
                grades_str,
                f'{avg:.1f}%',
                letter,
                student.get('added_date', 'N/A')
            ))

    def _update_stats(self) -> None:
        self._stats_box.config(state='normal')
        self._stats_box.delete('1.0', 'end')

        if not self.students:
            self._stats_box.insert(
                'end',
                "  No students recorded yet.\n\n"
                "  Switch to the '📋 Students' tab to add student grades.")
            self._stats_box.config(state='disabled')
            return

        all_avgs   = [calculate_average(s['grades']) for s in self.students]
        all_grades = [g for s in self.students for g in s['grades']]
        pass_count = sum(1 for a in all_avgs if a >= 50)

        # Sort to find top/bottom students
        ranked = bubble_sort(self.students, key='average', reverse=True)
        top_name = ranked[0]['name']
        top_avg  = calculate_average(ranked[0]['grades'])
        bot_name = ranked[-1]['name']
        bot_avg  = calculate_average(ranked[-1]['grades'])

        lines = [
            '  ' + '=' * 50,
            '         CLASS STATISTICS',
            f'  Generated : {datetime.now().strftime("%Y-%m-%d  %H:%M:%S")}',
            '  ' + '=' * 50,
            f'  Total Students    : {len(self.students)}',
            f'  Total Grades      : {len(all_grades)}',
            f'  Class Average     : {calculate_average(all_avgs):.2f}%',
            f'  Highest Average   : {max(all_avgs):.2f}%',
            f'  Lowest Average    : {min(all_avgs):.2f}%',
            f'  Pass Rate (≥50%)  : {pass_count} / {len(self.students)}',
            '  ' + '-' * 50,
            f'  🏆 Top Student    : {top_name}  ({top_avg:.2f}%  |  {get_grade_letter(top_avg)})',
            f'  📉 Needs Support  : {bot_name}  ({bot_avg:.2f}%  |  {get_grade_letter(bot_avg)})',
            '  ' + '=' * 50,
        ]

        self._stats_box.insert('end', '\n'.join(lines))
        self._stats_box.config(state='disabled')

    def _on_row_select(self, _event) -> None:
        selection = self._tree.selection()
        if selection:
            name = self._tree.item(selection[0])['values'][0]
            self.entry_name.delete(0, 'end')
            self.entry_name.insert(0, name)


# ──────────────────────────────────────────────────────────────────────────────
#  Entry Point
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    root = tk.Tk()
    app = StudentTrackerApp(root)
    root.mainloop()
