"""Vercel serverless entry point.

Imports the Flask app from web/server.py so Vercel can invoke it
as a WSGI handler. All /api/* requests are routed here via vercel.json.
"""

import os
import sys

# Add project root to path so 'web.server' and 'web.db' resolve correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.server import app
