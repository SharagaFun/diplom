# Now start with a Python base image for running the Flask application
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy the Python dependency file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask application files
COPY . .

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose the port Flask is accessible on
EXPOSE 5000

# Command to run the Flask application
CMD ["hypercorn", "app:asgi_app", "--bind", "0.0.0.0:5000"]

