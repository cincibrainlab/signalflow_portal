import os

import mne
import sqlalchemy as sa

from prefect import task, flow

from signalfloweeg.portal.db_connection import get_session
from signalfloweeg.portal.import_catalog import copy_import_files
from signalfloweeg.portal.portal_utils import load_config
from signalfloweeg.viz.heatmap import heatmap_power
from signalfloweeg.models import ImportCatalog, EegAnalyses


@task (retries = 3)
def getRaw(upload_id: str, upload_path: str):
    try: 
        set_dest_path, fdt_dest_path = copy_import_files(upload_id)
        raw_eeg = mne.io.read_raw(set_dest_path)

        if os.path.exists(set_dest_path):
            os.remove(set_dest_path)
            print(f"Removed SET file {set_dest_path}")
        if fdt_dest_path and os.path.exists(fdt_dest_path):
            os.remove(fdt_dest_path)
            print(f"Removed FDT file {fdt_dest_path}")
        return raw_eeg
    
    except Exception as e:
        print("Exception Occured when creating Raw Obj: " + e)
        raise

@task
def heatmap(raw: mne.io.Raw):
    epochs = mne.make_fixed_length_epochs(raw, duration=5, preload=False)
    heatmap_power(epochs)

@flow(log_prints=True)
def AnalysisFlow():
    config = load_config()
    upload_path = config["folder_paths"]["uploads"]

    with get_session() as session:
        import_ids = session.query(ImportCatalog).all()
        analyses = session.query(EegAnalyses).all()
        session.close()

    for analysis in analyses:
        for file in import_ids:
            if file.eeg_format in analysis.valid_formats and file.eeg_paradigm in analysis.valid_paradigms:
                #Run analysis
                pass
            pass
        pass


    raw_eeg = getRaw("fbba02b1598894178a0550d684f82d8e", upload_path)
    heatmap(raw_eeg)
    print("Ran heatmap")


if __name__ == "__main__":
    AnalysisFlow()

