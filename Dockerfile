FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY Prompt/ Prompt/
COPY static/ static/

# Create user_data directory
RUN mkdir -p user_data

# Listen inside the container; bind the published port on the host as needed
ENV HOST=0.0.0.0
EXPOSE 7860

# Run the application
CMD ["python", "app.py"]
