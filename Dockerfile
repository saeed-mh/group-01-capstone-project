# Build the Flask application image.
# Start from a small image with Python already installed.
FROM python:3.13-slim

# Use /app as the working directory inside the container.
WORKDIR /app
# Copy requirements first so the dependency layer can be reused.
COPY requirements.txt .
# Install packages without retaining the pip download cache.
RUN pip install --no-cache-dir -r requirements.txt
# Copy the project files allowed by .dockerignore.
COPY . .

# Document port 5000; Compose publishes it to the host.
EXPOSE 5000
# Run Flask on all container interfaces, with reloading disabled.
CMD ["python", "-m", "flask", "--app", "app:create_app", "run", "--host=0.0.0.0", "--no-reload"]
