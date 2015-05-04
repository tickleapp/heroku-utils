import os


def sns_publish(event, subject, message):
    sns_topic = os.environ.get('SNS_DEV_ADMIN_TOPIC', None)
    if sns_topic:
        import boto.sns
        sns_connection = boto.sns.connect_to_region('us-west-2')
        sns_connection.publish(topic=sns_topic, subject='[Tickle][{}] {}'.format(event, subject), message=message)
