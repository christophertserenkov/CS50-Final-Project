from cs50 import SQL
from datetime import date
from flask import Flask, render_template, redirect, request, session
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

db = SQL("sqlite:///productivity.db")

# Reference: [Tech With Tim]. (2019, November 15). Flask Tutorial #5 - Sessions [Video]. Youtube.com. https://www.youtube.com/watch?v=iIhAfX4iek0
app.secret_key = "my-productivity-app-123"


# Ensure the user is logged in
def login_required(f):
    """ Reference: Harvard CS50 Problem set 9 - Finance """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# Returns a list of the user's tags as a list of dictionaries with all the information from the SQL table
def get_tags():
    tag_list = db.execute("SELECT * FROM tags WHERE user_id = ?", session["user_id"])
    tags = []
    for tag in tag_list:
        tag_dict = {"id": tag["tag_id"], "name": tag["tag_name"], "color": tag["color"]}
        tags.append(tag_dict)
    return tags


# Ensure the tag is not associated with any task, habit, or note
def is_delete_tag_possible(tag_id):
    # This section of code was improved with the help of chatGPT
    tasks = db.execute("SELECT tag FROM tasks WHERE tag = ?", tag_id)
    habits = db.execute("SELECT tag FROM habbits WHERE tag = ?", tag_id)
    notes = db.execute("SELECT tag FROM notes WHERE tag = ?", tag_id)
    if tasks or habits or notes:
        return False
    else:
        return True


# Returns a list of dictionaries containing information from the SQL table about the user's tasks
def get_tasks():
    task_list = db.execute("SELECT * FROM tasks WHERE user_id = ? ORDER BY due_date ASC", session["user_id"])
    tasks = []
    for task in task_list:
        color = db.execute("SELECT color FROM tags WHERE tag_id = ?", task["tag"])
        task_dict = {"id": task["task_id"], "name": task["name"],
                     "due_date": task["due_date"], "tag": color[0]["color"], "status": task["status"]}
        tasks.append(task_dict)
    return tasks


# Checks whether the user has completed the habit on the current date
def get_habit_status(habbit_id):
    habbit_log = db.execute("SELECT * FROM habbit_log WHERE habbit_id = ? AND date = ?", habbit_id, str(date.today()))
    if len(habbit_log) == 1:
        if habbit_log[0]["completed"] == 1:
            return "True"
        elif habbit_log[0]["completed"] == 0:
            return "False"
    else:
        return "False"


# Returns a list of dictionaries containing information from the SQL table about the user's habits
def get_habits():
    habit_list = db.execute("SELECT habbit_id, name, start_date, tag FROM habbits WHERE user_id = ?", session["user_id"])
    habits = []
    for habit in habit_list:
        color = db.execute("SELECT color FROM tags WHERE tag_id = ?", habit["tag"])
        times_completed = db.execute("SELECT COUNT(*) FROM habbit_log WHERE habbit_id = ? AND completed = 1;", habit["habbit_id"])
        completed = get_habit_status(habit["habbit_id"])
        habbit_dict = {"habbit_id": habit["habbit_id"], "name": habit["name"], "start_date": habit["start_date"],
                       "tag": color[0]["color"], "times_completed": times_completed[0]["COUNT(*)"], "completed": completed}
        habits.append(habbit_dict)
    return habits


# Changes the status of a habit on the current date and returns "True" if successful
def change_status(habbit_id):
    habit = db.execute("SELECT * FROM habbits WHERE habbit_id = ?", habbit_id)
    status = db.execute("SELECT * FROM habbit_log WHERE habbit_id = ? AND date = ?", habbit_id, str(date.today()))
    if len(status) == 0:
        db.execute("INSERT INTO habbit_log (habbit_id, date, completed) VALUES (?, ?, ?)",
                   habit[0]["habbit_id"], str(date.today()), 1)
        return True
    else:
        if status[0]["completed"] == 0:
            db.execute("UPDATE habbit_log SET completed = 1 WHERE habbit_id = ? AND date = ?",
                       habit[0]["habbit_id"], str(date.today()))
            return True
        elif status[0]["completed"] == 1:
            db.execute("UPDATE habbit_log SET completed = 0 WHERE habbit_id = ? AND date = ?",
                       habit[0]["habbit_id"], str(date.today()))
            return True
        else:
            return False


