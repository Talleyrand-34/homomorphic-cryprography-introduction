
#!/bin/bash

# Create virtual environment named 'env'
python3 -m venv env

# Activate the virtual environment
source env/bin/activate

# Upgrade pip inside the environment
pip install --upgrade pip

# Install tfhe-py (try PyPI first)
if pip install tfhe-py; then
    echo "tfhe-py installed from PyPI"
else
    echo "tfhe-py not found on PyPI, installing from GitHub"
    pip install git+https://github.com/pmuens/tfhe-py.git
fi

echo "Environment setup complete. Virtual environment 'env' activated."
