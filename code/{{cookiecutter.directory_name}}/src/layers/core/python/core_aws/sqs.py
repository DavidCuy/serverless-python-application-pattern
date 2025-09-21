# -*- coding: utf-8 -*-
import uuid
import os
import boto3
from botocore.exceptions import (
    ClientError,
)

from aws_lambda_powertools import Logger

__all__ = [
    "delete_sqs_messages",
    "get_sqs_queue_url",
    "UnprocessedMessagesError",
    "RecordsUnprocessedException",
    "send_message_to_queue",
    "send_messages_by_url",
    "send_message_batch_by_url",
    "send_message_by_queue_name",
    "receive_message",
]

LOGGER = Logger('layers.core.core_aws.sqs')


def get_sqs_client(session=None, region="us-east-1"):
    """Gets a client for AWS SQS

    Returns
    -------
        A low-level client representing Amazon Simple Queue Service (SQS)

    """
    if not session:
        return boto3.client("sqs", endpoint_url="https://sqs.{}.amazonaws.com".format(
            os.environ.get("AWS_DEFAULT_REGION", "us-east-1")))
    else:
        params = {
            'region_name': region,
            'aws_access_key_id': session['Credentials']['AccessKeyId'],
            'aws_secret_access_key': session['Credentials']['SecretAccessKey'],
            'aws_session_token': session['Credentials']['SessionToken']
        }

        return boto3.client("sqs", **params)


def send_message_to_queue(queue_name: str, data: str, session=None, delay=None, is_fifo=False, message_group_id="1"):
    """Send message to queue.

    Parameters
    ----------
    delay
    message_group_id
        Message of group Fifo
    is_fifo: Boolean
        If the sqs is Fifo use True
    queue_name : str
        The name of the queue to be returned
    data: str
        json body to send
    session
        AWS session to use to send the message
    Returns
    -------
    dict
        dict with the response
    """

    sqs_client = get_sqs_client(session)
    params = {
        "MessageBody": data,
        "QueueUrl": get_sqs_queue_url(queue_name, session)
    }

    if is_fifo:
        params.update({"MessageGroupId": message_group_id})

    if delay:
        params.update({"DelaySeconds": delay})

    response = sqs_client.send_message(**params)
    return response


def get_sqs_client_sts(sts):
    """
    Create a low-level service client by name.
    Args:
        sts: (Any) session to create new client

    Returns: (Any)
        Service client instance

    """
    return sts.client("sqs")


def get_sqs_client_sts(sts):
    """
    Create a low-level service client by name.
    Args:
        sts: (Any) session to create new client

    Returns: (Any)
        Service client instance

    """
    return sts.client("sqs")


def delete_sqs_messages(queue_name: str, receipt_handles: list) -> dict:
    """Deletes a list of messages from the specified queue.

    It splits the messages in batches of 10 since the batch version of the DeleteMessage API only deletes up to ten.

    Parameters
    ----------
    queue_name : str
        The name of the queue where the messages will be deleted.
    receipt_handles : list
        The list of receipt handles for the messages to be deleted.

    Returns
    -------
    dict
        The response from the DeleteMessage API with the results of every deleted message

    Raises
    ------
    ValueError
        If a queue with the provided name doesn't exist

    """
    results = {"Successful": [], "Failed": []}

    sqs_client = get_sqs_client()
    try:
        queue_url = sqs_client.get_queue_url(QueueName=queue_name)["QueueUrl"]
    except ClientError as error:
        if error.response["Error"]["Code"] == "AWS.SimpleQueueService.NonExistentQueue":
            raise ValueError(
                f"A queue with the name provided on the parameters doesn't exist: {queue_name}"
            )
        else:
            raise error

    for chunk in chunks(receipt_handles, 10):
        try:
            entries = [
                {"Id": str(uuid.uuid4()), "ReceiptHandle": receipt_handle}
                for receipt_handle in chunk
            ]
            batch_results = delete_sqs_message_batch(queue_url, entries)
            results.get("Successful").append(batch_results.get("Successful"))
            results.get("Failed").append(batch_results.get("Failed"))
        except ValueError as error:
            results.get("Failed").append(
                [{"Id": item.get("Id"), "Message": str(error)} for item in chunk]
            )
            continue
    return results


