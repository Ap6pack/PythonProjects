# Stock Analysis Tool
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.txt)

## Overview

This Python script is designed for stock analysis using the `yfinance` library, enabling users to analyze historical stock data comprehensively. The script encompasses various functionalities, including fetching stock data, plotting closing prices, displaying moving averages, and visualizing the Relative Strength Index (RSI). Users can interactively input a stock symbol and date range to gain insights into historical stock performance.

## Features

- **Fetching Historical Stock Data:** Utilizes the `yfinance` library to download historical stock data for a specified stock symbol within a given date range.

- **Plotting Closing Prices:** Displays a visually intuitive plot of historical closing prices for the selected stock.

- **Moving Averages:** Calculates and plots 20-day and 50-day moving averages alongside closing prices for a more nuanced analysis.

- **Relative Strength Index (RSI):** Computes and plots the RSI for the chosen stock, aiding in identifying overbought or oversold conditions.

- **Input Validation:** Ensures accurate analysis by validating user input for stock symbols and date formats.

## Prerequisites

Make sure you have the following before running the script:

- Python 3.x
- A `requirements.txt` file specifying the required Python packages. (`yfinance`, `matplotlib`, `talib`)

## Getting Started

1. **Clone the repository:** `git clone https://github.com/Ap6pack/PythonProjects/stock-analysis-tool.git`

2. **Install the required packages:** pip install -r requirements.txt
   If you encounter errors installing TA-Lib, please follow the instructions [here](https://github.com/TA-Lib/ta-lib-python) to resolve the issue.

3. **Run the script:** `python /src/stockAnalysis.py`
   Follow the on-screen prompts to enter the stock symbol and date range.

## Usage

Execute the script and follow the interactive prompts to analyze historical stock data, gaining valuable insights into stock performance.



## Installing Python and Setting Up a Virtual Environment

### 1. Install Python 3.x
- **Windows:**
  - Visit the official Python website [here](https://www.python.org/downloads/).
  - Download the latest version of Python for Windows.
  - Run the installer, making sure to check the option to add Python to your PATH during installation.

- **macOS:**
  - macOS usually comes with Python pre-installed. You can check the version by opening a terminal and typing `python3 --version`.
  - If you need to update or install Python, you can use Homebrew (`brew install python`).

- **Linux (Debian/Ubuntu):**
  - Open a terminal and run the following commands:
    ```bash
    sudo apt update
    sudo apt install python3
    ```

### 2. Create a Virtual Environment (Optional but recommended)

- Creating a virtual environment helps isolate your project dependencies from the system-wide Python installation.

    ```bash
    pip install -r requirements.txt
    python3 -m venv venv
    ```
### 3. Activating the Virtual Environment

To activate the virtual environment, use the following commands:

- On Windows: `.\\venv\\Scripts\\activate`
- On macOS/Linux: `source venv/bin/activate`

### 4. Installing Dependencies from requirements.txt

1. Ensure you are in the project directory where `requirements.txt` is located.
2. Activate the virtual environment (if not already activated):
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ``` 

### 5. Running Your Python Script

To run your Python script, follow these steps:

1. Ensure the virtual environment is activated:

   - On Windows: `.\\venv\\Scripts\\activate`
   - On macOS/Linux: `source venv/bin/activate`

2. Run the script:

   ```bash
   python /src/stockAnalysis.py
   ```
   
## Contributing
Contributions are welcome! Feel free to open issues or pull requests for any improvements or additional features.

## License
This project is licensed under the MIT License, ensuring open collaboration and sharing of the codebase.
