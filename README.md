# dv-agents

## Overview
This repository contains a fully self-contained, offline-ready Docker image (`dv-agent`) that hosts a Multi-Agent system for Semiconductor Design Verification (DV) powered by LangGraph.

## Offline Installation & Usage

1. **Load the Docker Image**
   Once you have downloaded the `dv-agent.tar.gz` artifact from the CI/CD pipeline, extract it and load it into your local Docker environment:

   ```bash
   gunzip dv-agent.tar.gz
   docker load -i dv-agent.tar
   ```

2. **Run the Agent**
   To start the container, you need to provide the local LLM model (OpenAI-compatible) endpoint. Set the `LOCAL_API_URL` environment variable to point to your local endpoint. If an API key is required, set `LOCAL_API_KEY` as well.

   ```bash
   docker run -it --rm \
     -e LOCAL_API_URL="http://your-local-llm-ip:port/v1" \
     -e LOCAL_API_KEY="your-api-key" \
     dv-agent
   ```

   If you have project files or simulation scripts you need the agent to interact with, you can mount them as a volume:
   ```bash
   docker run -it --rm \
     -e LOCAL_API_URL="http://your-local-llm-ip:port/v1" \
     -e LOCAL_API_KEY="your-api-key" \
     -v /path/to/your/dv/project:/workspace \
     dv-agent
   ```

## Customizing Agents

The agent behaviors, roles, and expertise are defined in separate prompt template files located in the `prompts/` directory.

To customize an agent's instructions:
1. Edit the corresponding `.txt` file (e.g., `prompts/coder_agent.txt`).
2. Ensure the prompt explicitly instructs the LLM to return data in the required JSON format.
3. The `agent_bridge.py` script dynamically loads these files at runtime and uses robust regex parsing to extract the JSON payload, even if it is wrapped in markdown code blocks (` ```json ... ``` `).

## Offline Testing & Smoke Tests

If the local LLM endpoint is unreachable (e.g., during the CI/CD pipeline build), the agents will gracefully catch the connection error and fall back to returning mocked JSON data. This ensures the LangGraph cyclic workflow (Analyze -> Generate -> Simulate -> Debug -> Verify) can be continuously smoke-tested in complete isolation.