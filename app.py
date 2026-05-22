from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
import pandas as pd
from io import BytesIO
import pdfkit

app = Flask(__name__)

app.secret_key = "mail_secret_key"


# ================= DATABASE =================

def init_db():

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute("""

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

        hr_status TEXT DEFAULT 'Pending',
        admin_status TEXT DEFAULT 'Pending'

    )

    """)

    conn.commit()
    conn.close()


init_db()


# ================= LOGIN =================

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # USER
        if username == "user" and password == "user123":

            session["role"] = "user"

            return redirect("/user_dashboard")

        # HR
        elif username == "hr" and password == "hr123":

            session["role"] = "hr"

            return redirect("/hr_dashboard")

        # ADMIN
        elif username == "admin" and password == "admin123":

            session["role"] = "admin"

            return redirect("/admin")

    return render_template("login.html")


# ================= LOGOUT =================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ================= USER DASHBOARD =================

@app.route("/user_dashboard")
def user_dashboard():

    if session.get("role") != "user":
        return redirect("/")

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

    SELECT * FROM forms

    ORDER BY id DESC

    """)

    forms = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM forms")
    total_forms = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*) FROM forms
    WHERE hr_status='Pending'
    """)
    pending_forms = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*) FROM forms
    WHERE admin_status='Approved'
    """)
    approved_forms = cursor.fetchone()[0]

    conn.close()

    return render_template(

        "user_dashboard.html",

        forms=forms,

        total_forms=total_forms,

        pending_forms=pending_forms,

        approved_forms=approved_forms

    )


# ================= FORM =================

@app.route("/form", methods=["GET", "POST"])
def form():

    if session.get("role") != "user":
        return redirect("/")

    if request.method == "POST":

        conn = sqlite3.connect("database.db")

        cursor = conn.cursor()

        cursor.execute("""

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

        hr_status,
        admin_status

        )

        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)

        """, (

            request.form.get("company_name"),
            request.form.get("location"),
            request.form.get("form_date"),

            request.form.get("first_name"),
            request.form.get("middle_name"),
            request.form.get("last_name"),

            request.form.get("employee_code"),
            request.form.get("contact_detail"),
            request.form.get("extn_no"),

            request.form.get("mobile"),
            request.form.get("joining_date"),
            request.form.get("department"),
            request.form.get("designation"),

            request.form.get("email_type"),
            request.form.get("mail_service"),
            request.form.get("created_by"),
            request.form.get("domain_name"),
            request.form.get("preferred_id"),

            request.form.get("it_name"),
            request.form.get("it_designation"),
            request.form.get("it_contact"),
            request.form.get("it_email"),

            request.form.get("remarks"),

            "Pending",
            "Pending"

        ))

        conn.commit()
        conn.close()

        return redirect("/user_dashboard")

    return render_template("form.html")


# ================= HR DASHBOARD =================

@app.route("/hr_dashboard")
def hr_dashboard():

    if session.get("role") != "hr":
        return redirect("/")

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

    SELECT * FROM forms

    WHERE hr_status='Pending'

    ORDER BY id DESC

    """)

    forms = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM forms")
    total_forms = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*) FROM forms
    WHERE hr_status='Pending'
    """)
    pending_forms = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*) FROM forms
    WHERE hr_status='Approved'
    """)
    approved_forms = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*) FROM forms
    WHERE hr_status='Rejected'
    """)
    rejected_forms = cursor.fetchone()[0]

    conn.close()

    return render_template(

        "hr_dashboard.html",

        forms=forms,

        total_forms=total_forms,

        pending_forms=pending_forms,

        approved_forms=approved_forms,

        rejected_forms=rejected_forms

    )


# ================= HR APPROVE =================

@app.route("/hr_approve/<int:id>")
def hr_approve(id):

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute("""

    UPDATE forms

    SET hr_status='Approved'

    WHERE id=?

    """, (id,))

    conn.commit()
    conn.close()

    return redirect("/hr_dashboard")


# ================= HR REJECT =================

@app.route("/hr_reject/<int:id>")
def hr_reject(id):

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute("""

    UPDATE forms

    SET hr_status='Rejected'

    WHERE id=?

    """, (id,))

    conn.commit()
    conn.close()

    return redirect("/hr_dashboard")


# ================= ADMIN DASHBOARD =================

@app.route("/admin")
def admin_dashboard():

    if session.get("role") != "admin":
        return redirect("/")

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

    SELECT * FROM forms

    WHERE hr_status='Approved'

    ORDER BY id DESC

    """)

    forms = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM forms")
    total_forms = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*) FROM forms
    WHERE admin_status='Approved'
    """)
    approved_forms = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*) FROM forms
    WHERE admin_status='Pending'
    """)
    pending_forms = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*) FROM forms
    WHERE admin_status='Rejected'
    """)
    rejected_forms = cursor.fetchone()[0]

    conn.close()

    return render_template(

        "admin_dashboard.html",

        forms=forms,

        total_forms=total_forms,

        approved_forms=approved_forms,

        pending_forms=pending_forms,

        rejected_forms=rejected_forms

    )


# ================= ADMIN APPROVE =================

@app.route("/approve/<int:id>")
def approve(id):

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute("""

    UPDATE forms

    SET admin_status='Approved'

    WHERE id=?

    """, (id,))

    conn.commit()
    conn.close()

    return redirect("/admin")


# ================= ADMIN REJECT =================

@app.route("/reject/<int:id>")
def reject(id):

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute("""

    UPDATE forms

    SET admin_status='Rejected'

    WHERE id=?

    """, (id,))

    conn.commit()
    conn.close()

    return redirect("/admin")


# ================= VIEW FORM =================

@app.route("/view/<int:id>")
def view(id):

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

    SELECT * FROM forms

    WHERE id=?

    """, (id,))

    form = cursor.fetchone()

    conn.close()

    return render_template("view.html", form=form)


# ================= PDF DOWNLOAD =================

@app.route("/download/<int:id>")
def download(id):

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM forms WHERE id=?",
        (id,)
    )

    form = cursor.fetchone()

    conn.close()

    rendered = render_template(
        "view.html",
        form=form
    )

    config = pdfkit.configuration(
        wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    )

    pdf = pdfkit.from_string(

        rendered,

        False,

        configuration=config

    )

    return send_file(

        BytesIO(pdf),

        download_name=f"form_{id}.pdf",

        as_attachment=True,

        mimetype="application/pdf"

    )


# ================= EXCEL EXPORT =================

@app.route("/export_excel/<int:id>")
def export_excel(id):

    conn = sqlite3.connect("database.db")

    df = pd.read_sql_query(
        f"SELECT * FROM forms WHERE id={id}",
        conn
    )

    conn.close()

    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:

        df.to_excel(writer, index=False)

    output.seek(0)

    return send_file(

        output,

        as_attachment=True,

        download_name=f"form_{id}.xlsx",

        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    )


# ================= RUN =================

if __name__ == "__main__":

    app.run(debug=True)