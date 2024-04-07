import logging
from fastapi import FastAPI
import os
from signalfloweeg.portal import portal_utils
# from portal_utils import load_config
#from process_uploads import process_new_uploads

app = FastAPI()

@app.get("/process-uploads")
def process_uploads():
    logging.info("Processing new uploads...")
    config = portal_utils.load_config()
    logging.info(config)
    UPLOAD_PATH = config['folder_paths']['uploads']
    logging.info(f"UPLOAD_PATH: {UPLOAD_PATH}")
    #drop_all_tables()
    #process_new_uploads(upload_dir=UPLOAD_PATH)
    return {"message": "Upload processing completed."}

if __name__ == "__main__":
    import uvicorn
    if not os.path.exists("portal_files/logs/"):
        os.makedirs("portal_files/logs/")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S", handlers=[logging.FileHandler("portal_files/logs/sf_portal.log"), logging.StreamHandler()])
    uvicorn.run(app, host="0.0.0.0", port=8001)