import os
import json
from typing import TypedDict, Annotated, List, Dict, Any

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langgraph.graph import StateGraph, END
import operator

# Configure LLM based on environment variables for offline/local API URL
# Fallback to localhost if not provided
local_api_url = os.environ.get("LOCAL_API_URL", "http://localhost:8080/v1")
local_api_key = os.environ.get("LOCAL_API_KEY", "dummy-key-for-local")

llm = ChatOpenAI(
    base_url=local_api_url,
    api_key=local_api_key,
    model="local-model", # Set your target model
    temperature=0
)

# 1. Define State Schema
class DVState(TypedDict):
    project_path: str
    target_module: str
    coverage_report: str
    identified_gaps: List[str]
    generated_sequences: List[str]
    simulation_logs: str
    uvm_errors: List[str]
    fix_attempts: int
    max_fix_attempts: int
    status: str
    messages: Annotated[list, operator.add]

# 2. Define Node Functions (Agent Roles)

def architect_agent(state: DVState) -> DVState:
    """Architect_Agent: UVM structure analysis."""
    print(">>> Architect Agent: Analyzing UVM structure...")
    new_message = {"role": "system", "content": "Architect Agent executed."}
    return {"messages": [new_message]}

def coverage_agent(state: DVState) -> DVState:
    """Coverage_Agent: Coverage report parsing and pattern gap analysis."""
    print(">>> Coverage Agent: Parsing coverage report and identifying gaps...")
    # Simulate gap identification
    gaps = ["gap_in_axi_write_burst", "missing_read_after_write"]

    new_message = {"role": "system", "content": f"Coverage Agent found gaps: {gaps}"}
    return {"identified_gaps": gaps, "messages": [new_message]}

def coder_agent(state: DVState) -> DVState:
    """
    Coder_Agent: SV/UVM code generation.
    Must adhere to "Non-Intrusive UVM Strategy": prioritizes creating UVM extensions
    and factory overrides rather than modifying legacy RTL/TB code.
    """
    print(">>> Coder Agent: Generating sequences/patterns to close coverage gaps...")
    gaps = state.get("identified_gaps", [])
    sequences = []

    for gap in gaps:
        sequences.append(f"uvm_sequence_for_{gap}")

    new_message = {"role": "system", "content": "Coder Agent generated new UVM extensions & factory overrides."}
    return {"generated_sequences": sequences, "messages": [new_message]}

def script_agent(state: DVState) -> DVState:
    """Script_Agent: Python code generation (if needed for auxiliary tooling)."""
    print(">>> Script Agent: Generating auxiliary Python scripts...")
    new_message = {"role": "system", "content": "Script Agent executed."}
    return {"messages": [new_message]}

def sim_runner_agent(state: DVState) -> DVState:
    """Sim_Runner_Agent: Shell integration for VCS/Xcelium/Verilator."""
    print(">>> Sim Runner Agent: Executing simulation...")
    # Simulate simulation execution
    sequences = state.get("generated_sequences", [])

    # In a real scenario, this would execute a shell command and capture the output.
    # We simulate a successful run but with a UVM error to trigger the debug flow.
    sim_logs = "UVM_INFO: Starting simulation...\nUVM_ERROR: [SEQ_ERR] Sequence failed to execute properly.\nUVM_INFO: Simulation finished."

    # After some fix attempts, we simulate success
    fix_attempts = state.get("fix_attempts", 0)
    if fix_attempts > 0:
        sim_logs = "UVM_INFO: Starting simulation...\nUVM_INFO: Simulation finished successfully."

    new_message = {"role": "system", "content": "Sim Runner Agent executed simulation."}
    return {"simulation_logs": sim_logs, "messages": [new_message]}

