# HHOSSA-Based Data Balancing Tool

This project implements a data balancing tool using the HHOSSA SMOTE algorithm. The tool balances imbalanced datasets by applying the Harris Hawk Optimization (HHO) and Sparrow Search Algorithm (SSA) to enhance the SMOTE technique.

## Installation

To set up the project, run:


pip install -r requirements.txt


## Usage

To run the tool, use the following command:


python main.py <path_to_dataset>


Replace `<path_to_dataset>` with the path to your CSV dataset.

## Project Structure

- `hhosmote.py`: Implementation of the HHOSSA and SMOTE algorithm.
- `data_preprocessing.py`: Functions for data loading and preprocessing.
- `main.py`: Main script to run the tool.
- `utils.py`: Placeholder for utility functions.
- `requirements.txt`: Project dependencies.
- `README.md`: Project documentation.

## Example

An example usage:


python main.py data/your_dataset.csv


This will generate a balanced dataset saved as `balanced_dataset.csv`.

### Running the Project

1. **Set up the environment:**

   
   pip install -r requirements.txt
   

2. **Run the tool:**

   
   python main.py path_to_your_dataset.csv