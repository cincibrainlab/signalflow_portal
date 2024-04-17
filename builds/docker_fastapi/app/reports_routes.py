from fastapi import APIRouter
import logging
import signalfloweeg.portal as portal

router = APIRouter()


@router.get("/api/load-database-summary")
def load_database_summary():
    logging.info("Loading database summary...")
    summary = portal.db_utilities.generate_database_summary()
    return {"message": summary}


if __name__ == "__main__":
    load_database_summary()
