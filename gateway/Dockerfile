# base image
FROM python:3.11-slim AS builder
# create virtual environment to corale installed packages into a single place and not intermingling with
# base image files
RUN python -m venv /opt/venv
# "activate" the venv by prepending bin to PATH
ENV PATH="/opt/venv/bin:$PATH"

# pulls requirements.txt from build directory (gateway in this case)
COPY requirements.txt .
# installs packages listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# creating final image, start with "new" base image
FROM python:3.11-slim
# reach back into the previous layer and copy the things already installed. this prevents keeping wheels,
# build artifacts, temp files, compilers, whatever else doesn't gunk up here
COPY --from=builder /opt/venv /opt/venv
# activate the venv again
ENV PATH="/opt/venv/bin:$PATH"
# change directories
WORKDIR /app
# copy source package in, the actual code that i've written
COPY app/ ./app/

# since the venv is active, the pip install from earlier allows these commands to work and we can start 
# the container with the commands we want
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]