import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime

def setup_database():
    connection = sqlite3.connect('marks_tracker.db')
    cursor = connection.cursor()

    # Create the table
    cursor.execute('''CREATE TABLE IF NOT EXISTS marks (
                        ID INTEGER PRIMARY KEY,
                        Subject TEXT NOT NULL,
                        PaperType TEXT NOT NULL,
                        Marks INTEGER NOT NULL,
                        Date TEXT NOT NULL)''')
    connection.commit()
    connection.close()


setup_database()



class GraphWindow:
    def __init__(self, master, app):
        self.master = master
        self.app = app
        self.figure_canvas = None

        # Create a frame to hold the widgets
        self.center_frame = ttk.Frame(master)
        self.center_frame.grid(row=0, column=0, sticky="ew")  # Expand frame horizontally
        master.grid_columnconfigure(0, weight=1)  # Allow the column containing the frame to expand

        # Subject Dropdown
        self.subject_var = tk.StringVar()
        self.subject_dropdown = ttk.Combobox(self.center_frame, textvariable=self.subject_var,
                                             values=list(self.app.paper_types.keys()), state='readonly', width=20)
        self.subject_dropdown.grid(row=0, column=0, pady=5)
        self.subject_dropdown.bind('<<ComboboxSelected>>', self.update_content)

        # Paper Type Dropdown
        self.paper_type_var = tk.StringVar()
        self.paper_dropdown = ttk.Combobox(self.center_frame, textvariable=self.paper_type_var, state='readonly',
                                           width=20)
        self.paper_dropdown.grid(row=1, column=0, pady=5)
        self.paper_dropdown.bind('<<ComboboxSelected>>', self.update_graph)

        # Internal Grade Slider
        self.internal_grade_slider = tk.Scale(self.center_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=200,
                                              label="Internal Assessment")
        self.internal_grade_slider.grid(row=2, column=0, pady=5)
        self.internal_grade_slider.bind("<Motion>", self.update_graph)

        # Adjust the grid configuration of the frame to center the widgets
        self.center_frame.grid_columnconfigure(0, weight=1)  # Center widgets in the frame

        # Initially update dropdowns and content
        self.update_content()

    def clear_graph_and_stats(self):
        if self.figure_canvas:
            self.figure_canvas.get_tk_widget().destroy()  # Removes the graph canvas if it exists
            self.figure_canvas = None

        # Reset statistics text if you have a label for them
        if hasattr(self, 'stats_label'):
            self.stats_label.config(text="")

    def update_content(self, event=None):
        selected_subject = self.subject_var.get()
        if not selected_subject.strip():  # Checks if the selected subject is empty or whitespace
            self.paper_dropdown['values'] = []  # Clears paper dropdown
            self.clear_graph_and_stats()  # Clears the graph and stats
        else:
            paper_types = self.app.paper_types.get(selected_subject, [])
            self.paper_dropdown['values'] = paper_types
            if paper_types:
                self.paper_dropdown.current(0)
            else:
                self.clear_graph_and_stats()  # Clears the graph and stats if no paper types

            # Update the maximum value of the internal grade slider based on the selected subject
            max_internal_marks_subjects = {
                'Maths': 20,
                'Physics': 24,
                'Economics': 45,
                'Computer Science': 34,
                'Hindi': 30,
                'English': 40
            }
            max_internal_marks = max_internal_marks_subjects.get(selected_subject,
                                                                 100)  # Default to 100 if not specified
            self.internal_grade_slider.config(to=max_internal_marks)

        # Attempt to update the graph and statistics at the end of method execution
        self.update_graph()

    def update_graph(self, event=None):
        subject = self.subject_var.get()
        paper_type = self.paper_type_var.get()
        internal_marks = self.internal_grade_slider.get()

        if subject.strip() and paper_type.strip():
            connection = sqlite3.connect('marks_tracker.db')
            cursor = connection.cursor()
            cursor.execute('SELECT Marks FROM marks WHERE Subject=? AND PaperType=?', (subject, paper_type))
            marks = [row[0] for row in cursor.fetchall()]

            if marks:
                lowest_mark = min(marks)
                highest_mark = max(marks)
                average_mark = sum(marks) / len(marks)

                weightages_subjects = {
                    'Maths': {'Paper 1 - No Calc': 0.3, 'Paper 2 - Calc': 0.30, 'Paper 3 - Investigation': 0.2,
                              'Internal': 0.2},
                    'Physics': {'Paper 1 - MCQ': 0.2, 'Paper 2 - Theory': 0.4, 'Paper 3 - Astrophysics': 0.3,
                                'Internal': 0.1},
                    'Economics': {'Paper 1 - RWE': 0.30, 'Paper 2 - Text-based': 0.40, 'Internal': 0.3},
                    'Computer Science': {'Paper 1 - Theory': 0.4, 'Paper 2 - Databases': 0.2,
                                         'Paper 3 - Case Study': 0.2, 'Internal': 0.2},
                    'Hindi': {'Paper 1 - Writing': 0.25, 'Paper 2 - Reading': 0.3078, 'Paper 3 - Listening': 0.1923,
                              'Internal': 0.25},
                    'English': {'Paper 1 - Language': 0.35, 'Paper 2 - Literature': 0.35, 'Internal': 0.3}
                }

                max_marks_subjects = {
                    'Maths': {'Paper 1 - No Calc': 110, 'Paper 2 - Calc': 110, 'Paper 3 - Investigation': 55,
                              'Internal': 20},
                    'Physics': {'Paper 1 - MCQ': 40, 'Paper 2 - Theory': 90, 'Paper 3 - Astrophysics': 45,
                                'Internal': 24},
                    'Economics': {'Paper 1 - RWE': 25, 'Paper 2 - Text-based': 40, 'Internal': 45},
                    'Computer Science': {'Paper 1 - Theory': 100, 'Paper 2 - Databases': 65, 'Paper 3 - Case Study': 30,
                                         'Internal': 34},
                    'Hindi': {'Paper 1 - Writing': 30, 'Paper 2 - Reading': 40, 'Paper 3 - Listening': 25,
                              'Internal': 30},
                    'English': {'Paper 1 - Language': 20, 'Paper 2 - Literature': 30, 'Internal': 40}
                }
                # Fetch marks from the database
                connection = sqlite3.connect('marks_tracker.db')
                cursor = connection.cursor()
                cursor.execute('SELECT Date, Marks FROM marks WHERE Subject=? AND PaperType=?',
                               (subject, paper_type))
                data = cursor.fetchall()

                if not data:  # Checks if the data list is empty, indicating no marks for the selected paper type
                    self.clear_graph_and_stats()  # Clear the graph and stats
                    return  # Exit the method early
                paper_scores = []
                for paper, weightage in weightages_subjects[subject].items():
                    if paper != 'Internal':  # Skip internal for database query
                        cursor.execute('SELECT AVG(Marks) FROM marks WHERE Subject=? AND PaperType=?', (subject, paper))
                        avg_mark = cursor.fetchone()[0] or 0
                        max_mark = max_marks_subjects[subject][paper]
                        # Calculate and weight the score
                        paper_scores.append((avg_mark / max_mark) * weightage * 100)

                # Calculate for internal assessment
                internal_weightage = weightages_subjects[subject]['Internal']
                max_internal_marks = max_marks_subjects[subject]['Internal']
                internal_score = (internal_marks / max_internal_marks) * internal_weightage * 100

                # Sum scores for total
                total_mark = sum(paper_scores) + internal_score

                connection.close()

                # Initialize plot data
                plot_data = []

                # Fetch marks and dates from the database for all paper types of the selected subject
                connection = sqlite3.connect('marks_tracker.db')
                cursor = connection.cursor()

                for paper in weightages_subjects[subject]:
                    if paper != 'Internal':  # Exclude internal for this query
                        # Fetch marks and dates from the database only for the selected paper type
                        cursor.execute('SELECT Date, Marks FROM marks WHERE Subject=? AND PaperType=? ORDER BY Date',
                                       (subject, paper_type))
                        data = cursor.fetchall()
                        for date, mark in data:
                            plot_data.append((date, mark))

                # Sort plot_data by date if not already sorted
                plot_data.sort(key=lambda x: x[0])

                dates = [date for date, _ in plot_data]
                marks = [mark for _, mark in plot_data]

                # Ensure there's data to plot
                if not plot_data:
                    return  # Handle case with no data gracefully

                # Plotting
                if self.figure_canvas:
                    self.figure_canvas.get_tk_widget().destroy()

                figure = Figure(figsize=(5, 4), dpi=100)
                plot = figure.add_subplot(1, 1, 1)
                plot.plot(dates, marks, '-o')
                plot.set_title(f'Marks Progress for {subject}')
                plot.set_xlabel('Date')
                plot.set_ylabel('Marks')

                self.figure_canvas = FigureCanvasTkAgg(figure, master=self.center_frame)
                self.figure_canvas.draw()
                canvas_widget = self.figure_canvas.get_tk_widget()
                canvas_widget.grid(row=3, column=0, pady=20, padx=50, sticky='ew')
                self.center_frame.grid_columnconfigure(0, weight=1)  # Ensure the canvas expands to fill the frame

                # Prepare formatted strings for lowest, highest, and average marks
                lowest_mark_str = f"{lowest_mark:.2f}" if lowest_mark is not None else 'N/A'
                highest_mark_str = f"{highest_mark:.2f}" if highest_mark is not None else 'N/A'
                average_mark_str = f"{average_mark:.2f}" if average_mark is not None else 'N/A'

                # Update stats_text to include formatted statistics along with total mark
                stats_text = f"""Lowest: {lowest_mark_str}\n\n\nHighest: {highest_mark_str}\n\n\nAverage: {average_mark_str}\n\n\nSubject Mark: {total_mark:.2f}"""

                if hasattr(self, 'stats_label'):
                    self.stats_label.config(text=stats_text, wraplength=200)  # Adjust wraplength as needed
                else:
                    self.stats_label = ttk.Label(self.center_frame, text=stats_text,
                                                 wraplength=200)  # Adjust wraplength as needed
                    self.stats_label.grid(row=3, column=1, pady=10, sticky="w")  # Use "w" for west alignment (left)
                self.center_frame.grid_columnconfigure(0, weight=1)
            else:
                # If no valid subject or paper type is selected, clear the graph and stats
                self.clear_graph_and_stats()
                return

