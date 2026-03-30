import asyncio
import logging
import json
from mcp.server.fastmcp import FastMCP
from agent_bridge import build_dv_graph

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastMCP Server
mcp = FastMCP("DV-Agent MCP Server")

from mcp.server.fastmcp import Context

@mcp.tool()
async def run_dv_loop(
    mode: str,
    project_path: str,
    target_module: str,
    context_data: dict,
    ctx: Context,
    max_retries: int = 3
) -> str:
    """
    Executes the LangGraph Design Verification (DV) workflow to analyze coverage,
    generate "Non-Intrusive" UVM sequences, simulate, and debug iteratively.

    Args:
        mode: The operational mode ('dev', 'debug', 'coverage').
        project_path: The absolute path to the DV workspace.
        target_module: The specific Verilog/SystemVerilog module to verify.
        context_data: Dictionary containing contextual data (e.g. simulation_logs, coverage_report).
        max_retries: Maximum number of iterative debug/fix attempts.

    Returns:
        A formatted string containing structured suggestions of generated files
        and the final status of the verification loop.
    """
    logger.info(f"Received MCP request for {target_module} at {project_path} in {mode} mode")

    initial_state = {
        "mode": mode,
        "project_path": project_path,
        "target_module": target_module,
        "coverage_report": context_data.get("coverage_report", ""),
        "identified_gaps": [],
        "generated_sequences": [],
        "simulation_logs": context_data.get("simulation_logs", ""),
        "uvm_errors": [],
        "fix_attempts": 0,
        "max_fix_attempts": max_retries,
        "status": "INIT",
        "messages": []
    }

    dv_graph = build_dv_graph()

    progress_updates = []
    final_state = initial_state.copy()

    # Stream the LangGraph execution
    for s in dv_graph.stream(initial_state):
        node_name = list(s.keys())[0]
        update_msg = f"Completed Node: {node_name}"
        logger.info(update_msg)
        progress_updates.append(update_msg)

        # Stream progress back to the MCP Client
        ctx.info(update_msg)

        # Accumulate the state changes from the stream
        final_state.update(s[node_name])

    # Construct structured suggestions for the UI
    status = final_state.get("status", "UNKNOWN")
    sequences = final_state.get("generated_sequences", [])
    errors = final_state.get("uvm_errors", [])

    output = []
    output.append(f"### DV-Agent Verification Workflow Complete")
    output.append(f"**Target Module:** {target_module}")
    output.append(f"**Final Status:** {status}")

    output.append("\n**Workflow Progress:**")
    for update in progress_updates:
        output.append(f"- {update}")

    output.append("\n**Generated Artifacts:**")
    if sequences:
        output.append("The following sequences were generated using a Non-Intrusive UVM strategy (class extensions/factory overrides):")
        for seq in sequences:
            output.append(f"- `{project_path}/{seq}.sv`")
    else:
        output.append("No sequences generated.")

    if errors:
        output.append("\n**Unresolved Errors:**")
        for err in errors:
            output.append(f"- `{err}`")

    output.append("\n*Please review the generated sequences above and approve the file modifications via the UI.*")

    return "\n".join(output)

if __name__ == "__main__":
    logger.info("Starting DV-Agent MCP Server via stdio...")
    mcp.run()
