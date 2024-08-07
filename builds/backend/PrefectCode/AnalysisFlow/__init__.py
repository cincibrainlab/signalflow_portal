# AnalysisFlow/__init__.py

#* How to start prefect
# prefect cloud login
# prefect work-pool create analysis-process-pool
# prefect worker start --pool analysis-process-pool

# Import all modules in the package
#* You will need to import each analysis flow here
from .TemplateAnalysis import TemplateAnalysis_Flow
from .ComputePsdAnalysisMatlab import ComputePsdAnalysisMatlab_Flow


# Define package-level variables
#* Currently the only place new analysis flows need to be added is here and in analysis_flows.yaml
#* The key needs to be put both in this dictionary and in the analysis_flows.yaml file
analysis_flows = {
    "ComputePsd - Python": TemplateAnalysis_Flow,
    "ComputePsd - Matlab": ComputePsdAnalysisMatlab_Flow,
    # Add more flows here as needed
}

# Optionally, define a function or perform other initialization tasks
# def initialize_package():
#     print("Initializing my_package...")

# Define __all__ to specify which modules or subpackages should be imported
# __all__ = ["module1", "module2"]