class MarksTrackerApp:
    def __init__(self, master):
        self.master = master
        master.title('Marks Tracker')
        master.geometry('440x340')  # Increased window size for better layout
        master.configure(bg='white')  # Changed background color for aesthetics

        # Configure the style
        style = ttk.Style()
        style.configure('TLabel', background='light blue', font=('Arial', 16))
        style.configure('TButton', font=('Arial', 16))
        style.configure('TEntry', font=('Arial', 16))
        style.configure('TCombobox', font=('Arial', 16))

        # Adding a frame for better organization
        frame = ttk.Frame(master, padding="20 20 20 20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        # Predefined paper types for each subject
        self.paper_types = {
            'Maths': ['Paper 1 - No Calc', 'Paper 2 - Calc', 'Paper 3 - Investigation'],
            'Physics': ['Paper 1 - MCQ', 'Paper 2 - Theory', 'Paper 3 - Astrophysics'],
            'Economics': ['Paper 1 - RWE', 'Paper 2 - Text-based'],
            'Computer Science': ['Paper 1 - Theory', 'Paper 2 - Databases', 'Paper 3 - Case Study'],
            'Hindi': ['Paper 1 - Writing', 'Paper 2 - Reading', 'Paper 3 - Listening'],
            'English': ['Paper 1 - Language', 'Paper 2 - Literature']
        }
        # Labels for each field
        ttk.Label(frame, text="Subject:", style='TLabel').grid(row=0, column=0, pady=(0, 10), sticky=tk.W)
        ttk.Label(frame, text="Paper Type:", style='TLabel').grid(row=1, column=0, pady=10, sticky=tk.W)
        ttk.Label(frame, text="Marks:", style='TLabel').grid(row=2, column=0, pady=10, sticky=tk.W)
        ttk.Label(frame, text="Date (YYYY-MM-DD):", style='TLabel').grid(row=3, column=0, pady=10, sticky=tk.W)

        # Widgets...
        self.subject_var = tk.StringVar()
        self.subject_dropdown = ttk.Combobox(frame, textvariable=self.subject_var, values=list(self.paper_types.keys()),
                                             state='readonly', width=20)
        self.subject_dropdown.grid(row=0, column=1, padx=10, pady=(0, 10), sticky=(tk.W, tk.E))

        self.paper_type_var = tk.StringVar()
        self.paper_dropdown = ttk.Combobox(frame, textvariable=self.paper_type_var, state='readonly', width=20)
        self.paper_dropdown.grid(row=1, column=1, padx=10, pady=10, sticky=(tk.W, tk.E))

        self.marks_var = tk.IntVar()
        self.marks_entry = ttk.Entry(frame, textvariable=self.marks_var, width=23)
        self.marks_entry.grid(row=2, column=1, padx=10, pady=10, sticky=(tk.W, tk.E))

        self.date_var = tk.StringVar()
        self.date_entry = ttk.Entry(frame, textvariable=self.date_var, width=23)
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))  # Set to current date
        self.date_entry.grid(row=3, column=1, padx=10, pady=10, sticky=(tk.W, tk.E))

        self.save_button = ttk.Button(frame, text='Save', command=self.save_marks)
        self.save_button.grid(row=4, column=1, padx=10, pady=20)

        self.view_button = ttk.Button(frame, text='View Progress', command=self.open_graph_window)
        self.view_button.grid(row=5, column=1, padx=10, pady=10)


        # Bind the combobox
        self.subject_dropdown.bind('<<ComboboxSelected>>', self.update_paper_dropdown)

        self.paper_weightages = {
            'Maths': {'Paper 1 - No Calc': 0.3, 'Paper 2 - Calc': 0.30, 'Paper 3 - Investigation': 0.2, 'Internal': 0.2},
            'Physics': {'Paper 1 - MCQ': 0.2, 'Paper 2 - Theory': 0.4, 'Paper 3 - Astrophysics': 0.3, 'Internal': 0.1},
            'Economics': {'Paper 1 - RWE': 0.30, 'Paper 2 - Text-based': 0.40, 'Internal': 0.3},
            'Computer Science': {'Paper 1 - Theory': 0.4, 'Paper 2 - Databases': 0.2, 'Paper 3 - Case Study': 0.2, 'Internal': 0.2},
            'Hindi': {'Paper 1 - Writing': 0.25, 'Paper 2 - Reading': 0.3078, 'Paper 3 - Listening': 0.1923, 'Internal': 0.25},
            'English': {'Paper 1 - Language': 0.35, 'Paper 2 - Literature': 0.35, 'Internal': 0.3}
        }

        self.max_marks = {
            'Maths': {'Paper 1 - No Calc': 110, 'Paper 2 - Calc': 110, 'Paper 3 - Investigation': 55, 'Internal': 20},
            'Physics': {'Paper 1 - MCQ': 40, 'Paper 2 - Theory': 90, 'Paper 3 - Astrophysics': 45, 'Internal': 24},
            'Economics': {'Paper 1 - RWE': 25, 'Paper 2 - Text-based': 40, 'Internal': 45},
            'Computer Science': {'Paper 1 - Theory': 100, 'Paper 2 - Databases': 65, 'Paper 3 - Case Study': 30, 'Internal': 34},
            'Hindi': {'Paper 1 - Writing': 30, 'Paper 2 - Reading': 40, 'Paper 3 - Listening': 25, 'Internal': 30},
            'English': {'Paper 1 - Language': 20, 'Paper 2 - Literature': 30, 'Internal': 40}
        }

    def open_graph_window(self):
        new_window = tk.Toplevel(self.master)
        new_window.title('Marks Progress Graph')
        new_window.geometry('800x600')  # Adjust size as needed
        GraphWindow(new_window, self)

    def update_paper_dropdown(self, event):
        self.paper_dropdown['values'] = self.paper_types[self.subject_var.get()]

    def save_marks(self):
        subject = self.subject_var.get()
        paper_type = self.paper_type_var.get()
        marks = self.marks_var.get()
        date = self.date_var.get()

        # Insert into SQLite database
        connection = sqlite3.connect('marks_tracker.db')
        cursor = connection.cursor()
        cursor.execute('INSERT INTO marks (Subject, PaperType, Marks, Date) VALUES (?, ?, ?, ?)',
                       (subject, paper_type, marks, date))
        connection.commit()
        connection.close()
        messagebox.showinfo('Success', 'Marks saved successfully!')

        # Clear the entries, except for the date
        self.subject_var.set('')
        self.paper_type_var.set('')
        self.marks_var.set(0)  # Assuming default marks are set to 0 or some other default value

if __name__ == '__main__':
    root = tk.Tk()
    app = MarksTrackerApp(root)
    root.mainloop()