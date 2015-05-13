#
# Copyright 2015 Tickle Labs, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# import json
import logging
import os
import sys
from flask import Flask, request
from sns import sns_publish


source_root = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.ERROR)
logger.addHandler(stdout_handler)


@app.route('/')
def index():
    return '''<h1>Tickle SCM admin tool</h1><br><a href="https://tickleapp.com/">Tickle Labs, Inc.</a>'''


@app.route('/scm/push-webhook/pusher_check/', methods=['POST'])
def push_webhook_pusher_check():
    # Parse event data
    try:
        push_event_data = json.loads(request.data.decode('utf-8'))
    except ValueError:
        return 'Failed to parse push event', 400

    # Github's hook check
    if 'hook' in push_event_data and 'hook_id' in push_event_data:
        return 'OK', 200

    # Valid pushers info
    with open(os.path.join(source_root, 'pusher_matches.json'), 'r') as f:
        pusher_matches = json.load(f)

    # get SNS topic
    sns_topic = os.environ.get('SNS_SCM_ADMIN_TOPIC', None)

    # Pusher info
    pusher = push_event_data.get('pusher', None)
    if pusher:
        pusher = pusher.get('name', None)
    repository = push_event_data.get('repository', None)
    if repository:
        repository_name = repository.get('full_name', None)
    else:
        repository_name = None
    branch = push_event_data.get('ref', '').split('/')[-1]
    if not pusher or not repository_name or not branch:
        logger.error('Cannot parse push event data')
        logger.error(request.data)
        sns_publish(sns_topic=sns_topic,
                    event='SCM',
                    subject='Failed to parse oush event data',
                    message='received data is:\n\n{}'.format(request.data.decode('utf-8')))
        return 'Bad Request, Unknown push event payload', 400

    # Match
    repo_to_be_matched = pusher_matches.get(repository_name, None)
    if repo_to_be_matched:
        if branch in repo_to_be_matched:
            branch_to_be_matched = repo_to_be_matched[branch]
            if pusher in branch_to_be_matched:
                return 'OK', 200
            else:
                sns_publish(sns_topic=sns_topic,
                            event='SCM',
                            subject='Invalid push event @ {branch} of {repo}'.format(repo=repository_name,
                                                                                     branch=branch),
                            message='Pusher "{pusher}" pushed to `{branch}` branch at `{repo}` repo'.format(
                                pusher=pusher,
                                branch=branch,
                                repo=repository_name,
                            ))
                return 'Forbidden', 403

    # Don't have to match
    return 'OK', 200


if __name__ == "__main__":
    app.run(debug=True)
