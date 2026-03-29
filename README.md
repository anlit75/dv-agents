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
   To start the container, you need to provide the local LLM model (OpenAI-compatible) endpoint. Set the `LOCAL_API_URL`, `LOCAL_API_KEY`, and `LOCAL_MODEL_NAME` environment variables.

   ```bash
   docker run -it --rm \
     -e LOCAL_API_URL="http://your-local-llm-ip:port/v1" \
     -e LOCAL_API_KEY="EMPTY" \
     -e LOCAL_MODEL_NAME="local-model" \
     dv-agent
   ```

   **Using a `.env` file:**
   Instead of passing environment variables individually, copy the `.env.example` to `.env` and use the `--env-file` flag:
   ```bash
   docker run -it --rm \
     --env-file .env \
     dv-agent
   ```

   **Mounting Workspaces & Prompts:**
   If you have project files or simulation scripts you need the agent to interact with, you can mount them as a volume.
   Additionally, you can mount your local `prompts/` directory into the container. Because `agent_bridge.py` dynamically loads the prompts on every invocation (rather than globally caching them), any changes you make to the local prompt files will take effect immediately for the next agent task without needing to restart the container:

   ```bash
   docker run -it --rm \
     --env-file .env \
     -v /path/to/your/dv/project:/workspace \
     -v $(pwd)/prompts:/app/prompts \
     dv-agent
   ```

## Customizing Agents

The agent behaviors, roles, and expertise are defined in separate prompt template files located in the `prompts/` directory.

To customize an agent's instructions:
1. Edit the corresponding `.txt` file (e.g., `prompts/coder_agent.txt`) in your local workstation.
2. Because the agent dynamically reads the files (see the `Mounting Workspaces & Prompts` command above), changes will be instantly applied.
3. Ensure the prompt explicitly instructs the LLM to return data in the required JSON format.
4. The `agent_bridge.py` script uses robust regex parsing to extract the JSON payload, even if the LLM wraps it in markdown code blocks (` ```json ... ``` `).

## Offline Testing & Smoke Tests

If the local LLM endpoint is unreachable (e.g., during the CI/CD pipeline build), the agents will gracefully catch the connection error and fall back to returning mocked JSON data. This ensures the LangGraph cyclic workflow (Analyze -> Generate -> Simulate -> Debug -> Verify) can be continuously smoke-tested in complete isolation.