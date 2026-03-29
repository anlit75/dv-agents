FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies and clear pip cache to optimize image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application script and prompts
COPY agent_bridge.py .
COPY prompts/ ./prompts/

# Ensure agent_bridge.py is executable
RUN chmod +x agent_bridge.py

# Run the agent script by default
ENTRYPOINT ["python", "agent_bridge.py"]
