# Productivity app
#### Video Demo:  <URL https://youtu.be/PVHrWXgEvE0>

## Introduction
This productivity Flask app is my Final Project for Harvard's CS50 Introduction to Computer Science course. It enables users to manage their tasks, track habits, and create notes. While there certainly is no shortage of productivity apps available, I felt them to be mainly for managing teams or projects rather than personal life. That's why I decided to create a productivity app for my final project, as I found that the app I was using to manage my startup team - ClickUp - was too complicated for personal use, and Notion, another productivity app, can be tedious to set up. I also wanted the app to enable users to track their habits, as good habits are a significant part of a productive person's life. While most productivity apps allow you to track tasks, calendar events, and take notes, most of them do not allow you to monitor your habits. So, I decided to add a feature that tracks your habits, similar to an app I use to manage my own.
## Description
This productivity app was heavily inspired by ClickUp, Notion, and Habit Tracker, as it combines the functionality of all three. The Flask app allows the user to create a list of tasks and specify the date the task is due. Tasks can also be marked as done or not done as well as deleted altogether. The tasks are displayed in an ordered list by due date. Additionally, users can create habits and track the number of times they have completed them. Each day, a habit can be marked as complete or incomplete, and the app will store this information. The app also features a note-taking section, allowing users to create and view their notes as well as edit them later. Six tags are created when the user signs up, with different colors such as red, yellow, green, light blue, dark blue, and purple. These tags are used to categorize tasks, habits, and notes. Tags can be renamed and deleted if not in use. Additionally, the user can create new tags with two extra colors - orange and grey. The app is perfect for high school and university students looking to improve their productivity. The task list can help them stay on top of their assignments, the habits section allows them to build strong habits, and the notes section is perfect for taking notes in class or studying for tests or exams.

## Getting started
### Prerequisites
For this Flask app, you need:
+ Python (version 3.11.7 or later)
+ Flask (version 3.0.0 or later)
+ SQLite (version 3.44.0 or later)

You also need the following libraries:

+ cs50 (version: 9.3.4)
+ datetime
+ flask
+ functools
+ werkzeug.security

### Installation
Ensure you have Python (version 3.11.7 or later) installed.

Install the project by running the following command in the terminal:<br>
`git clone https://github.com/christophertserenkov/CS50-Final-Project.git`

Go to the project directory by running:<br>
`cd CS50-Final-Project/project`

Create a virtual environment by executing the following command in the terminal:<br>
`python3 -m venv env`

Activate the virtual environment by running<br>
on MacOS: `source env/bin/activate`<br>
on Windows: `.\env\Scripts\activate`

Install flask by running:<br>
`pip install flask`

Install the CS50 library by running:<br>
`pip install cs50`

To run a development server, run `flask run` terminal.

Deactivate the virtual environment by running `deactivate` in the terminal when finished.

### Usage
After you run the command `flask run` in your terminal to open a development server, follow the provided link to open the app in your browser. You will be redirected to the login page. Once you register or log in, you will land on the homepage. From there, you can go to the tasks, habits, or notes page to create a task, habit, or note. Upon registering you will have six tags by default: red, yellow, green, light blue, dark blue, and purple. You can delete these tags by clicking the trash icon (if they are not in use) or rename them by clicking the pencil icon. If you want to add tags, you can do so by clicking the "add tags" button.

## File descriptions
The `app.py` file handles all the backend of the Flask app. It includes all the libraries, configures the Flask app, and defines all the functions and app routes. It makes changes to the SQL database and renders all of the pages. I decided to define functions that retrieve data from the SQL database at the top of the file so that I could call the functions to get the needed data if I needed to display tags, tasks, habits, or notes on the user's screen. This way, I could call the functions to store the returned data in a variable and pass it to the template. I used multiple functions with only the "post" method when I needed to display information about a specific tag, task, habit, or note. I also debated whether to add an invisible input tag, whose value would tell the function what to do when a decorated function is called, however, I decided to just define multiple decorator functions as it would be easier to implement and cause less confusion. It also removed the need for "invisible" input tags for forms in the HTML documents that would have made the code more confusing.

In the `static` folder, there is a directory (`Images`) containing all the icons used in the app (provided by Flaticon) and the `style.css` file, which contains all the style elements of the HTML files in the `templates` directory.

The `templates` folder stores all the needed HTML files.

The `layout.html` file displays the header and the navbar. It serves as the base for the rest of the files, excluding `login.html` and `register.html`.

`index.html` displays the homepage with three sections: tasks, habits, and notes. Tasks are sorted by the nearest due date, and notes by the latest created date. The user can mark tasks as done, complete their daily habits, and view notes from the homepage.

`tasks.html` displays all the user's tasks with their tag, name, and due date. It allows the user to mark or unmark their tasks as done and delete them. It also features a button that directs the user to the add_task page to create new tasks.

The `add_task.html` page renders a form that allows the user to create a task by choosing its name, due date, and associated tag and submitting the form.

`habbits.html` (I apologize for the typo) displays all the user's habits and if they have completed them at the present day. Each habit box has a link (actually a form that stores the habit's ID when submitted) to the view habit page. It also includes a button that redirects to a form where the user can create a habit.

The `add_habbit.html` page (again, apologies for the typo) renders a form that allows the user to create a habit.

The `view_habbit.html` page shows information about the habit, like the start date, times completed, and associated tag

`notes.html` displays all of the user's notes in a list in order of creation date and a button that opens a page allowing the user to create a note. The user can view notes by clicking on the title or delete them by clicking on the trash icon.

`note_creator.html` allows the user to create a new note with a title, tag, and body. I used a textarea HTML tag instead of an input tag to create a better text field for taking notes.

The `note_viewer.html` page displays the note clicked on either in the notes.html or index.html page. It shows the title, body, and the date created. The edit note button redirects the user to the note editor where they can edit their note.

`note_editor.html` renders a page with the note title, tag, and text pre-filled in the field. The user can edit this text or choose a different tag and save it.

`add_tag.html` allows the user to create a tag with a form with a field for the tag's name and a color selector.

`rename_tag.html` lets the user rename a tag by typing the new name in the provided form.

`login.html` and register.html display the login and registration page.

`productivity.db` is the database file where the data is stored. It contains a table named `users` that stores all the usernames and password hashes. It also contains tables like `tags`, `tasks`, `habbits`, `notes`, and `habbit_log` which store the data for tags, tasks, habits, and notes.
