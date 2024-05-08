import requests
import signalfloweeg.portal as portal
from prefect import task, Flow

class APIgwAPI:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_portal_paths_api(self):
        url = f"{self.base_url}/api/get-portal-paths"
        response = requests.get(url)
        if response.status_code == 200:
            print("API Call Successful. Folder paths received:")
            data = response.json()
            import_folder = data.get('message', {}).get('imports', 'No import folder available')
            print(f"Import folder path: {import_folder}")
        else:
            print(f"API Call Failed. Status Code: {response.status_code}")
        return response.json()['message']['import']

    def get_import_catalog_api(self):
        url = f"{self.base_url}/api/get-import-catalog"
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