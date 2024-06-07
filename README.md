# SCMS_metadata
---

### Prerequisites

1. **Python Environment**: Ensure you have Python installed on your system.
2. **Required Packages**: Install the necessary Python packages using the following command:
    ```sh
    pip install azure-mgmt-resource azure-identity azure-cosmos pandas openpyxl
    ```

### Step-by-Step Guide

#### 1. Prepare the Credentials

Create a file named `credentials.txt` in the same directory as your scripts. This file should contain your Azure subscription credentials and Cosmos DB configuration. Format it as follows:
```plaintext
AZURE_SUBSCRIPTION_ID=your_subscription_id
AZURE_RESOURCE_GROUP_NAME=your_resource_group_name
AZURE_BLOCKCHAIN_MEMBER_NAME=your_blockchain_member_name
COSMOS_DB_ENDPOINT=your_cosmos_db_endpoint
COSMOS_DB_KEY=your_cosmos_db_key
COSMOS_DB_DATABASE_NAME=your_database_name
COSMOS_DB_CONTAINER_NAME=your_container_name
```

Replace `your_subscription_id`, `your_resource_group_name`, `your_blockchain_member_name`, `your_cosmos_db_endpoint`, `your_cosmos_db_key`, `your_database_name`, and `your_container_name` with your actual Azure and Cosmos DB details.

#### 2. Fetch Metadata and Create Excel File

This script will fetch the metadata from Azure Blockchain resources and create an Excel file (`blockchain_metadata.xlsx`) with the data.

**Script Name**: `create_metadata_excel.py`

**Overview**:
- Reads credentials from `credentials.txt`.
- Fetches blockchain member, node, and contract metadata using Azure Resource Management and Cosmos DB.
- Adds columns with `_Y` suffix for each data point.
- Writes the metadata to an Excel file with separate sheets for members, nodes, and contracts.

**Running the Script**:
```sh
python create_metadata_excel.py
```

**Expected Output**:
- `blockchain_metadata.xlsx` with three sheets: "Member Metadata", "Nodes Metadata", and "Contracts Metadata". Each sheet contains the corresponding metadata with `_Y` columns.

### Adapting SQL Queries

#### Customizing SQL Queries

You might need to customize the SQL queries based on your specific requirements. Here are a few scenarios and how you can adapt the SQL queries in the `get_blockchain_contracts_metadata` function.

#### Scenario 1: Fetch All Contracts for a Specific Blockchain Member
The provided script includes a query to fetch all contracts for a specific blockchain member:
```python
query = "SELECT * FROM c WHERE c.blockchain_member = @blockchain_member"
parameters = [{'name': '@blockchain_member', 'value': credentials['AZURE_BLOCKCHAIN_MEMBER_NAME']}]
```

#### Scenario 2: Fetch Contracts with Specific Fields
If you only want to fetch specific fields (e.g., contract address and name):
```python
query = "SELECT c.contract_address, c.contract_name FROM c WHERE c.blockchain_member = @blockchain_member"
parameters = [{'name': '@blockchain_member', 'value': credentials['AZURE_BLOCKCHAIN_MEMBER_NAME']}]
```

#### Scenario 3: Fetch Contracts Based on Additional Filters
If you need to apply additional filters, such as contracts deployed after a certain date:
```python
query = """
    SELECT * FROM c 
    WHERE c.blockchain_member = @blockchain_member 
    AND c.deployed_date > @deployed_date
"""
parameters = [
    {'name': '@blockchain_member', 'value': credentials['AZURE_BLOCKCHAIN_MEMBER_NAME']},
    {'name': '@deployed_date', 'value': '2022-01-01'}
]
```

**Example of a Custom Filter Implementation**:
```python
def get_blockchain_contracts_metadata(credentials, additional_filters=None):
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

        if additional_filters:
            for filter_name, filter_value in additional_filters.items():
                query += f" AND c.{filter_name} = @{filter_name}"
                parameters.append({'name': f'@{filter_name}', 'value': filter_value})

        contracts = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))

        return contracts
    except Exception as e:
        print(f"Error fetching blockchain contracts metadata: {e}")
        return []
```

**Using Custom Filters**:
```python
additional_filters = {
    'deployed_date': '2022-01-01'
}

contracts_metadata = get_blockchain_contracts_metadata(credentials, additional_filters)
```

### Detailed Explanation of Key Functions

#### `read_credentials(file_path)`
- **Purpose**: Reads the Azure subscription credentials from a file.
- **Input**: Path to the credentials file.
- **Output**: Dictionary containing the credentials.

#### `get_blockchain_member_metadata(resource_client, resource_group, blockchain_member)`
- **Purpose**: Fetches metadata for a blockchain member.
- **Input**: Resource management client, resource group name, blockchain member name.
- **Output**: Serialized metadata of the blockchain member.

#### `get_blockchain_nodes_metadata(resource_client, resource_group, blockchain_member)`
- **Purpose**: Fetches metadata for blockchain nodes.
- **Input**: Resource management client, resource group name, blockchain member name.
- **Output**: List of serialized metadata for each blockchain node.

#### `get_blockchain_contracts_metadata(credentials, additional_filters=None)`
- **Purpose**: Fetches metadata for blockchain contracts from Cosmos DB.
- **Input**: Credentials dictionary, additional filters (optional).
- **Output**: List of contract metadata.

#### `add_y_columns(dataframe)`
- **Purpose**: Adds `_Y` columns to a DataFrame for each existing column.
- **Input**: DataFrame.
- **Output**: Modified DataFrame with `_Y` columns.

#### `adjust_column_widths(sheet)`
- **Purpose**: Adjusts the width of columns in an Excel sheet to fit the text.
- **Input**: Excel sheet object.
- **Output**: None (modifies the sheet in place).

#### `filter_columns_with_Y(df)`
- **Purpose**: Filters columns based on the presence of 'Y' in `_Y` columns.
- **Input**: DataFrame.
- **Output**: Filtered DataFrame with only the necessary columns.

#### `process_excel_file(input_file, output_file)`
- **Purpose**: Processes an Excel file to filter columns and adjust column widths.
- **Input**: Input Excel file name, output Excel file name.
- **Output**: None (creates a new filtered Excel file).

---

### Script 2: `filter_metadata_excel.py`

**Overview**:
- Reads the original Excel file (`blockchain_metadata.xlsx`).
- Filters columns based on the presence of 'Y' in `_Y` columns.
- Writes the filtered data to a new Excel file with adjusted column widths.

**Changes You Might Need**:
- **Input and Output File Names**: Ensure the input file name matches the output of the first script. The script assumes the input file is `blockchain_metadata.xlsx` and outputs to `filtered_blockchain_metadata.xlsx`.

**Running the Script**:
```sh
python filter_metadata_excel.py
```

**Expected Output**:
- `filtered_blockchain_metadata.xlsx` with filtered data based on the presence of 'Y' in `_Y` columns.
