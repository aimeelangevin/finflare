"""
Vercel serverless function handler for Django application.
This file serves as the entry point for all non-React routes in Vercel.
"""

import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapps.settings')

# Import Django's get_wsgi_application
from django.core.wsgi import get_wsgi_application

# Get the WSGI application
application = get_wsgi_application()

def handler(request, context):
    """
    Vercel serverless function handler.
    This function is called by Vercel's serverless runtime.
    """
    # Import here to avoid circular imports
    from django.http import HttpResponse
    from django.core.handlers.wsgi import WSGIRequest
    
    # Create a WSGIRequest object from the request
    environ = {
        'REQUEST_METHOD': request.get('method', 'GET'),
        'PATH_INFO': request.get('path', '/'),
        'QUERY_STRING': request.get('query', {}),
        'CONTENT_TYPE': request.get('headers', {}).get('content-type', ''),
        'CONTENT_LENGTH': request.get('headers', {}).get('content-length', ''),
        'HTTP_HOST': request.get('headers', {}).get('host', ''),
        'wsgi.input': request.get('body', ''),
        'wsgi.errors': [],
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }
    
    # Create a WSGIRequest object
    wsgi_request = WSGIRequest(environ)
    
    # Call the WSGI application
    response = application(wsgi_request)
    
    # Return the response
    return {
        'statusCode': response.status_code,
        'headers': dict(response.headers),
        'body': response.content.decode('utf-8'),
    } 