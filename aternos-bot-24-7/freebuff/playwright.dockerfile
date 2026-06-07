FROM mcr.microsoft.com/playwright:v1.40.0-focal

# Install Python and pip for the submitter scripts
RUN apt-get update && apt-get install -y python3 python3-pip curl jq && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install --no-cache-dir playwright requests beautifulsoup4 pexpect

# Create working directory
WORKDIR /workspace

# Copy scripts
COPY freebuff/ /workspace/freebuff/
COPY reports/ /workspace/reports/

# Set environment variables for HackerOne
ENV HACKERONE_EMAIL=potosopotosolo@gmail.com
ENV HACKERONE_PASSWORD=#)a9By=*D#6/w9T

# Install Chromium for Playwright
RUN python3 -m playwright install chromium

# Default command
CMD ["/bin/bash"]