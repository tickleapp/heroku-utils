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
from flask import request
import hashlib
import hmac


class Github(object):

    @staticmethod
    def verify_webhook_signature(secret):
        if not secret:
            raise ValueError('Cannot get shared secret')

        signature = request.headers.get('X-Hub-Signature')
        if not signature:
            raise ValueError('Cannot get X-Hub-Signature from header')

        sha_name, signature = signature.split('=')
        if sha_name != 'sha1':
            raise ValueError('Unsupported hash function')

        if not hmac.compare_digest(signature,
                                   hmac.new(secret.encode('utf-8'),
                                            msg=request.data,
                                            digestmod=hashlib.sha1).hexdigest()):
            raise ValueError('Invalid signature')