def delete_sqs_message_batch(queue_url: str, entries: list) -> dict:
    """Deletes a batch of messages from the specified queue.

    Parameters
    ----------
    queue_url : str
        The URL of the queue where the messages will be deleted.
    entries : list
        The list of receipt handles and identifiers for the messages to be deleted.

    Returns
    -------
    dict
        The response from the DeleteMessage API with the results of every deleted message

    Raises
    -------
    ValueError
        If the provided list of receipt handles is invalid, or one of the receipt handle ids is invalid.

    """
    sqs_client = get_sqs_client()

    try:
        results = sqs_client.delete_message_batch(QueueUrl=queue_url, Entries=entries)
    except ClientError as error:
        if error.response["Error"]["Code"].split(".")[-1] in [
            "BatchEntryIdsNotDistinct",
            "InvalidBatchEntryId",
        ]:
            raise ValueError(
                "One of the entries id provided in the batch is invalid."
            ) from error
        elif error.response["Error"]["Code"].split(".")[-1] in [
            "TooManyEntriesInBatchRequest",
            "EmptyBatchRequest",
        ]:
            raise ValueError(
                "The entries list provided as parameter is invalid."
            ) from error
        else:
            raise error
    else:
        return results


def get_sqs_queue_url(queue_name, session=None):
    """
    Get Queue URL to specific SQS resource
    Args: (str)
        queue_name: Queue name to get URL

    Returns: (str)
        Queue URL belong SQS

    Raises: (QueueDoesNotExist) Exception founded when URL is not exists

    """
    try:
        sqs_client = get_sqs_client(session)
        queue_url = sqs_client.get_queue_url(QueueName=queue_name)
        return queue_url["QueueUrl"]
    except ClientError as error:
        if error.response["Error"]["Code"] == "AWS.SimpleQueueService.NonExistentQueue":
            raise ValueError(
                f"A queue with the name provided on the parameters doesn't exist: {queue_name}, error founded: {error}"
            )
        else:
            raise error


def send_messages_by_url(
        data_to_send,
        queue_url,
        is_fifo=False,
        message_group_id="",
        message_deduplication_id="",
        message_attributes=None,
        delay_seconds=0,
        apply_sts=False,
        sts=None,
):
    """
    Send a messages to specific queue using its URL. THe message to send is only supported by JSON in this case, but
    the library support XML and Plain text. For more information check this documentation URL:

    Boto 3 documentation:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#SQS.Client.send_message
    Args:
        data_to_send: (Any) The message to will be sent.
        queue_url: (str) The URL of the Amazon SQS queue to witch a message is sent.
        is_fifo: (bool) Flag to show if the queue URL is FIFO or not
        message_group_id: (str) Tag to specify that the message belong to a specific message group. Only apply whether
        the queue is FIFO
        message_deduplication_id: (str) Token used for deduplication of sent messages, Only apply in FIFO queues
        message_attributes: (dict) Dict to contain an attribute to send in the message. Each message attribute consists
        of a Name, Type, and Value.
        delay_seconds: (int) The length of the time, in seconds, for witch to delay a specific message. Valid values: 0
        to 900. Maximum 15 minutes.
        apply_sts: (Any) If apply a service session to send message
        sts: (Any) Service session to send the message

    Returns: (dict)
        Data to describe the messages in sent
    Raises:
        ClientError: When an AWS exception is founded
        RuntimeError: If an unexpected error is founded

    """
    LOGGER.info(
        f"Data executed: Queue URL: -> {queue_url}, Data to send: {data_to_send}"
    )
    if message_attributes is None:
        message_attributes = {}
    try:
        if apply_sts:
            sqs_client = get_sqs_client_sts(sts)
        else:
            sqs_client = get_sqs_client()
        if is_fifo:
            response = sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=data_to_send,
                MessageAttributes=message_attributes,
                MessageGroupId=message_group_id,
                MessageDeduplicationId=message_deduplication_id,
                DelaySeconds=delay_seconds,
            )
        else:
            response = sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=data_to_send,
                MessageAttributes=message_attributes,
                DelaySeconds=delay_seconds,
            )

        LOGGER.info(response)
        return response
    except ClientError as err:
        LOGGER.exception("Failed to send sqs message")
        raise err
    except Exception as err:
        LOGGER.exception(
            "Unexpected error was find when try to send a messages from SQS"
        )
        raise err


