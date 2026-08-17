# Built and secret-scanned on every MR that touches this image context
# (pr-check:build -> pr-check:trufflehog-image). The build emits a docker-save
# tarball that the scan job reads; as of github-workflows 0.0.54 that tarball
# transits an OCI Object Storage bucket instead of a GitLab job artifact.
FROM python:3.14-slim

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir .

# Default to a shell so users can run any of the four CLI commands:
# bart, actransit, nextbus, trip-planner
CMD ["/bin/bash"]
