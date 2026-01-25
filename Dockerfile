FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create user_data directory
RUN mkdir -p user_data

# Expose port 7860 (HF Spaces default)
EXPOSE 7860

# Run the application
CMD ["python", "app.py"]
