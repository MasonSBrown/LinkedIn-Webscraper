# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt (dependencies list) into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose port (optional, if you want to access the app externally)
# EXPOSE 8080

# Define the command to run the scraper script
CMD ["python", "scraper.py"]
