# Use the official Python image as the base image
FROM python:3.11

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the required packages
#RUN pip install "uvicorn[standard]"
RUN pip install --no-cache-dir -r requirements.txt -v

# Start the FastAPI application using Uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

# Expose port 8000 for the container
EXPOSE 8000