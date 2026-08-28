from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

DATABASE = "contractorpro.db"

def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection

def create_database():
    db = get_db()

    db.execute('''CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT NOT NULL,
        service_type TEXT NOT NULL,
        description TEXT,
        location TEXT,
        price REAL DEFAULT 0,
        status TEXT DEFAULT 'New'
    )''')
    db.commit()
    db.close()

@app.route('/')
def dashboard():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ContractorPro</title>
    </head>
    <body>
        <h1>ContractorPro Dashboard</h1>
        <p>The Dashboard route is working.</p>

        <a href="/jobs/add">+ New Job</a>
    </body>
    </html>
    """

@app.route('/jobs')
def jobs():

    db = get_db()
    jobs = db.execute("SELECT * FROM jobs ORDER BY id DESC").fetchall()
    db.close()

    job_rows = ""

    for job in jobs:
        job_rows += f"""
        <tr>
            <td>{job['client_name']}</td>
            <td>{job['service_type']}</td>
            <td>{job['location']}</td>
            <td>${job['price']:.2f}</td>
            <td>{job['status']}</td>
        </tr>
        """

    if not job_rows:
        job_rows = """
        <tr>
            <td colspan="5">No jobs yet.</td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>

    <head>

        <title>ContractorPro Jobs</title>

        <style>

            body {{
                font-family: Arial, sans-serif;
                max-width: 1100px;
                margin: 40px auto;
                padding: 20px;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
            }}

            th,
            td {{
                padding: 14px;
                border: 1px solid #ddd;
                text-align: left;
            }}

            th {{
                background: #111827;
                color: white;
            }}

            a {{
                display: inline-block;
                margin-bottom: 20px;
            }}

        </style>

    </head>

    <body>

        <h1>
            Contractor Jobs
        </h1>

        <a href="/">Dashboard</a>

        &nbsp;

        <a href="/jobs/add">
            + New Job
        </a>


        <table>

            <tr>
                <th>ID</th>
                <th>Client</th>
                <th>Service</th>
                <th>Location</th>
                <th>Price</th>
                <th>Status</th>
            </tr>

            {job_rows}

        </table>

    </body>

    </html>
    """


@app.route('/jobs/add', methods=['GET', 'POST'])
def add_job():
    if request.method == 'POST':
        client_name = request.form['client_name']
        service_type = request.form['service_type']
        description = request.form.get("description", "")
        location = request.form.get("location", "")
        price = float(request.form.get("price", 0) or 0)
        status = request.form.get("status", "New")

        
        db = get_db()
        db.execute('''
            INSERT INTO jobs (client_name, service_type, description, location, price, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (client_name, service_type, description, location, price, status))
        db.commit()
        db.close()

        return redirect('/jobs')

    return f"""
    <!DOCTYPE html>
    <html>

    <head>

        <title>New Contractor Job</title>

        <style>

            body {{
                font-family: Arial, sans-serif;
                max-width: 1100px;
                margin: 40px auto;
                padding: 20px;
            }}

            form {{
                display: grid;
                gap: 20px;
            }}

            label {{
                font-weight: bold;
            }}

            input,
            textarea,
            select {{
                padding: 10px;
                border-radius: 6px;
                border: 1px solid #ddd;
                width: 100%;
            }}

            button {{
                background: #2563eb;
                color: white;
                padding: 12px 18px;
                border-radius: 6px;
                border: none;
                cursor: pointer;
            }}

        </style>

    </head>

    <body>

        <div class="container">

            <h1>
                Create New Job
            </h1>

        <a href="/">
            Dashboard
        </a>

        <br><br>

        <form method="POST">

            
            <label> Client / Company </label>

            <input
                type="text"
                id="client_name"
                name="client_name"
                required>
            

                <label>
                    Service Type
                </label>

                <select
                    name="service_type"
                    required
                >

                    <option>
                        Courier Delivery
                    </option>

                    <option>
                        Medical Courier
                    </option>

                    <option>
                        Field Service
                    </option>

                    <option>
                        Property Inspection
                    </option>

                    <option>
                        Pickup and Delivery
                    </option>

                    <option>
                        Installation
                    </option>

                    <option>
                        Other
                    </option>

                </select>

                <label>
                    Description
                </label>

                <textarea
                    name="description"
                    rows="4"
                ></textarea>

                <label>
                    Service Location
                </label>

                <input
                    name="location"
                >

                <label>
                    Contract Amount
                </label>

                <input
                    name="price"
                    type="number"
                    step="0.01"
                    required
                >


                <button type="submit">

                    Create Job

                </button>

            </form>

        </div>

    </body>

    </html>
    """

if __name__ == '__main__':

    create_database()

    app.run(
        debug=True
    )
