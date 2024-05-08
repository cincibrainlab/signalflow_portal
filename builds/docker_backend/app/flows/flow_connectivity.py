import requests
import signalfloweeg.portal as portal
from prefect import task, Flow

def call_get_portal_paths_api():
    url = "http://localhost:3005/api/get-portal-paths"
    response = requests.get(url)
    if response.status_code == 200:
        print("API Call Successful. Folder paths received:")
        data = response.json()
        import_folder = data.get('message', {}).get('imports', 'No import folder available')
        print(f"Import folder path: {import_folder}")
    else:
        print(f"API Call Failed. Status Code: {response.status_code}")
    return response.json()['message']['import']

def call_get_import_catalog_api():
    url = "http://localhost:3005/api/get-import-catalog"
    response = requests.get(url)
    if response.status_code == 200:
        print("API Call Successful. Data received:")
        data = response.json()
        if data:
            first_record = data[0]
            original_name = first_record.get('original_name', 'No name available')
            print(f"First record's file name: {original_name}")
        else:
            print("No data available.")
    else:
        print(f"API Call Failed. Status Code: {response.status_code}")
    return response.json()[0]['upload_id']


@task
def prepare_input():
    pass

@task
def execute_operation():
    pass

@task
def prepare_output():
    pass

with Flow("my_flow") as flow:
    result1 = prepare_input()
    result2 = execute_operation()
    result3 = prepare_output()


if __name__ == "__main__":
    portal_paths = call_get_portal_paths_api()
    import_catalog = call_get_import_catalog_api()
    complete_file_name = f"{portal_paths}/{import_catalog}"
    set_dest_path, fdt_dest_path = portal.import_catalog.copy_import_files(import_catalog)
    print(f"Complete file name: {complete_file_name}")


