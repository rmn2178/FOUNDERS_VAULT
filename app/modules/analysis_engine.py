import pandas as pd
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from app.modules.llm_engine import get_llm


def analyze_csvs(file_infos, model_name):
    """
    Create a pandas agent that can analyze multiple CSV files simultaneously.
    """
    dfs = []
    try:
        for file_info in file_infos:
            df = pd.read_csv(file_info['path'])
            dfs.append(df)

        if not dfs:
            raise ValueError("No valid CSV files provided.")

    except Exception as e:
        raise ValueError(f"Failed to read CSV data: {str(e)}")

    llm = get_llm(model_name)

    # Creates an agent that handles a list of DataFrames
    agent = create_pandas_dataframe_agent(
        llm,
        dfs,
        verbose=True,
        allow_dangerous_code=True,
        handle_parsing_errors=True,
        max_iterations=10
    )

    return agent, dfs