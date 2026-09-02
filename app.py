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

    try:
        db.execute('''ALTER TABLE jobs ADD COLUMN client_id INTEGER''')
    except sqlite3.OperationalError:
        pass

    try:
        db.execute("""ALTER TABLE jobs ADD COLUMN mileage REAL DEFAULT 0""")
    except sqlite3.OperationalError:
        pass

    try:
        db.execute("""ALTER TABLE jobs ADD COLUMN expenses REAL DEFAULT 0""")
    except sqlite3.OperationalError:
        pass

    try:
        db.execute("""ALTER TABLE jobs ADD COLUMN notes_financial TEXT""")
    except sqlite3.OperationalError:
        pass

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

    db.execute("""CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_date TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        amount REAL NOT NULL DEFAULT 0,
        job_id INTEGER,
        vendor TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (job_id) REFERENCES jobs (id)
    )""")
    

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
    total_expenses = db.execute("""SELECT COALESCE(SUM(expenses), 0) FROM jobs""").fetchone()[0]
    total_mileage = db.execute("""SELECT COALESCE(SUM(mileage), 0) FROM jobs""").fetchone()[0]
    net_profit = total_contract_value - total_expenses
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

                        <div class="card">
                            <h3>Total Expenses</h3>
                            <h2>${total_expenses:.2f}</h2>
                        </div>

                        <div class="card">
                            <h3>Total Mileage</h3>
                            <h2>{total_mileage}</h2>
                        </div>

                        <div class="card">
                            <h3>Net Profit</h3>
                            <h2>${net_profit:.2f}</h2>
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


