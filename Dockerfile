# Use an official lightweight Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Copy the file that lists the required Python packages
COPY requirements.txt .

# Install the Python packages specified in requirements.txt
# --no-cache-dir ensures we don't store the download cache, keeping the image small
# --trusted-host is a good practice to avoid SSL issues in some networks
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

# Copy our application code (the entire 'app' folder) into the container at /app
COPY ./app .

# Expose port 8080 to the outside world. Our Flask app runs on this port.
EXPOSE 8080

# The command to run when the container starts.
# We use gunicorn, a production-ready web server, instead of Flask's built-in server.
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]