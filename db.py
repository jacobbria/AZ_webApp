import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'jobs.db')

# Demo job data - hardcoded for all users
DEMO_JOBS = [
    {
        'title': 'Senior Python Developer',
        'company': 'TechCorp Inc.',
        'location': 'Remote',
        'pay': '$120,000 - $160,000',
        'posting_date': '2025-02-01',
        'description': 'We are looking for an experienced Python developer to join our growing team. 5+ years of experience required.'
    },
    {
        'title': 'Full Stack Web Developer',
        'company': 'WebSolutions LLC',
        'location': 'San Francisco, CA',
        'pay': '$100,000 - $140,000',
        'posting_date': '2025-02-05',
        'description': 'Build scalable web applications with React, Node.js, and PostgreSQL. Work on cutting-edge projects.'
    },
    {
        'title': 'Data Scientist',
        'company': 'DataDriven AI',
        'location': 'New York, NY',
        'pay': '$130,000 - $180,000',
        'posting_date': '2025-02-08',
        'description': 'Join our ML team. Experience with Python, TensorFlow, and AWS required.'
    },
    {
        'title': 'DevOps Engineer',
        'company': 'CloudMasters',
        'location': 'Austin, TX',
        'pay': '$110,000 - $150,000',
        'posting_date': '2025-02-06',
        'description': 'Manage CI/CD pipelines, Kubernetes, and cloud infrastructure. 3+ years of DevOps experience.'
    },
    {
        'title': 'Frontend Developer (React)',
        'company': 'DesignStudio Pro',
        'location': 'Los Angeles, CA',
        'pay': '$90,000 - $130,000',
        'posting_date': '2025-02-04',
        'description': 'Create beautiful, responsive UIs with React and TypeScript. Strong focus on user experience.'
    },
    {
        'title': 'Software Architect',
        'company': 'Enterprise Solutions',
        'location': 'Boston, MA',
        'pay': '$140,000 - $180,000',
        'posting_date': '2025-02-07',
        'description': 'Design large-scale systems. 10+ years of software development experience. Leadership skills required.'
    },
]

def init_db():
    """Initialize SQLite database with demo jobs."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Create jobs table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            pay TEXT,
            posting_date TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert demo data if table is empty
    cursor.execute('SELECT COUNT(*) as count FROM jobs')
    if cursor.fetchone()['count'] == 0:
        for job in DEMO_JOBS:
            cursor.execute('''
                INSERT INTO jobs (title, company, location, pay, posting_date, description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (job['title'], job['company'], job['location'], job['pay'], job['posting_date'], job['description']))
    
    conn.commit()
    conn.close()

def get_all_jobs():
    """Retrieve all jobs from database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM jobs ORDER BY posting_date DESC')
    jobs = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return jobs

def get_job_by_id(job_id):
    """Retrieve a specific job by ID."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
    job = cursor.fetchone()
    
    conn.close()
    return dict(job) if job else None
