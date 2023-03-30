import os
import boto3
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Set up a Slack bot app using the bot token
client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

# Set up an AWS client and define the DynamoDB table
dynamodb = boto3.resource("dynamodb")
table_name = os.environ["DYNAMODB_TABLE_NAME"]
table = dynamodb.Table(table_name)

# Define an AWS Lambda function to update the user count in DynamoDB
def update_user_count(event, context):
    # Get the current time
    current_time = int(event["time"])

    # Get all items in the DynamoDB table
    response = table.scan()

    # Loop through the items and update the user count
    for item in response["Items"]:
        channel_id = item["channel_id"]
        timestamp = float(item["timestamp"])
        num_users = int(item["num_users"])

        # Check if 24 hours have passed since the initial message was sent
        if current_time - timestamp >= 86400:
            # Get the current number of users in the channel
            try:
                response = client.conversations_info(channel=channel_id)
                new_num_users = response["channel"]["num_members"]
            except SlackApiError as e:
                print("Error getting conversation info: {}".format(e))
                return

            # Update the user count in DynamoDB
            table.update_item(
                Key={
                    "channel_id": channel_id,
                    "timestamp": item["timestamp"]
                },
                UpdateExpression="set num_users = :nu",
                ExpressionAttributeValues={
                    ":nu": new_num_users
                }
            )

            # Send a message with the updated user count
            message_text = "{} of users have left the channel in 24 hours".format(new_num_users)
            try:
                client.chat_postMessage(
                    channel=channel_id,
                    text=message_text
                )
            except SlackApiError as e:
                print("Error posting message: {}".format(e))
                return

            # Delete the item from DynamoDB
            table.delete_item(
                Key={
                    "channel_id": channel_id,
                    "timestamp": item["timestamp"]
                }
            )
