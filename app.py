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

    db.execute('''CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        contact_name TEXT,
        email TEXT,
        phone TEXT,
        billing_address TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    db.commit()
    db.close()


@app.route('/')
def dashboard():
    db = get_db()
    total_jobs = db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    active_jobs = db.execute("SELECT COUNT(*) FROM jobs WHERE status IN ('New', 'Accepted', 'In Progress')").fetchone()[0]
    completed_jobs = db.execute("SELECT COUNT(*) FROM jobs WHERE status IN ('Completed', 'Invoiced', 'Paid')").fetchone()[0]
    total_contract_value = db.execute("""SELECT COALESCE(SUM(price), 0) FROM jobs""").fetchone()[0]
    paid_revenue = db.execute("""SELECT COALESCE(SUM(price), 0) FROM jobs WHERE status = 'Paid'""").fetchone()[0]
    recent_jobs = db.execute("SELECT * FROM jobs ORDER BY id DESC LIMIT 5").fetchall()
    db.close()

    recent_rows = ""

    for job in recent_jobs:
        recent_rows += f"""
        <tr>
            <td>{job['id']}</td>
            <td>{job['client_name']}</td>
            <td>{job['service_type']}</td>
            <td>${job['price']:.2f}</td>
            <td>{job['status']}</td>
        </tr>
        """

        if not recent_rows:
            recent_rows = """
            <tr>
                <td colspan="5">
                    No recent jobs have been created yet.
                </td>
            </tr>
            """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>ContractorPro Dashboard</title>

            <style>
                body {{
                        font-family: Arial, sans-serif;
                        margin: 0;
                        background: #f4f6f8;
                    }}

                    nav {{
                        background: #111827;
                        color: white;
                        padding: 18px 40px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    }}

                    nav h2 {{
                        margin: 0;
                    }}

                    nav a {{
                        color: white;
                        text-decoration: none;
                        margin-left: 18px;
                    }}
                    
                    .new-job {{
                        background: #16a34a;
                        padding: 10px 16px;
                        border-radius: 6px;
                    }}

                    .container {{
                        max-width: 1150px;
                        margin: 40px auto;
                        padding: 0 20px;
                    }}

                    .cards {{
                        display: grid;
                        grid-template-columns: repeat(5, 1fr);
                        gap: 16px;
                        margin: 30px 0 40px;
                    }}

                    .card {{
                        background: white;
                        padding: 22px;
                        border-radius: 10px;
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.8);
                    }}

                    .card h3 {{
                        margin-top: 0;
                        font-size: 15px;
                        color: #4b5563;
                    }}

                    .card h2 {{
                        margin-bottom: 0;
                        font-size: 30px;
                    }}

                    table {{
                        width: 100%;
                        background: white;
                        border-collapse: collapse;
                    }}

                    th,
                    td {{
                        padding: 14px;
                        border-bottom: 1px solid #ddd;
                        text-align: left;
                    }}

                    th {{
                        background: #1f2937;
                        color: white;
                    }}

                    .section-header {{
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    }}

                    .button {{
                        background: #2563eb;
                        color: white;
                        padding: 10px 15px;
                        border-radius: 6px;
                        text-decoration: none;
                    }}

                </style>

            </head>

            <body>

                <nav>
                    <h2>ContractorPro</h2>

                    <div>
                        <a href="/">Dashboard</a>
                        <a href="/jobs">Jobs</a>
                        <a href="/jobs/add" class="new-job">+ New Job</a>
                    </div>
                </nav>

                <div class="container">

                    <h1>Contractor Dashboard</h1>

                    <p>
                        Independent contractor operations and revenue overview
                    </p>

                    <div class="cards">

                        <div class="card">
                            <h3>Total Jobs</h3>
                            <h2>{total_jobs}</h2>
                        </div>

                        <div class="card">
                            <h3>Active Jobs</h3>
                            <h2>{active_jobs}</h2>
                        </div>

                        <div class="card">
                            <h3>Completed Jobs</h3>
                            <h2>{completed_jobs}</h2>
                        </div>

                        <div class="card">
                            <h3>Contract Value</h3>
                            <h2>${total_contract_value:.2f}</h2>
                        </div>

                        <div class="card">
                            <h3>Paid Revenue</h3>
                            <h2>${paid_revenue:.2f}</h2>
                        </div>

                    </div>

                    <div class="section-header">
                        <h2>Recent Jobs</h2>
                        <a href="/jobs" class="button">View All Jobs</a>
                    </div>

                    <table>

                        <tr>
                            <th>ID</th>
                            <th>Client</th>
                            <th>Service</th>
                            <th>Value</th>
                            <th>Status</th>
                        </tr>

                        {recent_rows}
                    
                    </table>

                </div>

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

        status_options = ""

        statuses = ['New', 'Accepted', 'In Progress', 'Completed', 'Invoiced', 'Paid']

        for status in statuses:

            selected = ""

            if job['status'] == status:
                selected = "selected"

            status_options += f"""
            <option value="{status}" {selected}>{status}</option>
            """

        job_rows += f"""
        <tr>

            <td>{job['id']}</td>

            <td>{job['client_name']}</td>

            <td>{job['service_type']}</td>

            <td>{job['location'] or ''}</td>

            <td>${job['price']:.2f}</td>

            <td>

                <form method="POST"
                action="/jobs/{job['id']}/status">
                    
                
                    <select name="status">

                        {status_options}

                    </select>

                    <button type="submit">
                        Update
                    </button>

                </form>
            
            </td>
            <td>

                <a href="/jobs/{job['id']}/edit">
                    Edit
                </a>

                &nbsp;

                <form
                    method="POST"
                    action="/jobs/{job['id']}/delete"
                    style="display: inline;"
                    onsubmit="return confirm('Delete this job?');"
                >

                    <button type="submit">
                        Delete
                    </button>

                </form>

            </td>

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
                <th>Actions</th>
            </tr>

            {job_rows}

        </table>

    </body>

    </html>
    """


@app.route('/jobs/<int:job_id>/status', methods=['POST'])
def update_job_status(job_id):
    new_status = request.form.get('status')

    alowed_statuses = ['New', 'Accepted', 'In Progress', 'Completed', 'Invoiced', 'Paid']

    if new_status not in alowed_statuses:
        return "Invalid status", 400

    db = get_db()

    db.execute('UPDATE jobs SET status = ? WHERE id = ?', (new_status, job_id))

    db.commit()
    db.close()

    return redirect('/jobs')


@app.route('/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
def edit_job(job_id):
    db = get_db()

    job = db.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()

    if job is None:
        db.close()
        return "Job not found", 404

    if request.method == 'POST':
        client_name = request.form['client_name']
        service_type = request.form['service_type']
        location = request.form.get('location', '')
        price = float(request.form.get('price', 0))

        db.execute('''
            UPDATE jobs
            SET client_name = ?, service_type = ?, location = ?, price = ?
            WHERE id = ?
        ''', (client_name, service_type, location, price, job_id))
        db.commit()
        db.close()
        return redirect('/jobs')

    db.close()

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Edit Job</title>
    </head>
    <body style="font-family: Arial, max-width: 700px; margin: 40px auto;">
        <h1>Edit Job #{job['id']}</h1>
        <form method="POST">
            <label>Client / Company</label><br>
            <input
                name="client_name"
                value="{job['client_name']}"
                required
                style="width: 100%; padding: 10px; margin: 8px 0 18px;"
            >
            <label>Service Type</label><br>
            <input
                name="service_type"
                value="{job['service_type']}"
                required
                style="width: 100%; padding: 10px; margin: 8px 0 18px;"
            >
            <label>Service Location</label><br>
            <input
                name="location"
                value="{job['location'] or ''}"
                style="width: 100%; padding: 10px; margin: 8px 0 18px;"
            >
            <label>Contract Amount</label><br>
            <input
                type="number"
                step="0.01"
                name="price"
                value="{job['price']}"
                style="width: 100%; padding: 10px; margin: 8px 0 18px;"
            >
            <button type="submit">
                Save
            </button>
        </form>
        <p>
            <a href="/jobs">Back to Jobs</a>
        </p>
    </body>
    </html>
    """

@app.route('/jobs/<int:job_id>/delete', methods=['POST'])
def delete_job(job_id):
    db = get_db()
    db.execute('DELETE FROM jobs WHERE id = ?', (job_id,))
    db.commit()
    db.close()
    return redirect('/jobs')


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

@app.route('/clients')
def clients():
    db = get_db()

    all_clients = db.execute("SELECT * FROM clients ORDER BY created_at DESC").fetchall()
    db.close()

    rows = ""

    for client in all_clients:
        rows += f"""
        <tr>
            <td>{client['id']}</td>
            <td>{client['company_name']}</td>
            <td>{client['contact_name'] or ''}</td>
            <td>{client['email'] or ''}</td>
            <td>{client['phone'] or ''}</td>
        </tr>
        """

    if not rows:
        rows = """
        <tr>
            <td colspan="5">
                No clients have been added yet.
            </td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ContractorPro Clients</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f4f6f8;
                margin: 0;
            }}

            .container {{
                max-width: 1100px;
                margin: 40px auto;
                padding: 0 20px;
            }}

            table {{
                width: 100%;
                background: white;
                border-collapse: collapse;
            }}

            th,
            td {{
                padding: 14px;
                border-bottom: 1px solid #ddd;
                text-align: left;
            }}

            th {{
                background: #111827;
                color: white;
            }}

            a {{
                margin-right: 15px;
            }} 
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Clients</h1>
            <p>
                <a href="/">Dashboard</a>
                <a href="/jobs">Jobs</a>
                <a href="/clients/add">+ New Client</a>
            </p>

            <table>
                <tr>
                    <th>ID</th>
                    <th>Company</th>
                    <th>Contact</th>
                    <th>Email</th>
                    <th>Phone</th>
                </tr>

                {rows}
            </table>

        </div>
    </body>
    </html>
    """

@app.route('/clients/add', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        company_name = request.form['company_name']
        contact_name = request.form.get('contact_name', '')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        billing_address = request.form.get('billing_address', '')
        notes = request.form.get('notes', '')

        db = get_db()
        db.execute('''
            INSERT INTO clients (company_name, contact_name, email, phone, billing_address, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (company_name, contact_name, email, phone, billing_address, notes))
        db.commit()
        db.close()

        return redirect('/clients')

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Add Client</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f6f8;
        }

        .container {
            max-width: 700px;
            margin: 50px auto;
            padding: 30px;
            background: white;
            border-radius: 10px;
        }

        input, textarea {
            width: 100%;
            padding: 12px;
            margin-top: 6px;
            margin-bottom: 18px;
            box-sizing: border-box;
        }

        button {
            background-color: #16a34a;
            color: white;
            border: none;
            padding: 13px 22px;
            border-radius: 6px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Add Client</h1>
        <p>
            <a href="/clients">Back to Clients</a>
        </p>
        <form method="POST">
            <label>Company Name</label>
            <input type="text" name="company_name" required>

            <label>Contact Name</label>
            <input type="text" name="contact_name">

            <label>Email</label>
            <input type="email" name="email">

            <label>Phone</label>
            <input type="text" name="phone">

            <label>Billing Address</label>
            <textarea name="billing_address"></textarea>

            <label>Notes</label>
            <textarea name="notes"></textarea>

            <button type="submit">Save Client</button>
        </form>
    </div>
</body>
</html>
"""

if __name__ == '__main__':

    create_database()

    app.run(
        debug=True, port=5001
)