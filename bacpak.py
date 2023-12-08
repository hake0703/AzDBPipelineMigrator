import os, time, json, argparse
from azure.identity import DefaultAzureCredential
from azure.mgmt.sql import SqlManagementClient
from azure.storage.blob import BlobServiceClient, BlobClient


def load_config(config_file_path):
    with open(config_file_path, 'r') as f:
        config = json.load(f)
    return config

def export_bacpac(database_name, storage_account_name, container_name, storage_account_key, admin_login, admin_password, resource_group_name, server_name, azure_subscription_id) -> BlobClient:

    credential = DefaultAzureCredential()
    sql_client = SqlManagementClient(credential, azure_subscription_id)

    bacpac_name = f"{database_name}_{time.strftime('%Y%m%d%H%M%S')}.bacpac"

    # Export BACPAC
    operation = sql_client.databases.export(resource_group_name, server_name, database_name, admin_login, admin_password, bacpac_name)
    operation.wait()

    blob_service_client = BlobServiceClient(f"https://{storage_account_name}.blob.core.windows.net", credential=storage_account_key)

    # Get a client that can interact with the specified container in Azure Blob Storage.
    # This does not create a new container if one does not exist.
    container_client = blob_service_client.get_container_client(container_name)

    # Attempt to create the container. If the container already exists, this call will have no effect.
    # This ensures that the container exists before the script tries to upload a blob to it.
    container_client.create_container()

    # Upload BACPAC to blob storage
    blob_client = container_client.get_blob_client(bacpac_name)
    with open(bacpac_name, "rb") as data:
        blob_client.upload_blob(data)

    os.remove(bacpac_name)

    return blob_client

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Export a BACPAC from Azure SQL Database.')
    parser.add_argument('config', type=str, help='Path to the configuration file.')

    args = parser.parse_args()

    # Load the configuration from the .json file
    config = load_config(args.config)

    result = export_bacpac(
        config['database_name'],
        config['storage_account_name'],
        config['container_name'],
        config['storage_account_key'],
        config['admin_login'],
        config['admin_password'],
        config['resource_group_name'],
        config['server_name'],
        config['subscription_id']
    )

    print(f"BACPAC file exported to the following storage account location: {result.url}")