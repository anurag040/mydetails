from setuptools import setup, find_packages

setup(
    name="core_model",
    version="0.1.0",
    description="LLM-driven data analysis system with Streamlit and MLflow",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "pandas",
        "numpy",
        "seaborn",
        "scipy",
        "scikit-learn",
        "mlflow",
        "openai",
        "statsmodels"
    ],
    entry_points={
        "console_scripts": [
            "core-model-app=core_model.app:main"
        ]
    },
    include_package_data=True,
)
