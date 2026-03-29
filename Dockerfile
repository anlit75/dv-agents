FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies and clear pip cache to optimize image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application scripts and prompts
COPY agent_bridge.py .
COPY mcp_server.py .
COPY prompts/ ./prompts/

# Ensure scripts are executable
RUN chmod +x agent_bridge.py mcp_server.py

# Run the MCP Server via stdio by default
ENTRYPOINT ["python", "mcp_server.py"]
