import pandas as pd
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from app.modules.llm_engine import get_llm


def analyze_csv(file_path, model_name):
    """Create pandas agent for CSV analysis"""
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise ValueError(f"Failed to read CSV: {e}")

    llm = get_llm(model_name)

    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True,
        allow_dangerous_code=True,  # Note: In production, sandbox this
        handle_parsing_errors=True,
        max_iterations=10
    )

    return agent, df