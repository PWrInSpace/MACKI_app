FROM python:3.12-slim

# Set environment variables
ENV POETRY_VERSION=1.8.3
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH=$POETRY_HOME/bin:$PATH

# update packages
RUN apt-get update

# Install Poetry
RUN apt-get install -y curl
RUN curl -sSL https://install.python-poetry.org | python3 - 
RUN apt-get remove -y curl

# Download VimbaX wheel
RUN apt-get install -y wget
RUN wget -P VimbaX https://github.com/alliedvision/VmbPy/releases/download/1.0.4/vmbpy-1.0.4-py3-none-any.whl
RUN apt-get remove -y wget

RUN apt-get clean

# Copy the project files
COPY . .

# instal libs
RUN poetry install --no-root

# expose port to use git
EXPOSE 420

CMD ["poetry", "run", "python", "src/main.py"]