# Not Done
# T0 build the image, run the following command in the terminal:
# docker build -t signalflow_portal .

# To run the container, run the following command in the terminal:
# docker run -it signalflow_portal

# Use an official Ubuntu as a parent image
FROM ubuntu:20.04

# Set environment variables to non-interactive
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages
RUN apt-get update && apt-get install -y \
    python3.10 \
    git \
    npm \
    tmux \
    && apt-get clean

# Clone the GitHub repository
RUN git clone https://github.com/cincibrainlab/signalflow_portal.git /app

# Set the working directory
WORKDIR /app/signalflow_portal

# Install Python dependencies
RUN python3.10 -m venv venv
RUN . venv/bin/activate && pip install -r requirements.txt

# Install npm dependencies
RUN npm install

# Start tmux and create three windows
CMD ["tmux", "new-session", "-d", "bash", ";", "split-window", "-h", "bash", ";", "split-window", "-v", "bash", ";", "attach"]
