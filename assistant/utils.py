import os
import boto3

def write_string_to_file(file_name, content):
    #if file does not exist create it
    if not os.path.exists(file_name):
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(content)
    else:
        with open(file_name, 'a', encoding='utf-8') as file:
            file.write(content)


def get_files_content(path):
    file_contents = {}  # Initialize an empty dictionary to store file names as keys and their contents as values
    for root, dirs, files in os.walk(path):
        for file_name in files:
            file_path = os.path.join(root, file_name)  # Construct the full file path
            with open(file_path, 'r', encoding='utf-8') as file:  # Open and read the file
                content = file.read()
            file_contents[file_name] = content  # Assign the content to the corresponding file name in the dictionary
    return file_contents

def get_item_from_dynamodb(table_name, primary_key, primary_key_value):
    # Create a DynamoDB service client
    dynamodb = boto3.resource('dynamodb')

    # Access the specified table
    table = dynamodb.Table(table_name)

    try:
        # Fetch the item based on primary key
        response = table.get_item(
            Key={
                primary_key: primary_key_value
            }
        )
        item = response.get('Item', {})

        if not item:
            print(f"No item found with {primary_key} = {primary_key_value}")
            return None

        return item

    except Exception as e:
        print(f"Error fetching item from DynamoDB: {e}")
        return None
    
