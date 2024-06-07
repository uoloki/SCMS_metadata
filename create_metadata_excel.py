import os
import pandas as pd
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.cosmos import CosmosClient, exceptions, PartitionKey
from openpyxl import load_workbook

# Function to read credentials from a file
def read_credentials(file_path):
    credentials = {}
    with open(file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            credentials[key] = value
    return credentials

# Function to get resource metadata
def get_blockchain_member_metadata(resource_client, resource_group, blockchain_member):
    try:
        member = resource_client.resources.get(
            resource_group_name=resource_group,
            resource_provider_namespace='Microsoft.Blockchain',
            parent_resource_path='',
            resource_type='blockchainMembers',
            resource_name=blockchain_member,
            api_version='2018-06-01-preview'
        )
        return member.serialize(True)
    except Exception as e:
        print(f"Error fetching blockchain member metadata: {e}")
        return {}

def get_blockchain_nodes_metadata(resource_client, resource_group, blockchain_member):
    try:
        nodes = resource_client.resources.list_by_resource_group(
            resource_group_name=resource_group,
            filter=f"resourceType eq 'Microsoft.Blockchain/blockchainNodes' and substringof('{blockchain_member}', name)"
        )
        return [node.serialize(True) for node in nodes]
    except Exception as e:
        print(f"Error fetching blockchain nodes metadata: {e}")
        return []

def get_blockchain_contracts_metadata(credentials):
    try:
        endpoint = credentials['COSMOS_DB_ENDPOINT']
        key = credentials['COSMOS_DB_KEY']
        database_name = credentials['COSMOS_DB_DATABASE_NAME']
        container_name = credentials['COSMOS_DB_CONTAINER_NAME']
        
        client = CosmosClient(endpoint, key)
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)

        query = "SELECT * FROM c WHERE c.blockchain_member = @blockchain_member"
        parameters = [{'name': '@blockchain_member', 'value': credentials['AZURE_BLOCKCHAIN_MEMBER_NAME']}]
        
        contracts = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))

        return contracts
    except Exception as e:
        print(f"Error fetching blockchain contracts metadata: {e}")
        return []

# Function to adjust the column width
def adjust_column_widths(sheet):
    for column_cells in sheet.columns:
        length = max(len(str(cell.value)) for cell in column_cells)
        sheet.column_dimensions[column_cells[0].column_letter].width = length + 2

# Function to add _Y columns
def add_y_columns(dataframe):
    for col in dataframe.columns:
        dataframe[f"{col}_Y"] = dataframe[col]
    return dataframe

if __name__ == "__main__":
    try:
        # Read credentials from the file
        credentials = read_credentials('credentials.txt')
        subscription_id = credentials['AZURE_SUBSCRIPTION_ID']
        resource_group_name = credentials['AZURE_RESOURCE_GROUP_NAME']
        blockchain_member_name = credentials['AZURE_BLOCKCHAIN_MEMBER_NAME']
        
        # Initialize the Resource management client
        credential = DefaultAzureCredential()
        resource_client = ResourceManagementClient(credential, subscription_id)
        
        member_metadata = get_blockchain_member_metadata(resource_client, resource_group_name, blockchain_member_name)
        nodes_metadata = get_blockchain_nodes_metadata(resource_client, resource_group_name, blockchain_member_name)
        contracts_metadata = get_blockchain_contracts_metadata(credentials)
        
        # Create dataframes
        member_df = pd.DataFrame([member_metadata])
        member_df.columns = [f"{col}_member" for col in member_df.columns]
        member_df = add_y_columns(member_df)
        
        nodes_df = pd.DataFrame(nodes_metadata)
        nodes_df.columns = [f"{col}_node" for col in nodes_df.columns]
        nodes_df = add_y_columns(nodes_df)
        
        contracts_df = pd.DataFrame(contracts_metadata)
        contracts_df.columns = [f"{col}_contract" for col in contracts_df.columns]
        contracts_df = add_y_columns(contracts_df)
        
        # Write to Excel with separate sheets
        with pd.ExcelWriter('blockchain_metadata.xlsx', engine='openpyxl') as writer:
            member_df.to_excel(writer, sheet_name='Member Metadata', index=False)
            nodes_df.to_excel(writer, sheet_name='Nodes Metadata', index=False)
            contracts_df.to_excel(writer, sheet_name='Contracts Metadata', index=False)
            
            adjust_column_widths(writer.sheets['Member Metadata'])
            adjust_column_widths(writer.sheets['Nodes Metadata'])
            adjust_column_widths(writer.sheets['Contracts Metadata'])
        
        print("Metadata has been written to 'blockchain_metadata.xlsx'")
    except Exception as e:
        print(f"An error occurred: {e}")