@app.route("/financials")
def financials():
    db = get_db()

    selected_month = request.args.get("month", "")
    selected_year = request.args.get("year", "")

    conditions = []
    params = []

    if selected_year:
        conditions.append("substr(job_date, 1, 4) = ?")
        params.append(selected_year)

    if selected_month:
        conditions.append("substr(job_date, 6, 2) = ?")
        params.append(selected_month)

    where_clause = ""

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)


    total_contract_value = db.execute(f"""SELECT COALESCE(SUM(price), 0) FROM jobs {where_clause}""", params).fetchone()[0]

    paid_where = conditions.copy()
    paid_params = params.copy()

    paid_where.append("status = ?")
    paid_params.append("Paid")

    paid_where_clause = "WHERE " + " AND ".join(paid_where)

    paid_revenue = db.execute(f"""SELECT COALESCE(SUM(price), 0) FROM jobs {paid_where_clause}""", paid_params).fetchone()[0]

    expense_conditions = []
    expense_params = []

    if selected_year:
        expense_conditions.append("substr(expense_date, 1, 4) = ?")
        expense_params.append(selected_year)

    if selected_month:
        expense_conditions.append("substr(expense_date, 6, 2) = ?")
        expense_params.append(selected_month)

    expense_where_clause = ""

    if expense_conditions:
        expense_where_clause = "WHERE " + " AND ".join(expense_conditions)

    total_expenses = db.execute(
        f"""
        SELECT COALESCE(SUM(amount), 0)
        FROM expenses
        {expense_where_clause}
        """,
        expense_params
    ).fetchone()[0]

    total_mileage = db.execute(f"""SELECT COALESCE(SUM(mileage), 0) FROM jobs {where_clause}""", params).fetchone()[0]


    ytd_contract_value = db.execute("""
        SELECT COALESCE(SUM(price), 0)
        FROM jobs
        WHERE job_date IS NOT NULL
            AND job_date != ''
            AND substr(job_date, 1, 4) = ?
    """, (selected_year or "2026",)).fetchone()[0]

    ytd_expenses = db.execute("""
    SELECT COALESCE(SUM(amount), 0)
    FROM expenses
    WHERE expense_date IS NOT NULL
        AND expense_date != ''
        AND substr(expense_date, 1, 4) = ?
    """, (selected_year or "2026",)).fetchone()[0]

    ytd_mileage = db.execute("""
        SELECT COALESCE(SUM(mileage), 0)
        FROM jobs
        WHERE job_date IS NOT NULL
            AND job_date != ''
            AND substr(job_date, 1, 4) = ?
    """, (selected_year or "2026",)).fetchone()[0]

    ytd_profit = ytd_contract_value - ytd_expenses

    monthly_query = """
        SELECT
            substr(job_date, 1, 7) AS month,
            COALESCE(SUM(price), 0) AS contract_value,
            COALESCE(SUM(expenses), 0) AS expenses,
            COALESCE(SUM(price - expenses), 0) AS profit,
            COALESCE(SUM(mileage), 0) AS mileage
        FROM jobs
        WHERE job_date IS NOT NULL
            AND job_date != ''
    """

    monthly_params = []

    if selected_year:
        monthly_query += " AND substr(job_date, 1, 4) = ?"
        monthly_params.append(selected_year)

    if selected_month:
        monthly_query += " AND substr(job_date, 6, 2) = ?"
        monthly_params.append(selected_month)

    monthly_query += """
        GROUP BY substr(job_date, 1, 7)
        ORDER BY month DESC
    """

    monthly_query = """
    SELECT
        month,
        SUM(contract_value) AS contract_value,
        SUM(expenses) AS expenses,
        SUM(contract_value) - SUM(expenses) AS profit,
        SUM(mileage) AS mileage
    FROM (
        SELECT
            substr(job_date, 1, 7) AS month,
            COALESCE(SUM(price), 0) AS contract_value,
            0 AS expenses,
            COALESCE(SUM(mileage), 0) AS mileage
        FROM jobs
        WHERE job_date IS NOT NULL
          AND job_date != ''
        GROUP BY substr(job_date, 1, 7)

        UNION ALL

        SELECT
            substr(expense_date, 1, 7) AS month,
            0 AS contract_value,
            COALESCE(SUM(amount), 0) AS expenses,
            0 AS mileage
        FROM expenses
        WHERE expense_date IS NOT NULL
          AND expense_date != ''
        GROUP BY substr(expense_date, 1, 7)
        )
        WHERE 1=1
    """

    monthly_params = []

    monthly_year = request.args.get("year", "")
    monthly_month = request.args.get("month", "")

    if monthly_year:
        monthly_query += " AND substr(month, 1, 4) = ?"
        monthly_params.append(monthly_year)

    if monthly_month:
        monthly_query += " AND substr(month, 6, 2) = ?"
        monthly_params.append(monthly_month)

    monthly_query += """
        GROUP BY month
        ORDER BY month DESC
    """

    monthly_rows = db.execute(
        monthly_query,
        monthly_params
    ).fetchall()
    
    outstanding_revenue = total_contract_value - paid_revenue
    net_profit = total_contract_value - total_expenses

    db.close()

    monthly_table_rows = ""

    for row in monthly_rows:
        monthly_table_rows += f"""
        <tr>
            <td>{row[0]}</td>
            <td>${row[1]:.2f}</td>
            <td>${row[2]:.2f}</td>
            <td>${row[3]:.2f}</td>
            <td>{row[4]:.1f}</td>
        </tr>
        """

    if total_contract_value > 0:
        profit_margin = (net_profit / total_contract_value) * 100
    else:
        profit_margin = 0

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ContractorPro Financials</title>

        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f4f6f8;
                margin: 0;
            }}

            nav {{
                background: #111827;
                color: white;
                padding: 18px 40px;
            }}

            nav a {{
                color: white;
                text-decoration: none;
                margin-right: 20px;
            }}

            .container {{
                max-width: 1100px;
                margin: 40px auto;
                padding: 0 20px;
            }}

            .cards {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 18px;
            }}

            .card {{
                background: white;
                padding: 22px;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            }}

            .card h3 {{
                margin-top: 0;
                font-size: 15px;
            }}

            .card h2 {{
                margin-bottom: 0;
            }}

            <h2 style="margin-top: 40px;">Monthly Financial Summary</h2>

            <table style="width: 100%; background: white; border-collapse: collapse">
                <tr style="background: #111827; color: white;">
                    <th style="padding: 12px;">Month</th>
                    <th style="padding: 12px;">Contract Value</th>
                    <th style="padding: 12px;">Expenses</th>
                    <th style="padding: 12px;">Profit</th>
                    <th style="padding: 12px;">Mileage</th>
                </tr>
                
                {monthly_table_rows}
            
            </table>

            <h2 style="margin-top: 40px;">Year-to-Date Financial Summary</h2>

            <div class="cards">

                <div class="card">
                    <h3>Contract Value</h3>
                    <h2>${ytd_contract_value:.2f}</h2>
                </div>

                <div class="card">
                    <h3>Total Expenses</h3>
                    <h2>${ytd_expenses:.2f}</h2>
                </div>

                <div class="card">
                    <h3>Net Profit</h3>
                    <h2>${ytd_profit:.2f}</h2>
                </div>

                <div class="card">
                    <h3>Business Mileage</h3>
                    <h2>{ytd_mileage:.1f}</h2>
                </div>

            </div>

        </style>
    </head>
    <body>
        <nav>
            <a href="/">Dashboard</a>
            <a href="/jobs">Jobs</a>
            <a href="/clients">Clients</a>
            <a href="/financials">Financials</a>
        </nav>
        <div class="container">

            <h1>Financials</h1>

            <p>Contractor revenue, expenses, and profit overview</p>

            <form method="GET" action="/financials" style="margin-bottom: 25px;">
                <label>Year</label>
                <select name="year">
                    <option value="">All Years</option>
                    <option value="2026" {"selected" if selected_year == "2026" else ""}>2026</option>
                    <option value="2027" {"selected" if selected_year == "2027" else ""}>2027</option>
                </select>

                &nbsp;

                <label>Month</label>
                <select name="month">
                    <option value="">All Months</option>
                    <option value="01" {"selected" if selected_month == "01" else ""}>January</option>
                    <option value="02" {"selected" if selected_month == "02" else ""}>February</option>
                    <option value="03" {"selected" if selected_month == "03" else ""}>March</option>
                    <option value="04" {"selected" if selected_month == "04" else ""}>April</option>
                    <option value="05" {"selected" if selected_month == "05" else ""}>May</option>
                    <option value="06" {"selected" if selected_month == "06" else ""}>June</option>
                    <option value="07" {"selected" if selected_month == "07" else ""}>July</option>
                    <option value="08" {"selected" if selected_month == "08" else ""}>August</option>
                    <option value="09" {"selected" if selected_month == "09" else ""}>September</option>
                    <option value="10" {"selected" if selected_month == "10" else ""}>October</option>
                    <option value="11" {"selected" if selected_month == "11" else ""}>November</option>
                    <option value="12" {"selected" if selected_month == "12" else ""}>December</option>
                </select>
                &nbsp;
                <button type="submit">Filter</button>
            </form>

            <div class="cards">

                <div class="card">
                    <h3>Contract Value</h3>
                    <h2>${total_contract_value:.2f}</h2>
                </div>

                <div class="card">
                    <h3>Paid Revenue</h3>
                    <h2>${paid_revenue:.2f}</h2>
                </div>

                <div class="card">
                    <h3>Outstanding Revenue</h3>
                    <h2>${outstanding_revenue:.2f}</h2>
                </div>

                <div class="card">
                    <h3>Total Expenses</h3>
                    <h2>${total_expenses:.2f}</h2>
                </div>

                <div class="card">
                    <h3>Net Profit</h3>
                    <h2>${net_profit:.2f}</h2>
                </div>

                <div class="card">
                    <h3>Profit Margin</h3>
                    <h2>{profit_margin:.2f}%</h2>
                </div>
            
                <div class="card">
                    <h3>Business Mileage</h3>
                    <h2>{total_mileage:.1f}</h2>
                </div>

            </div>

                <h2 style="margin-top: 40px;">Monthly Financial Summary</h2>

                <table style="width: 100%; background: white; border-collapse: collapse">
                    <tr style="background: #111827; color: white;">
                        <th style="padding: 12px;">Month</th>
                        <th style="padding: 12px;">Contract Value</th>
                        <th style="padding: 12px;">Expenses</th>
                        <th style="padding: 12px;">Profit</th>
                        <th style="padding: 12px;">Mileage</th>
                    </tr>
                    
                    {monthly_table_rows}
                </table>

                <h2 style="margin-top: 40px;">Year-to-Date Summary</h2>

                <div class="cards">

                    <div class="card">
                        <h3>Contract Value</h3>
                        <h2>${ytd_contract_value:.2f}</h2>
                    </div>

                    <div class="card">
                        <h3>YTD Expenses</h3>
                        <h2>${ytd_expenses:.2f}</h2>
                    </div>

                    <div class="card">
                        <h3>YTD Profit</h3>
                        <h2>${ytd_profit:.2f}</h2>
                    </div>

                    <div class="card">
                        <h3>Business Mileage</h3>
                        <h2>{ytd_mileage:.1f}</h2>
                    </div>

                </div>        
    </body>
    </html>
    """
    
@app.route('/jobs')
def jobs():

    db = get_db()
    jobs = db.execute("""
    SELECT
        jobs.*,
        COALESCE((
            SELECT SUM(expenses.amount)
            FROM expenses
            WHERE expenses.job_id = jobs.id
        ), 0) AS ledger_expenses
    FROM jobs
    ORDER BY jobs.id DESC
    """).fetchall()
    db.close()

    job_rows = ""

    for job in jobs:

        job_expenses = job["ledger_expenses"] or 0
        profit = (job["price"] or 0) - job_expenses

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

            <td>{job['job_date'] or ''}</td>

            <td>${job['price']:.2f}</td>

            <td>${job_expenses:,.2f}</td>

            <td>${profit:.2f}</td>

            <td>{(job['mileage'] or 0):.1f}</td>

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

                <a href="/jobs/{job['id']}/edit">Edit</a>
                <br>

                <a href="/expenses/add?job_id={job['id']}">+ Expense</a>
                <br>

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
                <th>Job Date</th>
                <th>Contract</th>
                <th>Expenses</th>
                <th>Profit</th>
                <th>Mileage</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>

            {job_rows}

        </table>

    </body>

    </html>
    """

