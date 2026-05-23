from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "erp_system_key"


# ================= DATABASE =================

def init_db():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS forms(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        company_name TEXT,
        location TEXT,
        form_date TEXT,

        first_name TEXT,
        middle_name TEXT,
        last_name TEXT,

        employee_code TEXT,
        contact_detail TEXT,
        extn_no TEXT,

        mobile TEXT,
        joining_date TEXT,
        department TEXT,
        designation TEXT,

        email_type TEXT,
        mail_service TEXT,
        created_by TEXT,
        domain_name TEXT,
        preferred_id TEXT,

        it_name TEXT,
        it_designation TEXT,
        it_contact TEXT,
        it_email TEXT,

        remarks TEXT,
        signature TEXT,

        hr_status TEXT DEFAULT 'Pending',
        hr_note TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ================= LOGIN =================

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        # ADMIN
        if username == "admin" and password == "admin123":
            session["role"] = "admin"
            return redirect("/admin")

        # HR
        elif username == "hr" and password == "hr123":
            session["role"] = "hr"
            return redirect("/hr")

        # USER
        elif username == "user" and password == "user123":
            session["role"] = "user"
            return redirect("/user")

    return render_template("login.html")


# ================= LOGOUT =================

@app.route("/logout")
def logout():

    session.clear()
    return redirect("/")


# ================= USER DASHBOARD =================

@app.route("/user")
def user():

    if session.get("role") != "user":
        return redirect("/")

    search = request.args.get("search", "")
    status = request.args.get("status", "")

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = "SELECT * FROM forms WHERE 1=1"
    values = []

    if status:
        query += " AND hr_status=?"
        values.append(status)

    if search:
        query += " AND (first_name LIKE ? OR employee_code LIKE ?)"
        values.append(f"%{search}%")
        values.append(f"%{search}%")

    query += " ORDER BY id DESC"

    cur.execute(query, values)

    forms = cur.fetchall()

    conn.close()

    return render_template("user_dashboard.html", forms=forms)


# ================= CREATE FORM =================

@app.route("/form", methods=["GET", "POST"])
def form():

    if session.get("role") != "user":
        return redirect("/")

    if request.method == "POST":

        signature_path = ""

        file = request.files.get("signature")

        if file and file.filename != "":

            os.makedirs("static/signatures", exist_ok=True)

            signature_path = "static/signatures/" + file.filename

            file.save(signature_path)

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO forms(

            company_name,
            location,
            form_date,

            first_name,
            middle_name,
            last_name,

            employee_code,
            contact_detail,
            extn_no,

            mobile,
            joining_date,
            department,
            designation,

            email_type,
            mail_service,
            created_by,
            domain_name,
            preferred_id,

            it_name,
            it_designation,
            it_contact,
            it_email,

            remarks,
            signature

        )

        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (

            request.form["company_name"],
            request.form["location"],
            request.form["form_date"],

            request.form["first_name"],
            request.form["middle_name"],
            request.form["last_name"],

            request.form["employee_code"],
            request.form["contact_detail"],
            request.form["extn_no"],

            request.form["mobile"],
            request.form["joining_date"],
            request.form["department"],
            request.form["designation"],

            request.form["email_type"],
            request.form["mail_service"],
            request.form["created_by"],
            request.form["domain_name"],
            request.form["preferred_id"],

            request.form["it_name"],
            request.form["it_designation"],
            request.form["it_contact"],
            request.form["it_email"],

            request.form["remarks"],
            signature_path
        ))

        conn.commit()
        conn.close()

        return redirect("/user")

    return render_template("form.html")


# ================= HR DASHBOARD =================

@app.route("/hr")
def hr():

    if session.get("role") != "hr":
        return redirect("/")

    search = request.args.get("search", "")
    status = request.args.get("status", "")

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = "SELECT * FROM forms WHERE 1=1"
    values = []

    if status:
        query += " AND hr_status=?"
        values.append(status)

    if search:
        query += " AND (first_name LIKE ? OR employee_code LIKE ?)"
        values.append(f"%{search}%")
        values.append(f"%{search}%")

    query += " ORDER BY id DESC"

    cur.execute(query, values)

    forms = cur.fetchall()

    conn.close()

    return render_template("hr_dashboard.html", forms=forms)


# ================= HR APPROVE =================

@app.route("/hr_approve/<int:id>")
def hr_approve(id):

    if session.get("role") != "hr":
        return redirect("/")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT hr_status FROM forms WHERE id=?", (id,))
    status = cur.fetchone()[0]

    if status == "Pending":

        cur.execute("""
        UPDATE forms
        SET hr_status='Approved'
        WHERE id=?
        """, (id,))

        conn.commit()

    conn.close()

    return redirect("/hr")


# ================= HR REJECT =================

@app.route("/hr_reject/<int:id>", methods=["POST"])
def hr_reject(id):

    if session.get("role") != "hr":
        return redirect("/")

    note = request.form.get("note")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT hr_status FROM forms WHERE id=?", (id,))
    status = cur.fetchone()[0]

    if status == "Pending":

        cur.execute("""
        UPDATE forms
        SET hr_status='Rejected',
            hr_note=?
        WHERE id=?
        """, (note, id))

        conn.commit()

    conn.close()

    return redirect("/hr")


# ================= ADMIN =================

@app.route("/admin")
def admin():

    if session.get("role") != "admin":
        return redirect("/")

    search = request.args.get("search", "")

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = """
    SELECT * FROM forms
    WHERE hr_status='Approved'
    """

    values = []

    if search:
        query += """
        AND (
            first_name LIKE ?
            OR employee_code LIKE ?
        )
        """

        values.append(f"%{search}%")
        values.append(f"%{search}%")

    query += " ORDER BY id DESC"

    cur.execute(query, values)

    forms = cur.fetchall()

    conn.close()

    return render_template("admin_dashboard.html", forms=forms)


# ================= VIEW =================

@app.route("/view/<int:id>")
def view(id):

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM forms WHERE id=?", (id,))

    form = cur.fetchone()

    conn.close()

    return render_template("view.html", form=form)


# ================= START =================

if __name__ == "__main__":

    app.run(debug=True)