import os
import json
import logging
from typing import TypedDict, Annotated, List, Dict, Any

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langgraph.graph import StateGraph, END
import operator
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure LLM based on environment variables for offline/local API URL
# Fallback to localhost if not provided
local_api_url = os.environ.get("LOCAL_API_URL", "http://localhost:8080/v1")
local_api_key = os.environ.get("LOCAL_API_KEY", "EMPTY")
local_model_name = os.environ.get("LOCAL_MODEL_NAME", "local-model")

llm = ChatOpenAI(
    base_url=local_api_url,
    api_key=local_api_key,
    model=local_model_name, # Set your target model
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

# Utility to load prompt templates
def load_prompt_template(agent_name: str) -> PromptTemplate:
    prompt_path = os.path.join("prompts", f"{agent_name}.txt")
    try:
        with open(prompt_path, "r") as f:
            template_str = f.read()
            return PromptTemplate.from_template(template_str)
    except Exception as e:
        logger.error(f"Failed to load prompt for {agent_name}: {e}")
        return PromptTemplate.from_template("Fallback prompt for {target_module}")

def parse_json_from_llm(text: str) -> dict:
    """Robustly extracts JSON from an LLM response string."""
    try:
        # Check if the output is wrapped in ```json ... ```
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        # If no code blocks, attempt to parse the entire string
        return json.loads(text)
    except Exception as e:
        logger.error(f"Failed to parse JSON from LLM: {e}")
        return {}


# 2. Define Node Functions (Agent Roles)

def architect_agent(state: DVState) -> DVState:
    """Architect_Agent: UVM structure analysis."""
    logger.info(f"Architect Agent: Analyzing UVM structure for module {state.get('target_module')}...")
    prompt = load_prompt_template("architect_agent")

    try:
        chain = prompt | llm
        response = chain.invoke({"target_module": state.get("target_module", "unknown")})
        parsed_res = parse_json_from_llm(response.content)
        analysis_msg = parsed_res.get("analysis", "Fallback architect analysis.")
    except Exception as e:
        logger.warning(f"LLM call failed, using mock data: {e}")
        analysis_msg = "Mock Architect Agent executed."

    new_message = {"role": "system", "content": analysis_msg}
    return {"messages": [new_message]}

def coverage_agent(state: DVState) -> DVState:
    """Coverage_Agent: Coverage report parsing and pattern gap analysis."""
    logger.info(f"Coverage Agent: Parsing coverage report {state.get('coverage_report')}...")
    prompt = load_prompt_template("coverage_agent")

    try:
        chain = prompt | llm
        response = chain.invoke({
            "target_module": state.get("target_module", "unknown"),
            "coverage_report": state.get("coverage_report", "empty")
        })
        parsed_res = parse_json_from_llm(response.content)
        gaps = parsed_res.get("identified_gaps", ["gap_in_axi_write_burst"])
        msg = f"Coverage Agent found gaps: {gaps}"
    except Exception as e:
        logger.warning(f"LLM call failed, using mock data: {e}")
        gaps = ["gap_in_axi_write_burst", "missing_read_after_write"]
        msg = f"Mock Coverage Agent found gaps: {gaps}"

    new_message = {"role": "system", "content": msg}
    return {"identified_gaps": gaps, "messages": [new_message]}

def coder_agent(state: DVState) -> DVState:
    """Coder_Agent: SV/UVM code generation."""
    logger.info(f"Coder Agent: Generating sequences for gaps {state.get('identified_gaps')}...")
    prompt = load_prompt_template("coder_agent")
    gaps = state.get("identified_gaps", [])

    try:
        chain = prompt | llm
        response = chain.invoke({
            "target_module": state.get("target_module", "unknown"),
            "identified_gaps": str(gaps)
        })
        parsed_res = parse_json_from_llm(response.content)
        sequences = parsed_res.get("generated_sequences", [f"uvm_sequence_for_{g}" for g in gaps])
        msg = "Coder Agent generated new UVM extensions."
    except Exception as e:
        logger.warning(f"LLM call failed, using mock data: {e}")
        sequences = [f"uvm_sequence_for_{g}" for g in gaps]
        msg = "Mock Coder Agent generated new UVM extensions & factory overrides."

    new_message = {"role": "system", "content": msg}
    return {"generated_sequences": sequences, "messages": [new_message]}

def script_agent(state: DVState) -> DVState:
    """Script_Agent: Python code generation."""
    logger.info(f"Script Agent: Generating auxiliary Python scripts for {state.get('target_module')}...")
    prompt = load_prompt_template("script_agent")

    try:
        chain = prompt | llm
        response = chain.invoke({
            "target_module": state.get("target_module", "unknown"),
            "project_path": state.get("project_path", "./")
        })
        parsed_res = parse_json_from_llm(response.content)
        msg = parsed_res.get("script_purpose", "Script Agent executed.")
    except Exception as e:
        logger.warning(f"LLM call failed, using mock data: {e}")
        msg = "Mock Script Agent executed."

    new_message = {"role": "system", "content": msg}
    return {"messages": [new_message]}

def sim_runner_agent(state: DVState) -> DVState:
    """Sim_Runner_Agent: Shell integration for VCS/Xcelium/Verilator."""
    logger.info(f"Sim Runner Agent: Executing simulation for {state.get('generated_sequences')}...")
    prompt = load_prompt_template("sim_runner_agent")
    fix_attempts = state.get("fix_attempts", 0)

    try:
        chain = prompt | llm
        response = chain.invoke({
            "target_module": state.get("target_module", "unknown"),
            "project_path": state.get("project_path", "./"),
            "generated_sequences": str(state.get("generated_sequences", []))
        })
        parsed_res = parse_json_from_llm(response.content)
        sim_logs = parsed_res.get("simulation_logs", "UVM_INFO: Simulating...")
    except Exception as e:
        logger.warning(f"LLM call failed, using mock data: {e}")
        if fix_attempts > 0:
            sim_logs = "UVM_INFO: Starting simulation...\nUVM_INFO: Simulation finished successfully."
        else:
            sim_logs = "UVM_INFO: Starting simulation...\nUVM_ERROR: [SEQ_ERR] Sequence failed to execute properly.\nUVM_INFO: Simulation finished."

    new_message = {"role": "system", "content": "Sim Runner Agent executed simulation."}
    return {"simulation_logs": sim_logs, "messages": [new_message]}

def debug_agent(state: DVState) -> DVState:
    """Debug_Agent: Log/Waveform text analysis."""
    logger.info("Debug Agent: Analyzing simulation logs for UVM errors...")
    prompt = load_prompt_template("debug_agent")
    logs = state.get("simulation_logs", "")

    try:
        chain = prompt | llm
        response = chain.invoke({
            "target_module": state.get("target_module", "unknown"),
            "simulation_logs": logs
        })
        parsed_res = parse_json_from_llm(response.content)
        errors = parsed_res.get("uvm_errors", [])
    except Exception as e:
        logger.warning(f"LLM call failed, using mock data: {e}")
        errors = []
        for line in logs.split("\n"):
            if "UVM_ERROR" in line or "UVM_FATAL" in line:
                errors.append(line)

    fix_attempts = state.get("fix_attempts", 0) + 1

    new_message = {"role": "system", "content": f"Debug Agent found {len(errors)} errors. Attempt {fix_attempts}."}
    return {"uvm_errors": errors, "fix_attempts": fix_attempts, "messages": [new_message]}

def verifier_node(state: DVState) -> DVState:
    """Verifier logic to check if fixes resolved the issue."""
    logger.info("Verifier: Checking if fixes were successful...")
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
        logger.warning("MAX RETRIES REACHED. Exiting workflow.")
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
    logger.info("=== DV-Agent Initializing ===")
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

    logger.info("=== DV-Agent Graph Compilation Successful ===")
    logger.info("=== Starting Smoke Test Execution ===")

    for s in dv_graph.stream(initial_state):
        node_name = list(s.keys())[0]
        logger.info(f"--- Completed Node: {node_name} ---")

    logger.info("=== Smoke Test Complete ===")
