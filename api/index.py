{"rewrites": [{"source": "/api/(.*)", "destination": "/api/index.py"}]} -e import sys\nimport os\nsys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))\nfrom server import app
