# Use the official Python 3.12 slim image based on Debian Bullseye
FROM python:3.12-slim-bullseye

# Set environment variables to ensure Python runs in unbuffered mode and doesn't write bytecode
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Set the working directory inside the container
WORKDIR /apps

# Copy the entire application directory into the container at /app/
COPY . /app/

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Copy the requirements.txt file from the local directory into the container at /apps/
COPY ./requirements.txt .

# Install the dependencies listed in the requirements.txt file
RUN pip install -r requirements.txt
