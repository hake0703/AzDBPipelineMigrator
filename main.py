# We will break out the bacpak module and put the main into here. We need to start breaking this up
# so that we can use this stuff on its own.
import argparse
import config_loader
import bacpac_operations

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Export a BACPAC from Azure SQL Database.')
    parser.add_argument('config', type=str, help='Path to the configuration file.')

    args = parser.parse_args()

    # Load the bacbak configuration from the .json file
    config = config_loader.from_json_file(args.config)

    result = bacpac_operations.export_bacpac(
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