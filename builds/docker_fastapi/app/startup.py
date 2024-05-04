import os
from signalfloweeg.portal.db_connection import get_session, is_database_connected
from signalfloweeg.portal.models import Startup
from signalfloweeg.portal.portal_config import check_database_and_tables, load_config_from_yaml
from sqlalchemy.exc import SQLAlchemyError

def add_portal_config_path(portal_config_path):
    try:
        with get_session() as session:
            startup_record = session.query(Startup).filter_by(id=1).first()
            if not startup_record:
                startup_record = Startup(id=1)
                session.add(startup_record)
            
            startup_record.sf_config_path = portal_config_path
            session.commit()
            print(f"✅ Startup table updated with portal config path: {portal_config_path}")
            return True
    except SQLAlchemyError as e:
        print(f"Failed to update startup table: {e}")
        return False

def free_disk_space(target_path):
    """
    Function to check if the free disk space in a given path is greater than 10 GB
    :param target_path: The path to check the free disk space
    :return: True if the free disk space is greater than 10 GB, False otherwise
    """
    import shutil
    total, used, free = shutil.disk_usage(target_path)
    return (free // (2**30)) > 10  # Convert bytes to gigabytes and check if greater than 10 GB

def entry_point():
    from rich.console import Console
    console = Console()
    console.print("🚀 [bold magenta]Entrypoint Checks:[/bold magenta]")
    entrypoint_check = dict()
    
    # check if database is connected
    entrypoint_check['database_connected'] = is_database_connected()
    status_icon = '✅' if entrypoint_check['database_connected'] else '❌'
    console.print(f"[bold]{status_icon} Database Connected:[/bold] [yellow]{entrypoint_check['database_connected']}[/yellow]")
    if not entrypoint_check['database_connected']:
        return False

    # Add the portal config path to the database
    portal_config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'portal_config.yaml')
    entrypoint_check['portal_config_path'] = add_portal_config_path(portal_config_path)
    status_icon = '✅' if entrypoint_check['portal_config_path'] else '❌'
    console.print(f"[bold]{status_icon} Portal Config Path Assigned:[/bold] [yellow]{portal_config_path}[/yellow]")
   
    # # check if the database and tables are present
    entrypoint_check['database_and_tables'] = check_database_and_tables()
    status_icon = '✅' if entrypoint_check['database_and_tables'] else '❌'
    console.print(f"[bold]{status_icon} Database Tables Validated:[/bold] [yellow]{entrypoint_check['database_and_tables']}[/yellow]")
  
    # # check if portal_config.yaml is loaded
    entrypoint_check['config_loaded'] =  load_config_from_yaml()
    status_icon = '✅' if entrypoint_check['config_loaded'] else '❌'
    console.print(f"[bold]{status_icon} Portal Config Loaded:[/bold] [yellow]{entrypoint_check['config_loaded']}[/yellow]")
   
    # check if free disk space is greater than 10 GB
    entrypoint_check['disk_space'] = free_disk_space(portal_config_path)
    status_icon = '✅' if entrypoint_check['disk_space'] else '❌'
    console.print(f"[bold]{status_icon} Free Disk Space Check (> 10 GB):[/bold] [yellow]{entrypoint_check['disk_space']}[/yellow]")

    all_checks_passed = all(entrypoint_check.values())
    return all_checks_passed


if __name__ == "__main__":
    valid_entry = entry_point()
