# Marks Tracker Application

## Description
This Python application allows you to track and visualize marks progress for different subjects and paper types. It provides functionality to save marks along with the date and view the progress through interactive graphs.

## Requirements
- Python 3.x
- Tkinter
- SQLite3
- Matplotlib

## Installation
1. Clone or download the repository to your local machine.
2. Ensure you have Python installed on your machine.
3. Install required dependencies using pip:

```pip install matplotlib```

4. Run the application:

```python marks_tracker.py```

## Usage
1. **Subject Selection**: Choose a subject from the dropdown menu.
2. **Paper Type Selection**: Once a subject is selected, choose a paper type from the dropdown menu.
3. **Marks Entry**: Enter the marks obtained for the selected paper type.
4. **Date Entry**: Optionally, you can select a date for the marks entry.
5. **Save**: Click the "Save" button to save the marks entry.
6. **View Progress**: Click the "View Progress" button to visualize the marks progress for the selected subject and paper type.

## Features
- Track marks for various subjects and paper types.
- Visualize marks progress through interactive graphs.
- Save marks along with the date of entry.
- Dynamically update paper type dropdown based on the selected subject.

## Database Structure
The application uses SQLite database to store marks data. The database table "marks" has the following structure:
- ID (Primary Key)
- Subject (Text)
- PaperType (Text)
- Marks (Integer)
- Date (Text)

## Author
Shahu123


