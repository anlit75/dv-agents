# 🤖 DV-Agents

Autonomous Multi-Agent Orchestration for Semiconductor Design Verification.

dv-agents is a self-contained, air-gapped framework designed to automate complex Semiconductor Design Verification (DV) workflows. 
Powered by LangGraph, it orchestrates specialized agents to handle UVM code generation, log analysis, and coverage closure—all within a secure, offline Docker environment.

## ✨ Key Features
 * 🤖 Multi-Agent Orchestration: Specialized agents (Coder, Analyst, Debugger) working in cyclic LangGraph workflows (Analyze → Generate → Simulate → Verify).
 * 🔒 Privacy-First / Offline Ready: Designed for secure hardware environments with support for local OpenAI-compatible LLM endpoints.
 * 🔌 MCP Native: Fully compliant with the Model Context Protocol, acting as a high-level logic server for AI IDEs like OpenCode.
 * ⚡ Dynamic Hot-Reloading: Modify agent behaviors via local prompt files without restarting the container.

## 💻 Tech Stack
 * Core Logic: Python, LangGraph (Stateful Orchestration)
 * Deployment: Docker (Self-contained Image)
 * Interface: MCP (Model Context Protocol)
 * Inference: OpenAI-Compatible APIs (vLLM, Ollama, etc.)

## 🚀 Quick Start
1. Installation (Offline)
Download the dv-agent.tar.gz artifact from your CI/CD pipeline, then load it:
```bash
# Decompress and load the image
gunzip dv-agent.tar.gz
docker load -i dv-agent.tar
```

2. Configuration
Create a .env file based on .env.example:
```bash
LOCAL_API_URL="http://your-local-llm-ip:port/v1"
LOCAL_API_KEY="EMPTY"
LOCAL_MODEL_NAME="your-model-name"
```

3. Running the Agent (Standalone)
Mount your project files and local prompts to enable live updates and agent persistence:
```bash
docker run -it --rm \
  --env-file .env \
  -v /path/to/dv/project:/workspace \
  -v $(pwd)/prompts:/app/prompts \
  dv-agent
```

> Note: Because agent_bridge.py dynamically loads prompts on each invocation, any changes made to files in prompts/ on your host machine take effect immediately.
> 

## 🤖 Customizing Agent Behavior
Agent personas and domain expertise are defined in the prompts/ directory.
 * Modify Roles: Edit prompts/coder_agent.txt or prompts/analyst_agent.txt.
 * JSON Enforcement: Ensure prompts instruct the LLM to return structured data. The system uses robust regex parsing to extract payloads even if wrapped in markdown blocks (```json ... ```).

## 🛠️ Integration with OpenCode (MCP)
dv-agent serves as an MCP Server, separating "Heavy Logic" from "File Operations."
The "UI vs. Logic" Separation
 * DV-Agent (Server): Orchestrates LangGraph loops, maps UVM coverage gaps, and analyzes simulation logs.
 * OpenCode (Client): Manages the File System and UI. It displays agent suggestions for human approval before writing to disk.

### OpenCode Configuration
Add this to your settings.json:
```json
{
  "mcpServers": {
    "dv-agent": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--env-file", "/abs/path/to/.env",
        "-v", "/abs/path/to/project:/workspace",
        "dv-agent"
      ]
    }
  }
}
```

### Example Commands
Trigger complex loops directly from the OpenCode chat:
 * `@dv-agent start dev-loop for module axi_interconnect`
 * `@dv-agent debug log=sim.log for module axi_interconnect`

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