@app.route("/expenses")
def expenses():
    db = get_db()

    expense_rows = db.execute("""
        SELECT
            expenses.*,
            jobs.client_name,
            jobs.service_type
        FROM expenses
        LEFT JOIN jobs ON expenses.job_id = jobs.id
        ORDER BY expense_date DESC, expenses.id DESC
    """).fetchall()

    total_expenses = db.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM expenses
    """).fetchone()[0]

    db.close()

    rows = ""

    for expense in expense_rows:
        linked_job = ""

        if expense["job_id"]:
            linked_job = f"Job #{expense['job_id']}"

        rows += f"""
        <tr>
            <td>{expense['expense_date']}</td>
            <td>{expense['category']}</td>
            <td>{expense['description'] or ''}</td>
            <td>{expense['vendor'] or ''}</td>
            <td>{linked_job}</td>
            <td>${expense['amount']:,.2f}</td>
            <td>
                <a href="/expenses/{expense['id']}/edit">Edit</a>
                &nbsp;

                <form
                    method="POST"
                    action="/expenses/{expense['id']}/delete"
                    style="display:inline;"
                    onsubmit="return confirm('Delete this expense?');"
                >
                    <button type="submit">Delete</button>
                </form>
            </td>
        </tr>
        """

    if not rows:
        rows = """
        <tr>
            <td colspan="7" style="text-align:center; padding:20px;">
                No expenses have been recorded yet.
            </td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ContractorPro Expenses</title>

        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f4f6f8;
                margin: 0;
            }}

            nav {{
                background: #111827;
                padding: 18px 30px;
            }}

            nav a {{
                color: white;
                text-decoration: none;
                margin-right: 25px;
            }}

            .container {{
                width: 900px;
                max-width: 90%;
                margin: 40px auto;
            }}

            .summary-card {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 30px;
                box-shadow: 0 2px 8px rgba(0,0,0,.08);
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
            }}

            th {{
                background: #111827;
                color: white;
                padding: 12px;
                text-align: left;
            }}

            td {{
                padding: 12px;
                border-bottom: 1px solid #ddd;
            }}

            .new-expense {{
                display: inline-block;
                background: #16a34a;
                color: white;
                padding: 10px 16px;
                text-decoration: none;
                border-radius: 5px;
                margin-bottom: 20px;
            }}
        </style>
    </head>

    <body>

        <nav>
            <a href="/">Dashboard</a>
            <a href="/jobs">Jobs</a>
            <a href="/clients">Clients</a>
            <a href="/financials">Financials</a>
            <a href="/expenses">Expenses</a>
        </nav>

        <div class="container">

            <h1>Business Expenses</h1>

            <p>
                Track deductible business expenses and job-related costs.
            </p>

            <a href="/expenses/add" class="new-expense">
                + New Expense
            </a>

            <div class="summary-card">
                <h3>Total Recorded Expenses</h3>
                <h2>${total_expenses:,.2f}</h2>
            </div>

            <table>
                <tr>
                    <th>Date</th>
                    <th>Category</th>
                    <th>Description</th>
                    <th>Vendor</th>
                    <th>Job</th>
                    <th>Amount</th>
                    <th>Actions</th>
                </tr>

                {rows}

            </table>

        </div>

    </body>
    </html>
    """

@app.route("/expenses/add", methods=["GET", "POST"])
def add_expense():
    db = get_db()

    if request.method == "POST":
        expense_date = request.form["expense_date"]
        category = request.form["category"]
        description = request.form.get("description", "")
        vendor = request.form.get("vendor", "")
        amount = float(request.form["amount"])
        job_id = request.form.get("job_id")
        notes = request.form.get("notes", "")

        if not job_id:
            job_id = None
        else:
            job_id = int(job_id)

        db.execute("""
            INSERT INTO expenses (
                expense_date,
                category,
                description,
                amount,
                job_id,
                vendor,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            expense_date,
            category,
            description,
            amount,
            job_id,
            vendor,
            notes
        ))

        db.commit()
        db.close()

        return redirect("/expenses")

    jobs = db.execute("""
        SELECT id, client_name, service_type
        FROM jobs
        ORDER BY id DESC
    """).fetchall()

    selected_job_id = request.args.get("job_id")

    job_options = """
        <option value="">General Business Expense — No Job</option>
    """

    for job in jobs:
        selected = ""

        if selected_job_id and str(job["id"]) == selected_job_id:
            selected = "selected"

        job_options += f"""
        <option value="{job['id']}" {selected}>
            Job #{job['id']} — {job['client_name']} — {job['service_type']}
        </option>
        """

    db.close()

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Add Expense - ContractorPro</title>

        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f4f6f8;
                margin: 0;
            }}

            nav {{
                background: #111827;
                padding: 18px 30px;
            }}

            nav a {{
                color: white;
                text-decoration: none;
                margin-right: 25px;
            }}

            .container {{
                width: 700px;
                max-width: 90%;
                margin: 40px auto;
            }}

            .form-card {{
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,.08);
            }}

            label {{
                display: block;
                font-weight: bold;
                margin-top: 18px;
                margin-bottom: 7px;
            }}

            input, select, textarea {{
                width: 100%;
                box-sizing: border-box;
                padding: 11px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }}

            textarea {{
                min-height: 90px;
            }}

            button {{
                background: #16a34a;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 5px;
                margin-top: 22px;
                cursor: pointer;
            }}
        </style>
    </head>

    <body>

        <nav>
            <a href="/">Dashboard</a>
            <a href="/jobs">Jobs</a>
            <a href="/clients">Clients</a>
            <a href="/financials">Financials</a>
            <a href="/expenses">Expenses</a>
        </nav>

        <div class="container">

            <h1>Add Business Expense</h1>

            <div class="form-card">

                <form method="POST">

                    <label>Expense Date</label>
                    <input
                        type="date"
                        name="expense_date"
                        required
                    >

                    <label>Category</label>
                    <select name="category" required>
                        <option value="">Select Category</option>
                        <option value="Fuel">Fuel</option>
                        <option value="Vehicle Maintenance">Vehicle Maintenance</option>
                        <option value="Parking & Tolls">Parking & Tolls</option>
                        <option value="Supplies">Supplies</option>
                        <option value="Equipment">Equipment</option>
                        <option value="Software">Software</option>
                        <option value="Insurance">Insurance</option>
                        <option value="Subcontractor">Subcontractor</option>
                        <option value="Advertising">Advertising</option>
                        <option value="Professional Services">Professional Services</option>
                        <option value="Travel">Travel</option>
                        <option value="Meals">Meals</option>
                        <option value="Other">Other</option>
                    </select>

                    <label>Description</label>
                    <input
                        type="text"
                        name="description"
                        placeholder="Example: Fuel for delivery route"
                    >

                    <label>Vendor</label>
                    <input
                        type="text"
                        name="vendor"
                        placeholder="Example: Chevron"
                    >

                    <label>Amount</label>
                    <input
                        type="number"
                        name="amount"
                        min="0"
                        step="0.01"
                        required
                    >

                    <label>Associated Job</label>
                    <select name="job_id">
                        {job_options}
                    </select>

                    <label>Notes</label>
                    <textarea
                        name="notes"
                        placeholder="Optional expense notes"
                    ></textarea>

                    <button type="submit">
                        Save Expense
                    </button>

                </form>

            </div>

        </div>

    </body>
    </html>
    """

@app.route("/expenses/<int:expense_id>/delete", methods=["POST"])
def delete_expense(expense_id):
    db = get_db()

    db.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expense_id,)
    )

    db.commit()
    db.close()

    return redirect("/expenses")


@app.route("/expenses/<int:expense_id>/edit", methods=["GET", "POST"])
def edit_expense(expense_id):
    db = get_db()

    expense = db.execute(
        "SELECT * FROM expenses WHERE id = ?",
        (expense_id,)
    ).fetchone()

    if expense is None:
        db.close()
        return "Expense not found", 404

    if request.method == "POST":
        expense_date = request.form["expense_date"]
        category = request.form["category"]
        description = request.form.get("description", "")
        vendor = request.form.get("vendor", "")
        amount = float(request.form["amount"])
        job_id = request.form.get("job_id")
        notes = request.form.get("notes", "")

        if not job_id:
            job_id = None
        else:
            job_id = int(job_id)

        db.execute("""
            UPDATE expenses
            SET expense_date = ?,
                category = ?,
                description = ?,
                vendor = ?,
                amount = ?,
                job_id = ?,
                notes = ?
            WHERE id = ?
        """, (
            expense_date,
            category,
            description,
            vendor,
            amount,
            job_id,
            notes,
            expense_id
        ))

        db.commit()
        db.close()

        return redirect("/expenses")

    jobs = db.execute("""
        SELECT id, client_name, service_type
        FROM jobs
        ORDER BY id DESC
    """).fetchall()

    job_options = """
        <option value="">General Business Expense — No Job</option>
    """

    for job in jobs:
        selected = ""

        if expense["job_id"] == job["id"]:
            selected = "selected"

        job_options += f"""
        <option value="{job['id']}" {selected}>
            Job #{job['id']} — {job['client_name']} — {job['service_type']}
        </option>
        """

    db.close()


    categories = [
        "Fuel",
        "Vehicle Maintenance",
        "Parking & Tolls",
        "Supplies",
        "Equipment",
        "Software",
        "Insurance",
        "Subcontractor",
        "Advertising",
        "Professional Services",
        "Travel",
        "Meals",
        "Other"
    ]

    category_options = ""

    for category in categories:
        selected = "selected" if expense["category"] == category else ""

        category_options += f"""
        <option value="{category}" {selected}>{category}</option>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Edit Expense - ContractorPro</title>

        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f4f6f8;
                margin: 0;
            }}

            nav {{
                background: #111827;
                padding: 18px 30px;
            }}

            nav a {{
                color: white;
                text-decoration: none;
                margin-right: 25px;
            }}

            .container {{
                width: 700px;
                max-width: 90%;
                margin: 40px auto;
            }}

            .form-card {{
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,.08);
            }}

            label {{
                display: block;
                font-weight: bold;
                margin-top: 18px;
                margin-bottom: 7px;
            }}

            input, select, textarea {{
                width: 100%;
                box-sizing: border-box;
                padding: 11px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }}

            textarea {{
                min-height: 90px;
            }}

            button {{
                background: #16a34a;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 5px;
                margin-top: 22px;
                cursor: pointer;
            }}
        </style>
    </head>

    <body>

        <nav>
            <a href="/">Dashboard</a>
            <a href="/jobs">Jobs</a>
            <a href="/clients">Clients</a>
            <a href="/financials">Financials</a>
            <a href="/expenses">Expenses</a>
        </nav>

        <div class="container">

            <h1>Edit Business Expense</h1>

            <div class="form-card">

                <form method="POST">

                    <label>Expense Date</label>
                    <input
                        type="date"
                        name="expense_date"
                        value="{expense['expense_date']}"
                        required
                    >

                    <label>Category</label>
                    <select name="category" required>
                        {category_options}
                    </select>

                    <label>Description</label>
                    <input
                        type="text"
                        name="description"
                        value="{expense['description'] or ''}"
                    >

                    <label>Vendor</label>
                    <input
                        type="text"
                        name="vendor"
                        value="{expense['vendor'] or ''}"
                    >

                    <label>Amount</label>
                    <input
                        type="number"
                        name="amount"
                        min="0"
                        step="0.01"
                        value="{expense['amount']}"
                        required
                    >

                    <label>Associated Job</label>
                    <select name="job_id">
                        {job_options}
                    </select>

                    <label>Notes</label>
                    <textarea name="notes">{expense['notes'] or ''}</textarea>

                    <button type="submit">
                        Save Changes
                    </button>

                </form>

                <p>
                    <a href="/expenses">Back to Expenses</a>
                </p>

            </div>

        </div>

    </body>
    </html>
    """


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
        mileage = request.form.get('mileage', 0)
        notes_financial = request.form.get('notes_financial', '')
        job_date = request.form.get('job_date', '')

        db.execute('''
            UPDATE jobs
            SET client_name = ?, service_type = ?, location = ?, price = ?, mileage = ?, notes_financial = ?, job_date = ?
            WHERE id = ?
        ''', (client_name, service_type, location, price, mileage, notes_financial, job_date, job_id))
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
            <label>Job Date</label><br>
            <input
                type="date"
                name="job_date"
                value="{job['job_date'] or ''}"
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
            <label>Business Mileage</label><br>
            <input
                type="number"
                step="0.1"
                name="mileage"
                value="{job['mileage']}"
                style="width: 100%; padding: 10px; margin: 8px 0 18px;"
                min="0"
            >
            <label>Financial Notes</label><br>
            <textarea
                name="notes_financial"
                style="width: 100%; padding: 10px; margin: 8px 0 18px;"
                rows="3"
            >{job['notes_financial'] or ''}</textarea>


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
        client_id = request.form["client_id"]

        service_type = request.form["service_type"]
        description = request.form.get("description", "")
        location = request.form.get("location", "")
        price = request.form.get("price", 0)
        mileage = request.form.get("mileage", 0)
        notes_financial = request.form.get("notes_financial", "")
        job_date = request.form.get("job_date", "")

        db = get_db()

        client = db.execute("SELECT company_name FROM clients WHERE id = ?", (client_id,)).fetchone()

        if client is None:
            db.close()
            return "Client not found", 404

        client_name = client["company_name"]

        db.execute("""
            INSERT INTO jobs (client_name, client_id, service_type, description, location, price, status, mileage, notes_financial, job_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (client_name, client_id, service_type, description, location, float(price), 'New', float(mileage), notes_financial, job_date))

        db.commit()
        db.close()

        return redirect("/jobs")

    db = get_db()

    clients = db.execute("SELECT * FROM clients ORDER BY created_at DESC").fetchall()

    db.close()

    client_options = ""

    for client in clients:
        client_options += f"""
        <option value="{client['id']}">
            {client['company_name']}
        </option>
        """

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

            <select
                name="client_id"
                required
            >
                {client_options}
            </select>

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
                    Job Date
                </label>

                <input
                    name="job_date"
                    type="date"
                    required
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

                <label>
                    Business Mileage
                </label>

                <input
                    name="mileage"
                    type="number"
                    min="0"
                    step="0.1"
                    value="0"
                >
                
                <label>
                    Job Expenses
                </label>

                <input
                    name="expenses"
                    type="number"
                    min="0"
                    step="0.01"
                    value="0"
                >

                <label>
                    Financial Notes
                </label>

                <textarea
                    name="notes_financial"
                    rows="3"
                    placeholder="Fuel, parking, tolls, supplies, subcontractor costs, etc."
                ></textarea>

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
            
            <td>
                <a href="/clients/{client['id']}">
                    {client['company_name']}
                </a>
            </td>

            <td>{client['contact_name'] or ''}</td>
            <td>{client['email'] or ''}</td>
            <td>{client['phone'] or ''}</td>

            <td>
                <a href="/clients/{client['id']}/edit">Edit</a>
                
                &nbsp;

                <form
                    method="POST"
                    action="/clients/{client['id']}/delete"
                    style="display: inline;"
                    onsubmit="return confirm('Delete this client?');"
                >
                    <button type="submit">
                        Delete
                    </button>
                </form>
            </td>
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
                    <th>Actions</th>
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

