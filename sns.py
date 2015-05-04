
def sns_publish(sns_topic, event, subject, message):
    if not sns_topic:
        return

    import boto.sns
    sns_connection = boto.sns.connect_to_region('us-west-2')
    sns_connection.publish(topic=sns_topic, subject='[Tickle][{}] {}'.format(event, subject), message=message)