def send_message_by_queue_name(
        data_to_send: dict,
        queue_name,
        is_fifo=False,
        message_group_id="",
        message_deduplication_id="",
        message_attributes=None,
        delay_seconds=0,
):
    """
    Send a message using a queue name instead an url. Using its name is possible to search its queue URL and send the
    message. For that, this method call the another methods: first call get_sqs_queue_url to get the queue URL and
    later send_messages_by_url to send the message to URL founded before.
    Args:
        data_to_send: (dict) The message to will be sent.
        queue_name: (str) The name of the Amazon SQS queue to witch a message is sent.
        is_fifo: (bool) Flag to show if the queue URL is FIFO or not
        message_group_id: (str) Tag to specify that the message belong to a specific message group. Only apply whether
        the queue is FIFO
        message_deduplication_id: (str) Token used for deduplication of sent messages, Only apply in FIFO queues
        message_attributes: (dict) Dict to contain an attribute to send in the message. Each message attribute consists
        of a Name, Type, and Value.
        delay_seconds: (int) The length of the time, in seconds, for witch to delay a specific message. Valid values: 0
        to 900. Maximum 15 minutes.

    Returns: (dict)
        Data to describe the messages in sent

    """
    LOGGER.info(
        f"Data executed: Queue Name: -> {queue_name}, Data to send: {data_to_send}"
    )
    queue_url = get_sqs_queue_url(queue_name)
    return send_messages_by_url(
        data_to_send,
        queue_url,
        is_fifo,
        message_group_id,
        message_deduplication_id,
        message_attributes,
        delay_seconds,
    )


def send_message_batch_by_url(queue_url: str, entries: list):
    """
    Delivers up to ten messages to the specified queue. This is a batch version of SendMessage. For a FIFO queue,
    multiple messages within a single batch are enqueued in the order they are sent. For more information check
    this URL:

    Boto 3 documentation:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#SQS.Client.send_message_batch

    Args:
        queue_url: (str) The URL of the Amazon SQS queue to which batched messages are sent.
        entries: (list) A list of SendMessageBatchRequestEntry items.

    Returns: (dict)
        List of the data status that is sent. The result of sending each message is reported individually in the
        response. Because the batch request can result in a combination of successful and unsuccessful actions,
        you should check for batch errors even when the call returns an HTTP status code of 200.

    Raises:
        ClientError: When an AWS exception is founded
        RuntimeError: If an unexpected error is founded
    """
    LOGGER.info(f"Data executed: Queue URL: -> {queue_url}, Entries to send: {entries}")
    try:
        sqs_client = get_sqs_client()
        response = sqs_client.send_message_batch(QueueUrl=queue_url, Entries=entries)
        LOGGER.info(response)
        return response
    except ClientError as err:
        LOGGER.exception("Failed to send message batch to sqs")
        raise err
    except Exception as err:
        LOGGER.exception("Unexpected error to try to send message batch")
        raise err


def receive_message(queue_url, max_number_messages, wait_time):
    """
    Retrieves one or more messages (up to 10), from the specified queue. For more information about this, check this
    URL:
    Boto 3 documentation:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#SQS.Client.receive_message
    Args:
        queue_url: (str) The URL of the Amazon SQS queue from which messages are received. Queue URLs and names
        are case-sensitive.
        max_number_messages: (int)  The maximum number of messages to return. Valid values: 1 to 10. Default: 1.
        wait_time: (int) The duration (in seconds) for which the call waits for a message to arrive in the queue before
        returning.

    Returns: (dict)
        Data about the messages to receive. For each message returned, the response includes the following:
            - The message body.
            - An MD5 digest of the message body. For information about MD5.
            - The MessageId you received when you sent the message to the queue.
            - The receipt handle.
            - The message attributes.
            - An MD5 digest of the message attributes.

    Raises:
        ClientError: When an AWS exception is founded
        RuntimeError: If an unexpected error is founded
    """
    LOGGER.info(
        f"Data executed: Queue URL: -> {queue_url}, Max number of messages to receive: {max_number_messages} "
        f"Wait time: -> {wait_time}"
    )
    try:
        sqs_client = get_sqs_client()
        response = sqs_client.receive_messages(
            QueueUrl=queue_url,
            AttributeNames=["ALL"],
            MaxNumberOfMessages=max_number_messages,
            WaitTimeSeconds=wait_time,
        )
        return response
    except ClientError as err:
        LOGGER.exception("Failed to receive messages to the current queue url")
        raise err
    except Exception as err:
        LOGGER.exception("Unexpected error was found when try to receive messages")
        raise err


class UnprocessedMessagesError(Exception):
    """Exception raised when messages couldn't be successfully processed"""

    pass


class RecordsUnprocessedException(Exception):
    def __init__(
            self,
            message=None,
    ):
        if message is None:
            message = "one or more records could not be processed"

        super(RecordsUnprocessedException, self).__init__(message)
