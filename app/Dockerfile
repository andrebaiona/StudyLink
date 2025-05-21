FROM python:3.9

# Set working directory
WORKDIR /workspace

# Copy project files
COPY . /workspace

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080
# Run Flask app directly
CMD ["python", "app.py"]