# Returns a list of dictionaries containing information from the SQL table about the user's notes
def get_notes():
    notes_list = db.execute("SELECT * FROM notes WHERE user_id = ? ORDER BY date_created DESC", session["user_id"])
    notes = []
    for note in notes_list:
        color = db.execute("SELECT color FROM tags WHERE tag_id = ?", note["tag"])
        note_dict = {"note_id": note["note_id"], "title": note["title"], "body": note["body"],
                     "date_created": note["date_created"], "tag": color[0]["color"]}
        notes.append(note_dict)
    return notes


# Returns a dictionary containing the note's data from the SQL table
def get_note(note_id):
    note_select = db.execute("SELECT * FROM notes WHERE note_id = ?", note_id)
    color = db.execute("SELECT color FROM tags WHERE tag_id = ?", note_select[0]["tag"])
    note = {"note_id": note_select[0]["note_id"], "title": note_select[0]["title"], "body": note_select[0]["body"],
            "date_created": note_select[0]["date_created"], "tag": color[0]["color"], "tag_id": note_select[0]["tag"]}
    return note


# Retrieves all the necessary information, storing them in variables, and renders the homepage
@app.route("/")
@login_required
def index():
    tags = get_tags()
    tasks = get_tasks()
    habits = get_habits()
    notes = get_notes()
    error = False
    return render_template("index.html", tags=tags, tasks=tasks, habits=habits, notes=notes, error=error)


# Logs the user in and creates a session
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    valid = True
    if request.method == "POST":
        if request.form.get("username") and request.form.get("password"):

            """ Reference: Harvard CS50 Problem set 9 - Finance """
            usernames = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
            if len(usernames) == 1 and check_password_hash(usernames[0]["password_hash"], request.form.get("password")):
                session["user_id"] = usernames[0]["user_id"]
                return redirect("/")
            else:
                valid = False
                return render_template("login.html", valid=valid)
        else:
            valid = False
            return render_template("login.html", valid=valid)
    else:
        return render_template("login.html", valid=valid)


# Logs the user in and clears the session
@app.route("/log_out", methods=["GET", "POST"])
def log_out():
    """ Reference: Harvard CS50 Problem set 9 - Finance """
    session.clear()
    return redirect("/")


# Registers the new user and stores their login information in the SQL table
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if request.form.get("username") and request.form.get("password") and request.form.get("confirm_password") and request.form.get("password") == request.form.get("confirm_password"):
            users = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
            if len(users) == 0:
                db.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?,?)",
                    request.form.get("username"),
                    generate_password_hash(request.form.get("password")),
                )
                user_id = db.execute("SELECT user_id FROM users WHERE username = ?", request.form.get("username"),)
                colors = [{"name": "Red", "hex": "#FF0000"},
                          {"name": "Yellow", "hex": "#FFD910"},
                          {"name": "Green", "hex": "#61FF00"},
                          {"name": "Light Blue", "hex": "#00E0FF"},
                          {"name": "Dark Blue", "hex": "#0047FF"},
                          {"name": "Purple", "hex": "#FA00FF"},]
                for color in colors:
                    db.execute("INSERT INTO tags (tag_name, color, user_id) VALUES (?, ?, ?)",
                               color["name"], color["hex"], user_id[0]["user_id"])
                return redirect("/")
            else:
                message = "Username taken"
                return render_template("register.html", message=message)
        else:
            message = "No username or passwords do not match"
            return render_template("register.html", message=message)
    else:
        message = "none"
        return render_template("register.html", message=message)


# Renders the tasks page displaying all the user's tasks and allows the user to check or uncheck a task as well as delete it
@app.route("/tasks", methods=["GET", "POST"])
@login_required
def tasks():
    tags = get_tags()
    tasks = get_tasks()
    if request.method == "POST":
        if request.form.get("action") == "check_or_uncheck":
            if request.form.get("value") == "True":
                db.execute("UPDATE tasks SET status = 'False' WHERE task_id = ?", request.form.get("task_id"))
                if request.form.get("location") == "home":
                    return redirect("/")
                else:
                    return redirect("/tasks")
            else:
                db.execute("UPDATE tasks SET status = 'True' WHERE task_id = ?", request.form.get("task_id"))
                if request.form.get("location") == "home":
                    return redirect("/")
                else:
                    return redirect("/tasks")
        elif request.form.get("action") == "delete_task":
            db.execute("DELETE FROM tasks WHERE task_id = ? AND user_id = ?", request.form.get("task_id"), session["user_id"])
            return redirect("/tasks")
    else:
        return render_template("tasks.html", tags=tags, tasks=tasks)


