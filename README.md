# BL & Container Tracking API Example

This project is a basic example implementation of the Vizion tracking API to provide bill of lading and container milestone tracking written in Python. This project uses Flask, SQLAlchemy, and Marshmallow.

# Getting Started
1. Clone the repo to your machine
1. Rename/copy `.env.sample` file to `.env` and replace API key and/or database URI.
1. (optional) Create a virtual Python environment in the project directory and activate
1. Install dependencies (`pip install -r requirements.txt`)
1. Create database in Python console
    - `>>> from api import db`
    - `>>> db.create_all()`
1. Start API server (`python api.py`)
