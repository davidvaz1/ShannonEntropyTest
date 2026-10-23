FROM python:3.10-slim

# Install OpenJDK
RUN apt-get update && \
    apt-get install -y default-jdk && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and templates
COPY EntropyTest.java server.py /app/
COPY templates/ /app/templates/

# Compile the Java file during build time so it's ready to go
RUN javac EntropyTest.java

EXPOSE 8080

CMD ["python3", "server.py"]