@app.route('/clients/<int:client_id>/edit', methods=['GET', 'POST'])
def edit_client(client_id):
    db = get_db()
    client = db.execute('SELECT * FROM clients WHERE id = ?', (client_id,)).fetchone()

    if client is None:
        db.close()
        return "Client not found", 404

    if request.method == 'POST':
        company_name = request.form['company_name']
        contact_name = request.form.get('contact_name', '')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        billing_address = request.form.get('billing_address', '')
        notes = request.form.get('notes', '')

        db.execute('''
            UPDATE clients
            SET company_name = ?, contact_name = ?, email = ?, phone = ?, billing_address = ?, notes = ?
            WHERE id = ?
        ''', (company_name, contact_name, email, phone, billing_address, notes, client_id))
        db.commit()
        db.close()
        return redirect('/clients')

    db.close()
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Edit Client</title>
    </head>
    <body style="font-family: Arial, max-width: 700px; margin: 40px auto;">
        <h1>Edit Client #{client['id']}</h1>
        <form method="POST">
            <label>Company Name</label><br>
            <input
                name="company_name"
                value="{client['company_name']}"
                required
                style="width: 100%; padding: 10px; margin: 8px 0 18px;"
            >
            <label>Contact Name</label><br>
            <input
                name="contact_name"
                value="{client['contact_name'] or ''}"
                style="width: 100%; padding: 10px; margin: 8px 0 18px;"
            >
            <label>Email</label><br>
            <input
                name="email"
                value="{client['email'] or ''}"
                style="width: 100%; padding: 10px; margin: 8px 0 18px;"
            >
            <label>Phone</label><br>
            <input
                name="phone"
                value="{client['phone'] or ''}"
                style="width: 100%; padding: 10px; margin: 8px 0 18px;"
            >
            <label>Billing Address</label><br>
            <textarea
                name="billing_address"
                style="width: 100%; padding: 10px; margin: 8px 0 18px;"
            >{client['billing_address'] or ''}</textarea>
            <label>Notes</label><br>
            <textarea
                name="notes"
                style="width: 100%; padding: 10px; margin: 8px 0 18px;"
            >{client['notes'] or ''}</textarea>
            <button type="submit">
                Save Changes
            </button>
        </form>
        <p>
            <a href="/clients">Back to Clients</a>
        </p>
    </body>
    </html>
    """

@app.route('/clients/<int:client_id>/delete', methods=['POST'])
def delete_client(client_id):
    db = get_db()
    db.execute('DELETE FROM clients WHERE id = ?', (client_id,))
    db.commit()
    db.close()
    return redirect('/clients')

@app.route('/clients/<int:client_id>')
def client_detail(client_id):
    db = get_db()
    client = db.execute('SELECT * FROM clients WHERE id = ?', (client_id,)).fetchone()

    if client is None:
        db.close()
        return "Client not found", 404

    jobs = db.execute('SELECT * FROM jobs WHERE client_id = ? ORDER BY id DESC', (client_id,)).fetchall()

    total_value = db.execute("""SELECT COALESCE(SUM(price), 0) FROM jobs WHERE client_id = ?""", (client_id,)).fetchone()[0]

    paid_revenue = db.execute("""SELECT COALESCE(SUM(price), 0) FROM jobs WHERE client_id = ? AND status = 'Paid'""", (client_id,)).fetchone()[0]

    db.close()

    job_rows = ""

    for job in jobs:
        job_rows += f"""
        <tr>
            <td>{job['id']}</td>
            <td>{job['service_type']}</td>
            <td>{job['location'] or ''}</td>
            <td>${job['price']:.2f}</td>
            <td>{job['status']}</td>
        </tr>
        """

    if not job_rows:
        job_rows = """
        <tr>
            <td colspan="5">
                No linked jobs yet.
            </td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{client['company_name']} - ContractorPro</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f4f6f8;
                margin: 0;
            }}

            .container {{
                max-width: 1050px;
                margin: 40px auto;
                padding: 0 20px;
            }}

            .card {{
                padding: 20px;
                background: white;
                border-radius: 8px;
            }}

            table {{
                width: 100%;
                background: white;
                border-collapse: collapse;
            }}

            th, td {{
                padding: 14px;
                border-bottom: 1px solid #ddd;
                text-align: left;
            }}

            th {{
                background: #111827;
                color: white;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <p>
                <a href="/clients">Back to Clients</a>
            </p>

            <h1>{client['company_name']}</h1>

            <p>
                Contact: {client['contact_name'] or '-'}<br>
                Email: {client['email'] or '-'}<br>
                Phone: {client['phone'] or '-'}
            </p>

            <div class="cards">

                <div class="card">
                    <h3>Linked Jobs</h3>
                    <h2>{len(jobs)}</h2>
                </div>

                <div class="card">
                    <h3>Contract Value</h3>
                    <h2>${total_value:.2f}</h2>
                </div>

                <div class="card">
                    <h3>Paid Revenue</h3>
                    <h2>${paid_revenue:.2f}</h2>
                </div>

            </div>

            <h2>Job History</h2>

            <table>
            
                <tr>
                    <th>ID</th>
                    <th>Service</th>
                    <th>Location</th>
                    <th>Value</th>
                    <th>Status</th>
                </tr>

                {job_rows}

            </table>

        </div>
    </body>
    </html>
    """

if __name__ == '__main__':

    create_database()

    app.run(
        debug=True, port=5001
)