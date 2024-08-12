# Not Done
# T0 build the image, run the following command in the terminal:
# docker build -t sf_portal .

# To run the container, run the following command in the terminal:
# docker run -it sf_portal

# Use an official Python runtime as a parent image
FROM python:3.10.14-slim-bookworm

# Set the working directory in the container
WORKDIR /app

COPY ./builds/ ./

# Install system dependencies
RUN apt-get update && apt-get install -y \
    npm \
    tmux \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install npm dependencies
RUN cd frontend && npm install

EXPOSE 5173
EXPOSE 8001

ENV BACKEND_PORT=8001
ENV FRONTEND_PORT=5173
ENV DB_PORT=27017
ENV UPLOADER_PORT=1080
