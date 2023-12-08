import os, time
from azure.identity import DefaultAzureCredential
from azure.mgmt.sql import SqlManagementClient
from azure.storage.blob import BlobServiceClient, BlobClient

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