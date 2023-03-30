import os
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

# Set up a Slack bot app using the bot token and signing secret
app = App(token=os.environ["SLACK_BOT_TOKEN"], signing_secret=os.environ["SLACK_SIGNING_SECRET"])

# Set up a Slack request handler for AWS Lambda
handler = SlackRequestHandler(app)

# Define an AWS Lambda function to handle incoming messages
def message_handler(event, context):
    # Pass the event to the request handler
    response = handler.handle(event, context)

    # Return the response as a dictionary
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": response
    }

# Define a message listener for the "general" channel
@app.event("message")
def handle_message_event(event, logger):
    channel_id = event["channel"]
    if channel_id != "C1234567890":  # Replace with the ID of the "general" channel
        return
    message_text = event["text"]

    # Check if the message contains "@here" or "@channel"
    if "@here" in message_text or "@channel" in message_text:
        # Get the number of users in the channel
        num_users = len(app.client.conversations_members(channel=channel_id)["members"])

        # Send a message asking if the @here or @channel was necessary
        response = app.client.chat_postMessage(
            channel=channel_id,
            text="Please note, there is {} of users in this channel, was this really necessary?".format(num_users)
        )

# Define a main function to run the app locally (for testing)
def main():
    app.start(port=3000)

if __name__ == "__main__":
    main()
