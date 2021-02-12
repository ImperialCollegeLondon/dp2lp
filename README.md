# dp2lp
Source code and data for the paper "Optimal Hospital Care Scheduling During the SARS-CoV-2 Pandemic". The provided code takes as input patient groups dynamic programs (DP) data in MS Excel format, translates them to json, creates the LP fluid approximation and solves it using cplex. An open-source dataset is provided for the National Health System (NHS) in England. 

# Content description

Code:
- User\_input.xlsx: Excel file containing patient group-level data (DP)
- excel\_to\_json.py: converts the data in User\_input.xlsx into a json format
- LP\_script.py: takes as input the json data and writes the LP problem 
- prob\_sol.py: solves the LP problem in CPLEX 

Data (data\_sources folder):
- InputstoOpsModel\_DataDesc.docx: document describing the methodology used for data collection and treatment. For the methodology, please also refer to: https://github.com/HFAnalyticsLab/overflow_analysis
- Optimization\_model\_input\_data.xlsx: original input data, subsequently organized in the User\_input.xlsx format

# Additional notes:
For running the model, the following might be needed:
- remove disease groups with 0 inflow, like ICD15\_AGE3
- Restart Python kernel before running each python script