# Use the official Python image
FROM python:3.13-slim

# Set the folder inside the container
WORKDIR /app

# Copy your code into the container
COPY . .

# Install the openai library
RUN pip install openai

# Run your script when the container starts
CMD ["python", "main.py"]