def debug_agent(state: DVState) -> DVState:
    """Debug_Agent: Log/Waveform text analysis."""
    print(">>> Debug Agent: Analyzing simulation logs for UVM errors...")
    logs = state.get("simulation_logs", "")
    errors = []

    for line in logs.split("\n"):
        if "UVM_ERROR" in line or "UVM_FATAL" in line:
            errors.append(line)

    fix_attempts = state.get("fix_attempts", 0) + 1

    new_message = {"role": "system", "content": f"Debug Agent found {len(errors)} errors. Attempt {fix_attempts}."}
    return {"uvm_errors": errors, "fix_attempts": fix_attempts, "messages": [new_message]}

def verifier_node(state: DVState) -> DVState:
    """Verifier logic to check if fixes resolved the issue."""
    print(">>> Verifier: Checking if fixes were successful...")
    errors = state.get("uvm_errors", [])
    if not errors:
        status = "PASSED"
    else:
        status = "FAILED"

    new_message = {"role": "system", "content": f"Verifier determined status: {status}"}
    return {"status": status, "messages": [new_message]}

# 3. Construct Workflow

def router_debug(state: DVState) -> str:
    """Router logic for debug loop."""
    if state.get("status") == "PASSED":
        return "end"

    if state.get("fix_attempts", 0) >= state.get("max_fix_attempts", 3):
        print(">>> MAX RETRIES REACHED. Exiting workflow.")
        return "end"

    return "coder_agent"

def build_dv_graph():
    """Constructs the LangGraph multi-agent workflow."""
    workflow = StateGraph(DVState)

    # Add Nodes
    workflow.add_node("architect_agent", architect_agent)
    workflow.add_node("script_agent", script_agent)
    workflow.add_node("coverage_agent", coverage_agent)
    workflow.add_node("coder_agent", coder_agent)
    workflow.add_node("sim_runner_agent", sim_runner_agent)
    workflow.add_node("debug_agent", debug_agent)
    workflow.add_node("verifier_node", verifier_node)

    # Build Edges (Closed-Loop Workflow Logic)
    # Analyze Coverage -> Generate Sequence/Pattern -> Execute Simulation -> Parse Logs -> If UVM_ERROR: Debug & Fix -> Verify Fix
    workflow.set_entry_point("architect_agent")

    # Architect -> Script Agent (Auxiliary Tooling Init)
    workflow.add_edge("architect_agent", "script_agent")

    # Script Agent -> Coverage Analysis
    workflow.add_edge("script_agent", "coverage_agent")

    # Coverage Analysis -> Code Generation (Coder Agent)
    workflow.add_edge("coverage_agent", "coder_agent")

    # Code Generation -> Simulation (Sim Runner Agent)
    workflow.add_edge("coder_agent", "sim_runner_agent")

    # Simulation -> Debug Agent
    workflow.add_edge("sim_runner_agent", "debug_agent")

    # Debug Agent -> Verifier
    workflow.add_edge("debug_agent", "verifier_node")

    # Verifier -> Conditional (If Failed & Retries < Max -> Coder; Else -> END)
    workflow.add_conditional_edges(
        "verifier_node",
        router_debug,
        {
            "coder_agent": "coder_agent",
            "end": END
        }
    )

    # Compile graph
    app = workflow.compile()
    return app

if __name__ == "__main__":
    print("=== DV-Agent Initializing ===")
    dv_graph = build_dv_graph()

    # Test execution / smoke test
    initial_state = {
        "project_path": "/workspace",
        "target_module": "axi_interconnect",
        "coverage_report": "cov.xml",
        "identified_gaps": [],
        "generated_sequences": [],
        "simulation_logs": "",
        "uvm_errors": [],
        "fix_attempts": 0,
        "max_fix_attempts": 3,
        "status": "INIT",
        "messages": []
    }

    print("=== DV-Agent Graph Compilation Successful ===")
    print("=== Starting Smoke Test Execution ===")

    for s in dv_graph.stream(initial_state):
        node_name = list(s.keys())[0]
        print(f"--- Completed Node: {node_name} ---")

    print("=== Smoke Test Complete ===")
