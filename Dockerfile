# FROM python:3.12-bookworm

# # Set environment variables
# ENV POETRY_VERSION=1.8.3
# ENV POETRY_HOME=/opt/poetry
# ENV POETRY_VIRTUALENVS_IN_PROJECT=true
# ENV PATH=$POETRY_HOME/bin:$PATH`
# # install git
# # RUN apt-get install -y git

# # install packages for Qt
# RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
# RUN apt-get install -y freeglut3-dev
# RUN apt-get install -y libxcb-cursor-dev libxcb1 libxcb-render0 libxcb-shape0 libxcb-xfixes0
# RUN apt-get install libxcb-xinerama0
# RUN apt-get install qt6-base-dev
# # Install Poetry
# RUN apt-get install -y curl
# RUN curl -sSL https://install.python-poetry.org | python3 -
# RUN apt-get remove -y curl

# # Download VimbaX wheel
# RUN apt-get install -y wget
# RUN wget -P VimbaX https://github.com/alliedvision/VmbPy/releases/download/1.0.4/vmbpy-1.0.4-py3-none-any.whl
# RUN apt-get remove -y wget

# RUN apt-get clean

# # Copy the project files
# COPY . .

# # instal libs
# RUN poetry install --no-root

# # expose port to use git
# EXPOSE 420

# CMD ["poetry", "run", "python", "src/main.py"]


# Use an Ubuntu base image
FROM ubuntu:latest

# Install required packages
RUN apt-get update && apt-get install -y \
    x11-apps \
    xauth \
    xserver-xorg-video-dummy \
    && rm -rf /var/lib/apt/lists/*

# Set the DISPLAY environment variable
# ENV DISPLAY=:0