# Creates a new task and stores it in the SQL database
@app.route("/add_task", methods=["GET", "POST"])
@login_required
def add_task():
    tags = get_tags()
    tasks = get_tasks()
    if request.method == "POST":
        if request.form.get("task_name") and request.form.get("due_date") and request.form.get("tag"):
            db.execute("INSERT INTO tasks (name, due_date, tag, status, user_id) VALUES (?, ?, ?, ?, ?)", request.form.get(
                "task_name"), request.form.get("due_date"), request.form.get("tag"), "False", session["user_id"])
            return redirect("/tasks")
        else:
            valid = False
            return render_template("add_task.html", tags=tags, tasks=tasks, valid=valid)
    else:
        valid = True
        return render_template("add_task.html", tags=tags, tasks=tasks, valid=valid)


# Renders the habits page displaying all the user's habits and updates a habit's status on a given day
@app.route("/habbits", methods=["GET", "POST"])
@login_required
def habbits():
    tags = get_tags()
    habits = get_habits()
    if request.method == "POST":
        change = change_status(request.form.get("habbit_id"))
        if change == True:
            if request.form.get("location") == "home":
                return redirect("/")
            else:
                return redirect("/habbits")
        else:
            return render_template("habbits.html", tags=tags, habbits=habits)
    else:
        return render_template("habbits.html", tags=tags, habbits=habits)


# Creates a new habit and stores it in the SQL database
@app.route("/add_habbit", methods=["GET", "POST"])
@login_required
def add_habbit():
    tags = get_tags()
    habits = get_habits()
    if request.method == "POST":
        if request.form.get("habbit_name") and request.form.get("tag"):
            db.execute("INSERT INTO habbits (name, tag, user_id) VALUES (?, ?, ?)",
                       request.form.get("habbit_name"), request.form.get("tag"), session["user_id"])
            return redirect("/habbits")
        else:
            return render_template("add_habbit.html", tags=tags, habbits=habits)
    else:
        return render_template("add_habbit.html", tags=tags, habbits=habits)


# Renders a page with a habit's information
@app.route("/view_habbit", methods=["POST"])
@login_required
def view_habbit():
    tags = get_tags()
    habit_selected = db.execute("SELECT * FROM habbits WHERE habbit_id = ? AND user_id = ?",
                                request.form.get("habbit_id"), session["user_id"])
    habit_id = habit_selected[0]["habbit_id"]

    times_completed = db.execute("SELECT COUNT(*) FROM habbit_log WHERE habbit_id = ? AND completed = 1;", habit_id)
    tag = db.execute("SELECT tag_name, color FROM tags WHERE tag_id = ?", habit_selected[0]["tag"])

    habit = {"habbit_id": habit_id, "name": habit_selected[0]["name"], "start_date": habit_selected[0]["start_date"][:10], "tag_name": tag[0]
             ["tag_name"], "tag_color": tag[0]["color"], "times_completed": times_completed[0]["COUNT(*)"], "completed": get_habit_status(habit_id)}
    return render_template("view_habbit.html", tags=tags, habit=habit)


# Deletes a habit from the SQL table
@app.route("/delete_habit", methods=["POST"])
@login_required
def delete_habit():
    db.execute("DELETE FROM habbit_log WHERE habbit_id = ?", request.form.get("habbit_id"))
    db.execute("DELETE FROM habbits WHERE user_id = ? AND habbit_id = ?", session["user_id"], request.form.get("habbit_id"))
    return redirect("/habbits")


# Renders the notes page displaying all the users notes and deletes a note if the function is called using the "post" method
@app.route("/notes", methods=["GET", "POST"])
@login_required
def notes():
    tags = get_tags()
    notes = get_notes()
    if request.method == "POST":
        if request.form.get("action") == "delete_note":
            db.execute("DELETE FROM notes WHERE note_id = ?", request.form.get("note_id"))
            return redirect("/notes")
    else:
        return render_template("notes.html", tags=tags, notes=notes)


