from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
import db

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

# Initialize database on startup
db.init_db()

@app.route('/')
def index():
    """Home page with greeting and demo data button."""
    return render_template('index.html')

@app.route('/demo')
def demo():
    """Display all demo job data."""
    jobs = db.get_all_jobs()
    return render_template('analysis_page.html', jobs=jobs, is_demo=True)

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    """Display details for a specific job."""
    job = db.get_job_by_id(job_id)
    if not job:
        return render_template('error.html', message='Job not found'), 404
    return render_template('job_detail.html', job=job)

@app.route('/health')
def health():
    """Health check endpoint for load balancer probe."""
    return 'OK', 200

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', message='Page not found'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('error.html', message='Server error'), 500

if __name__ == '__main__':
    # Note: In production, use Gunicorn instead of Flask's development server
    # gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
    app.run(host='0.0.0.0', port=8000, debug=False)
