import yaml
from sqlalchemy.exc import SQLAlchemyError
from signalfloweeg.portal.models import AnalysisConfig
from signalfloweeg.portal.db_connection import get_session
import json


def import_analysis_config():
    # Load YAML configuration
    with open("analysis_config.yaml", 'r') as file:
        config_data = yaml.safe_load(file)
    
    # Connect to the database
    with get_session() as session:
        # Iterate through each analysis configuration
        for analysis in config_data['analyses']:
            try:
                # Prepare the data
                function_name = analysis['function_name']
                description = analysis.get('description', None)
                eeg_formats = json.dumps(analysis['eeg_formats'])
                eeg_paradigms = json.dumps(analysis['eeg_paradigms'])
                parameters = json.dumps(analysis['parameters'])
                
                # Check if the analysis already exists
                existing_analysis = session.query(AnalysisConfig).filter_by(function_name=function_name).first()
                
                if existing_analysis:
                    # Update existing record
                    existing_analysis.description = description
                    existing_analysis.eeg_formats = eeg_formats
                    existing_analysis.eeg_paradigms = eeg_paradigms
                    existing_analysis.parameters = parameters
                else:
                    import uuid
                    # Create new record with a unique identifier
                    new_analysis = AnalysisConfig(
                        id=str(uuid.uuid4()),
                        function_name=function_name,
                        description=description,
                        eeg_formats=eeg_formats,
                        eeg_paradigms=eeg_paradigms,
                        parameters=parameters
                    )
                    session.add(new_analysis)
                # Commit the changes
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                print(f"Error importing analysis config: {e}")

# Call the function to import analysis configurations
import_analysis_config()
