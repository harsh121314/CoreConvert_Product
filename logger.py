import logging

# Configure logging
logging.basicConfig(
    filename='app.log',  # Log to app.log (remove to log to console only)
    level=logging.DEBUG,  # Capture all logs at DEBUG and above
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create a logger to import across files
logger = logging.getLogger('pdf_extraction')
