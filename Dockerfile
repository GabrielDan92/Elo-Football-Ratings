# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that your application will run on (if applicable)
EXPOSE 8000

# Set the entrypoint to a shell so you can manually run commands
ENTRYPOINT ["/bin/bash"]