# Renders a page displaying input fields pre-filled with the notes' text and updates the note's data in the SQL table
@app.route("/edit_note", methods=["POST"])
@login_required
def edit_note():
    tags = get_tags()
    if request.form.get("action") == "update_note":
        db.execute("UPDATE notes SET title = ?, body = ?, tag = ? WHERE note_id = ?", request.form.get(
            "title"), request.form.get("body"), request.form.get("tag"), request.form.get("note_id"))
        return redirect("/notes")
    elif request.form.get("action") == "edit_note":
        note = get_note(request.form.get("note_id"))
        return render_template("note_editor.html", tags=tags, note=note)


# Renders a page displaying empty input fields and creates a new note with the data storing it in the SQL table
@app.route("/create_note", methods=["GET", "POST"])
@login_required
def create_note():
    tags = get_tags()
    if request.method == "POST":
        if request.form.get("title") and request.form.get("tag"):
            db.execute("INSERT INTO notes (user_id, title, body, tag) VALUES (?, ?, ?, ?)",
                       session["user_id"], request.form.get("title"), request.form.get("body"), request.form.get("tag"))
            return redirect("/notes")
        else:
            return render_template("note_creator.html", tags=tags)
    else:
        return render_template("note_creator.html", tags=tags)


# Renders a page displaying the note's data
@app.route("/view_note", methods=["POST"])
@login_required
def view_note():
    tags = get_tags()
    note = get_note(request.form.get("note_id"))
    return render_template("note_viewer.html", tags=tags, note=note)


# Renders a page with a form to create a new tag and inserts it into the SQL table if the number of tags does not exceed 8
@app.route("/tags", methods=["GET", "POST"])
@login_required
def edit_tags():
    tags = get_tags()
    colors = []
    color_list = [{"name": "Red", "color": "#FF0000"}, {"name": "Orange", "color": "#FF9F10"}, {"name": "Yellow", "color": "#FFD910"}, {"name": "Green", "color": "#61FF00"}, {
        "name": "Light Blue", "color": "#00E0FF"}, {"name": "Dark Blue", "color": "#0047FF"}, {"name": "Purple", "color": "#FA00FF"}, {"name": "Grey", "color": "#CDCDCD"}]
    for tag in tags:
        colors.append(tag["color"])
    if request.method == "POST":
        tag_list = db.execute("SELECT * FROM tags WHERE user_id = ?", session["user_id"])
        if request.form.get("tag_name") and request.form.get("color"):
            if len(tag_list) <= 8:
                db.execute("INSERT INTO tags (tag_name, color, user_id ) VALUES (?, ?, ?)",
                           request.form.get("tag_name"), request.form.get("color"), session["user_id"])
                return redirect("/")
            else:
                message = True
                return render_template("add_tag.html", tags=tags, colors=colors, color_list=color_list, message=message)
        else:
            return redirect("/")
    else:
        if len(tags) <= 8:
            message = False
        else:
            message = True
        return render_template("add_tag.html", tags=tags, colors=colors, color_list=color_list, message=message)


# Renders a page to rename the tag and updates the tag's name in the SQL table
@app.route("/rename_tag", methods=["POST"])
@login_required
def rename_tags():
    tags = get_tags()
    if request.form.get("action") == "update":
        if request.form.get("tag_name"):
            db.execute("UPDATE tags SET tag_name = ? WHERE tag_id = ?", request.form.get("tag_name"), request.form.get("tag_id"))
            return redirect("/")
        else:
            message = True
            return render_template("rename_tag.html", tags=tags, message=message)
    else:
        name = db.execute("SELECT tag_name FROM tags WHERE tag_id = ?", request.form.get("tag_id"))
        message = False
        id = request.form.get("tag_id")
        return render_template("rename_tag.html", tags=tags, message=message, name=name[0]["tag_name"], id=id)


# Deletes a tag if not associated with any task, habit, or note rendering an error message if the latter is true
@app.route("/delete_tag", methods=["POST"])
@login_required
def delete_tags():
    if request.form.get("tag_id"):
        if is_delete_tag_possible(request.form.get("tag_id")):
            db.execute("DELETE FROM tags WHERE tag_id = ?", request.form.get("tag_id"))
            return redirect("/")
        else:
            tags = get_tags()
            tasks = get_tasks()
            habits = get_habits()
            notes = get_notes()
            error = True
            return render_template("index.html", tags=tags, tasks=tasks, habits=habits, notes=notes, error=error)
    else:
        return redirect("/")
