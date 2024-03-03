FROM python3.10
LABEL authors="alien23"

# Get POSTGRES_XX to satisfy server version
# POSTGRES_VERSION = 16
# POSTGRES_OS_CODENAME = bookworm
# Finall
# image-name = 16-bookworm
# client = postgresql-16

ARG POSTGRES_VERSION=16
ARG POSTGRES_OS_CODENAME=bookworm
ARG DB_OPTION_DUMPS_DIR=/app/dumps


# Create the file repository configuration:
RUN echo "deb https://apt.postgresql.org/pub/repos/apt ${POSTGRES_OS_CODENAME}-pgdg main" > /etc/apt/sources.list.d/pgdg.list
# Import the repository signing key:
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
# Update the package lists && certain version of PostgreSQL.
RUN apt-get update && apt-get -y install postgresql-client-${POSTGRES_VERSION} && pg_dump -V

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir -p ${DB_OPTION_DUMPS_DIR}
COPY ./app/ ./.env /app/
ENV PYTHONPATH=/:/app
VOLUME ${DB_OPTION_DUMPS_DIR}

WORKDIR /app
CMD ["python3", "main.py"]








