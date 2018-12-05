#!/usr/bin/env bash
source virtual/bin/activate
export SECRET_KEY='yoursecretkey'
export DATABASE_URL="postgres://yourusername:password@localhost:5432/databasename"
export JWT_SECRET_KEY='set-this-to-be-your-secret-key'
python manage.py server