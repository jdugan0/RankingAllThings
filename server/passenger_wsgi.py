# Passenger (cPanel "Setup Python App") entry point.
# FastAPI is ASGI, but Passenger speaks WSGI, so we wrap the app with a2wsgi.
from a2wsgi import ASGIMiddleware
from main import app

application = ASGIMiddleware(app)
