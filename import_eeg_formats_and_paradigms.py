from portal_utils import load_config
from db import get_db_session
from models import EegFormat, EegParadigm
from db import drop_all_tables




if __name__ == '__main__':
    drop_all_tables()
    generate_eeg_format_and_paradigm()