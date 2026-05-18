
FROM python:3.13-bookworm

WORKDIR /app
COPY app/ /app

# Preinstall deps once (avoid slow apt or source builds)
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir pyarrow pandas matplotlib pytest

RUN mkdir -p /usr/local/python3.13-nogil/bin && \
    ln -s /usr/local/bin/python3.13 /usr/local/python3.13-nogil/bin/python3.13 && \
    ln -s /usr/local/python3.13-nogil/bin/python3.13 /usr/local/bin/python3.13-nogil

# Set up entrypoint
CMD ["python3.13", "--version"]

