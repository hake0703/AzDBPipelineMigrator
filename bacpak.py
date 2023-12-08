from azure.identity import DefaultAzureCredential
from azure.mgmt.sql import SqlManagementClient
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os
import time

def export_bacpac(database_name, storage_account_name, container_name, storage_account_key, admin_login, admin_password, resource_group_name, server_name):
    # Initialize SQL client
    credential = DefaultAzureCredential()
    sql_client = SqlManagementClient(credential, "<YourSubscriptionId>")

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

    return f"BACPAC file exported to: {storage_account_name}/{container_name}/{bacpac_name}"

if __name__ == "__main__":
    # Replace with your actual values
    database_name = "<YourDatabaseName>"
    storage_account_name = "<YourStorageAccountName>"
    container_name = "<YourContainerName>"
    storage_account_key = "<YourStorageAccountKey>"
    admin_login = "<YourAdminLogin>"
    admin_password = "<YourAdminPassword>"
    resource_group_name = "<YourResourceGroupName>"
    server_name = "<YourSqlServerName>"

    result = export_bacpac(
        database_name,
        storage_account_name,
        container_name,
        storage_account_key,
        admin_login,
        admin_password,
        resource_group_name,
        server_name
    )

    print(result)
