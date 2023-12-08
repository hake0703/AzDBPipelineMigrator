import os, time, json, argparse
from azure.identity import DefaultAzureCredential
from azure.mgmt.sql import SqlManagementClient
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient


def load_config(config_file_path):
    with open(config_file_path, 'r') as f:
        config = json.load(f)
    return config

def export_bacpac(database_name, storage_account_name, container_name, storage_account_key, admin_login, admin_password, resource_group_name, server_name, azure_subscription_id):
    # Initialize SQL client
    credential = DefaultAzureCredential()
    sql_client = SqlManagementClient(credential, azure_subscription_id)

    # Generate BACPAC name based on database name
    bacpac_name = f"{database_name}_{time.strftime('%Y%m%d%H%M%S')}.bacpac"

    # Get server details
    server = sql_client.servers.get(resource_group_name, server_name)

    # Export BACPAC
    operation = sql_client.databases.export(resource_group_name, server_name, database_name, admin_login, admin_password, bacpac_name)
    operation.wait()

    # Initialize Blob service client
    blob_service_client = BlobServiceClient(f"https://{storage_account_name}.blob.core.windows.net", credential=storage_account_key)

    # Get or create container
    container_client = blob_service_client.get_container_client(container_name)
    container_client.create_container()

    # Upload BACPAC to blob storage
    blob_client = container_client.get_blob_client(bacpac_name)
    with open(bacpac_name, "rb") as data:
        blob_client.upload_blob(data)

    # Clean up local BACPAC file
    os.remove(bacpac_name)

    return f"{storage_account_name}/{container_name}/{bacpac_name}"

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

    print(f"BACPAC file exported to the following storage account location: {result}")