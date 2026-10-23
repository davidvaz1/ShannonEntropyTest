FROM python:3.10-slim

# Install OpenJDK for Java execution
RUN apt-get update && \
    apt-get install -y default-jdk && \
    apt-get clean;

WORKDIR /app

# Copy application files
COPY EntropyTest.java server.py /app/
COPY templates/ /app/templates/

# Install Python dependencies
RUN pip install flask

EXPOSE 5000

CMD ["python3", "server.py"]


EXPOSE 8080

CMD ["python3", "server.py"]
