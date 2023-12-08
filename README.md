## Manual Migration Using Azure Portal

### Navigate to Azure Portal
Go to the [Azure Portal](https://portal.azure.com/).

### Find Your Database
Locate and select your Azure SQL Database in the portal.

### Export Database
In the database menu, under the "Settings" section, find and select "Export database". Follow the wizard to export the database schema to a BACPAC file.

### Convert BACPAC to DACPAC
The exported file will be in BACPAC format. You can use the "bacpac to dacpac" converter tool available on [GitHub: Microsoft/bacpac-to-dacpac](https://github.com/Microsoft/bacpac-to-dacpac).

Alternatively, you can import the BACPAC into Visual Studio and then use Visual Studio to generate the DACPAC:

1. Open Visual Studio and create a new SQL Server Database Project.
2. Right-click on the project and choose "Import" > "Data-tier Application (.bacpac)".
3. Follow the wizard to import the BACPAC into your project.
4. Build the project to generate the DACPAC.

After generating the DACPAC using one of these methods, you can use the DACPAC file in your Azure DevOps pipeline for database schema deployment, as discussed in previous responses.

### PowerShell Script for Automation
To generate a BACPAC file from an Azure SQL Database using Azure Portal and include a PowerShell script for automation, follow these steps:

1. Navigate to Azure Portal.
2. Locate and select your Azure SQL Database in the portal.
3. In the database menu, under the "Settings" section, find and select "Export database".
4. Follow the wizard to export the database schema to a BACPAC file.
5. Once the export is complete, download the generated BACPAC file.

## Automatic Migration
Can be done with the python script within this repo. 

