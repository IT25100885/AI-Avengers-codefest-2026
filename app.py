"""
Root entrypoint for Ashen Era Agentic Search Streamlit application.
Delegates to src/app.py.
"""
import runpy
from pathlib import Path

target_file = Path(__file__).resolve().parent / "src" / "app.py"
runpy.run_path(str(target_file), run_name="__main__")
