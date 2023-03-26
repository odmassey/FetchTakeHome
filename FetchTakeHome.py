"""FetchTakeHome.py

Python file to read messages from AWS SQS queue and store them in a postgres database
__author__ = "Owen Massey"
__email__ = "odmassey@gmail.com"
"""
import boto3
import hashlib
from datetime import date
import psycopg2
import json
import copy

def receive_messages(messages):
    """Recieves messages from queue"""
    sqs = boto3.client(
        "sqs",
        # Local host connections still need dummy key values
        aws_access_key_id = "accesskeyid",
        aws_secret_access_key = "secretaccesskey",
        endpoint_url="http://localhost:4566/000000000000/login-queue"
    )

    response = sqs.receive_message(
        QueueUrl="http://localhost:4566/000000000000/login-queue",
        AttributeNames=[
            "All"
        ],
        MaxNumberOfMessages=10,
    )
    # Check if there is messages to read
    if "Messages" in response.keys():
        for message in response["Messages"]:
            messages.append(message)
            # Must delete messages to avoid repetition
            sqs.delete_message(
                QueueUrl="http://localhost:4566/000000000000/login-queue",
                ReceiptHandle=message["ReceiptHandle"]
            )
        receive_messages(messages)
    return messages

def hide_pii(body):
    """Hides desired values"""
    new_body = copy.deepcopy(body)
    # hashlib.sha256 is non random so repeated sensitive info should have the same value (can see duplicates)
    new_body["ip"] = hashlib.sha256(body['ip'].encode('utf-8')).hexdigest()
    new_body["device_id"] = hashlib.sha256(body['device_id'].encode('utf-8')).hexdigest()
    return new_body

def send_to_postgres(connection, m):
    """Sends row data to postgres database.  Takes connection so program is not repeating connections for every row."""
    
    cursor = connection.cursor()
    cursor.execute("INSERT INTO user_logins VALUES(%s,%s,%s,%s,%s,%s,%s)", [
        m["user_id"],
        m["device_type"],
        m['ip'],
        m['device_id'],
        m["locale"],
        # Changes version number (2.0.3) into integer (20003) to accommodate double didget version numbers
        "0".join(x for x in m["app_version"].split(".")),
        date.today()
    ])
    connection.commit()
    cursor.close()

def main():
    """Main function that controls the logic"""
    messages = receive_messages([])
    hidden_messages = []
    for message in messages:
        # Checks if message has required info
        if all(key in message["Body"] for key in ("user_id", "app_version", "device_type", "ip", "locale", "device_id")):
            hidden_messages.append(hide_pii(json.loads(message["Body"])))
        # else:
        #     # print(f"Bad Message {message}")
    connection = psycopg2.connect(
        database="postgres", user="postgres", password="postgres", host="localhost", port="5432"
    )
    for message in hidden_messages:
        send_to_postgres(connection, message)
    

if __name__ == "__main__":
    main()
