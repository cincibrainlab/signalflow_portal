# Not Done
# T0 build the image, run the following command in the terminal:
# docker build -t sf_portal .

# To run the container, run the following command in the terminal:
# docker run -it sf_portal

# Use an official Python runtime as a parent image
FROM python:3.10.14-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Clone the GitHub repository
RUN apt-get update && apt-get install -y git && \
    git clone https://github.com/cincibrainlab/signalflow_portal.git . && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install system dependencies
RUN apt-get update && apt-get install -y \
    npm \
    tmux \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install npm dependencies
RUN npm install

CMD [ "tail", "-f", "/dev/null" ]