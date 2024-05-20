import yaml
from sqlalchemy.orm import Session

# Models definition (add them as needed)
class ParameterNamingConvention(Base):
    __tablename__ = 'parameter_naming_conventions'
    id = Column(Integer, primary_key=True)
    parameter_name = Column(String, unique=True, nullable=False)
    expected_format = Column(String, nullable=False)

def load_yaml_config(filepath):
    with open(filepath, 'r') as file:
        return yaml.safe_load(file)

def validate_naming_conventions_first(config, session):
    # Fetch naming conventions from the database
    naming_conventions = {p.parameter_name: p.expected_format for p in session.query(ParameterNamingConvention).all()}
    errors = []
    for analysis in config['analyses']:
        for param_name in analysis['parameters']:
            if param_name not in naming_conventions:
                errors.append(f"Unexpected parameter name: {param_name} in analysis {analysis['function_name']}")
    if errors:
        raise ValueError(f"Validation errors found: {errors}")

def apply_defaults_after_validation(config, session):
    # Fetch analysis parameters
    analysis_dict = {a.function_name: a.default_parameters for a in session.query(Analysis).all()}
    for analysis in config['analyses']:
        function_name = analysis['function_name']
        if function_name in analysis_dict:
            default_params = analysis_dict[function_name] or {}
            analysis['parameters'] = {**default_params, **analysis['parameters']}

# Example usage
yaml_filepath = 'path/to/analysis_config.yaml'
with Session(engine) as session:
    config = load_yaml_config(yaml_filepath)
    validate_naming_conventions_first(config, session)
    apply_defaults_after_validation(config, session)
