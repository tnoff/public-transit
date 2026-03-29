FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install --no-cache-dir .

# Default to a shell so users can run any of the four CLI commands:
# bart, actransit, nextbus, trip-planner
CMD ["/bin/bash"]
