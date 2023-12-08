import time, subprocess
from azure.identity import DefaultAzureCredential
from azure.mgmt.sql import SqlManagementClient
from azure.storage.blob import BlobServiceClient, BlobClient
import datetime
from azure.storage.blob import ResourceTypes, AccountSasPermissions

def export_bacpac(database_name, storage_account_name, container_name, storage_account_key, admin_login, admin_password, resource_group_name, server_name, azure_subscription_id) -> BlobClient:

    credential = DefaultAzureCredential()
    sql_client = SqlManagementClient(credential, azure_subscription_id)

    bacpac_name = f"{database_name}_{time.strftime('%Y%m%d%H%M%S')}.bacpac"

    # Create a BlobServiceClient object which will be used to create a container client
    blob_service_client = BlobServiceClient(f"https://{storage_account_name}.blob.core.windows.net", credential=storage_account_key)

    # Get a client that can interact with the specified container in Azure Blob Storage.
    # This does not create a new container if one does not exist.
    container_client = blob_service_client.get_container_client(container_name)

    # Attempt to create the container. If the container already exists, this call will have no effect.
    # This ensures that the container exists before the script tries to upload a blob to it.
    container_client.create_container()

    def generate_account_sas(account_name, account_key, resource_types, permission, expiry):
        # Implementation of generate_account_sas function goes here
        pass


    # Create a blob client using the blob name from above
    blob_client = container_client.get_blob_client(bacpac_name)

    # Build the SAS URL for the blob
    sas_token = generate_account_sas(
        blob_service_client.account_name,
        account_key=storage_account_key,
        resource_types=ResourceTypes(object=True),
        permission=AccountSasPermissions(read=True),
        expiry=datetime.utcnow() + datetime.timedelta(hours=1)
    )

    bacpac_url = blob_client.url + "?" + sas_token

    # Export BACPAC
    operation = sql_client.databases.export(resource_group_name, server_name, database_name, admin_login, admin_password, bacpac_url)
    operation.wait()

    return blob_client

def import_bacpac_to_database(bacpac_url, server_name, database_name, admin_login, admin_password, sqlpackage_path):
    # Command to import BACPAC into a new database
    command = [
        sqlpackage_path,  # Path to SqlPackage.exe
        "/a:Import",  # Action to perform: Import
        f"/sf:{bacpac_url}",  # Source File: URL of the BACPAC file
        f"/tsn:{server_name}",  # Target Server Name: Name of the SQL Server instance
        f"/tdn:{database_name}",  # Target Database Name: Name of the database to import into
        f"/tu:{admin_login}",  # Target User: Login for the SQL Server instance
        f"/tp:{admin_password}"  # Target Password: Password for the SQL Server instance
    ]

    # Run the command
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Check if the command was successful
    if result.returncode != 0:
        print(f"Error importing BACPAC: {result.stderr.decode()}")
    else:
        print(f"Successfully imported BACPAC into database {database_name}")

def export_dacpac(server_name, database_name, admin_login, admin_password, dacpac_file_path, sqlpackage_path):
    # Command to export DACPAC from a database
    command = [
        sqlpackage_path,  # Path to SqlPackage.exe
        "/a:Extract",  # Action to perform: Extract
        f"/ssn:{server_name}",  # Source Server Name: Name of the SQL Server instance
        f"/sdn:{database_name}",  # Source Database Name: Name of the database to export from
        f"/su:{admin_login}",  # Source User: Login for the SQL Server instance
        f"/sp:{admin_password}",  # Source Password: Password for the SQL Server instance
        f"/tf:{dacpac_file_path}"  # Target File: Path where the DACPAC file will be saved
    ]

    # Run the command
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode != 0:
        print(f"Error exporting DACPAC: {result.stderr.decode()}")
    else:
        print(f"Successfully exported DACPAC to {dacpac_file_path}")