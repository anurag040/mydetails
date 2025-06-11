# Entrypoint for Streamlit app after pip install
import streamlit.web.cli as stcli
import sys
import os

def main():
    # Ensure working directory is the package root for relative paths
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sys.argv = ["streamlit", "run", os.path.join(os.path.dirname(__file__), "..", "app.py")]
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()
