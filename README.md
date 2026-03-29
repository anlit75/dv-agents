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