from flask import Flask, render_template, request, jsonify
import os
import logging
from dotenv import load_dotenv
import db
import gemini_service

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize database on startup
db.init_db()

@app.route('/')
def index():
    """Home page with greeting and demo data button."""
    logger.info("Index page accessed")
    return render_template('index.html')

@app.route('/demo')
def demo():
    """Display all demo job data."""
    logger.info("Demo page accessed")
    try:
        jobs = db.get_all_jobs()
        logger.info(f"Successfully retrieved {len(jobs)} jobs from database")
        return render_template('analysis_page.html', jobs=jobs, is_demo=True)
    except Exception as e:
        logger.error(f"Error loading demo data: {str(e)}", exc_info=True)
        return render_template('error.html', message='Error loading job data'), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_query():
    """API endpoint to analyze job postings based on natural language query."""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        logger.info(f"Analysis query submitted: '{query}'")
        
        if not query:
            logger.warning("Empty query submitted")
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        # Parse the query using Gemini
        logger.info("Parsing natural language query with Gemini...")
        parsed_filters = gemini_service.parse_query(query)
        
        if 'error' in parsed_filters:
            logger.error(f"Error parsing query: {parsed_filters['error']}")
            return jsonify({'error': parsed_filters['error']}), 500
        
        logger.info(f"Parsed filters: {parsed_filters}")
        
        # Get all jobs
        all_jobs = db.get_all_jobs()
        logger.info(f"Retrieved {len(all_jobs)} total jobs from database")
        
        # Filter jobs based on parsed criteria
        filtered_jobs = gemini_service.filter_jobs(all_jobs, parsed_filters)
        logger.info(f"After filtering: {len(filtered_jobs)} jobs match the criteria")
        
        # Use Gemini to analyze the filtered jobs
        logger.info("Analyzing filtered jobs with Gemini...")
        analysis = gemini_service.analyze_jobs(filtered_jobs, query, parsed_filters)
        
        logger.info(f"Analysis completed successfully for query: '{query}'")
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'job_count': len(filtered_jobs),
            'filtered_jobs': filtered_jobs,
            'filters': parsed_filters
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing analysis query: {str(e)}", exc_info=True)
        return jsonify({'error': 'Analysis failed: ' + str(e)}), 500

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    """Display details for a specific job."""
    logger.info(f"Job detail page accessed for job ID: {job_id}")
    try:
        job = db.get_job_by_id(job_id)
        if not job:
            logger.warning(f"Job not found for ID: {job_id}")
            return render_template('error.html', message='Job not found'), 404
        logger.info(f"Successfully retrieved job: {job.get('title')}")
        return render_template('job_detail.html', job=job)
    except Exception as e:
        logger.error(f"Error retrieving job {job_id}: {str(e)}", exc_info=True)
        return render_template('error.html', message='Error loading job details'), 500

@app.route('/health')
def health():
    """Health check endpoint for load balancer probe."""
    logger.debug("Health check endpoint called")
    return 'OK', 200

@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 error: {request.path}")
    return render_template('error.html', message='Page not found'), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"500 server error: {str(error)}", exc_info=True)
    return render_template('error.html', message='Server error'), 500

if __name__ == '__main__':
    # Note: In production, use Gunicorn instead of Flask's development server
    # gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
    logger.info("Starting Flask application on 0.0.0.0:8000")
    app.run(host='0.0.0.0', port=8000, debug=False)
