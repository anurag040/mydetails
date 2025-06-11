# core_model

LLM-driven data analysis system using Streamlit and MLflow.

## Features
- Upload, clean, and profile data
- Advanced statistics and visualizations
- LLM-driven insights and recommendations
- MLflow experiment tracking

## Installation

```sh
pip install .
```

## Usage (Streamlit App)

```sh
core-model-app
```

or

```sh
streamlit run core_model/app.py
```

## Usage (as a Python package)

```python
from core_model.main import CoreModel
core = CoreModel(api_key="YOUR_OPENAI_API_KEY")
# Use core.process('your_file.csv') or other methods
```
