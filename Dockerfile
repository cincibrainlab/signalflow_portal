# Use an official Python runtime as a parent image
FROM python:3.10.14-bookworm

# Set the working directory in the container
COPY builds/ /app/

# Install system dependencies
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y --fix-missing npm tmux

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Set the working directory to /app/frontend
WORKDIR /app/frontend
RUN rm -rf node_modules package-lock.json
RUN npm install --platform=linux --arch=x64 --include=dev

EXPOSE 5173
EXPOSE 8001

ENV BACKEND_PORT=8001
ENV FRONTEND_PORT=5173
ENV DB_PORT=27017
ENV UPLOADER_PORT=1080
