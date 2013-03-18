# HTTP Multipart Body Parser
#
# Copyright 2012 Adam Venturella
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from collections import deque
import string
from tempfile import TemporaryFile


class ParserControl(object):
    START_TEXT = '\x02'
    START_FILE = '\x1C'
    FINALIZE = '\x10'


def coroutine(func):
    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        next(cr)
        return cr
    return start


@coroutine
def multipart_headers():

    results = {}

    while True:

        line = yield

        if line == ParserControl.FINALIZE:
            yield results
            results = {}
            continue

        parts = line.split(':', 1)

        if len(parts) != 2:
            continue

        key = parts[0].strip().lower()
        header = results.setdefault(key, {})
        options = deque(map(string.strip, parts[1].split(';')))
        header['type'] = options.popleft()
        header['params'] = {}

        while options:
            option = options.popleft().replace('\"', '')
            try:
                option_k, option_v = option.split('=')
            except ValueError:
                continue

            header['params'][option_k] = option_v


@coroutine
def multipart_body():
    result = None
    action = None
    context = None

    while True:
        data = yield

        if data == ParserControl.FINALIZE:
            if context == ParserControl.START_TEXT:
                body = ''.join(result)
            elif context == ParserControl.START_FILE:

                filesize = result.tell() - 2
                result.seek(0)
                result.truncate(filesize)

                body = {'filename': None,
                        'content-type': None,
                        'filesize': filesize,
                        'data': result}

            result = None
            action = None
            yield body
            continue

        elif data == ParserControl.START_TEXT:
            result = []
            action = result.append
            context = data
            continue

        elif data == ParserControl.START_FILE:
            result = TemporaryFile()
            action = result.write
            context = data
            continue

        if context == ParserControl.START_TEXT:
            if data[-2:] == '\r\n':
                data = data[:-2]

        action(data)


@coroutine
def multipart_stream(boundary, header_parser, body_parser, params, files):
    data = None
    headers = None
    boundry_len = len(boundary)

    while True:
        line = yield

        if line == '\r\n':
            headers = data.send(ParserControl.FINALIZE)
            meta = headers['content-disposition']['params']
            data.send(None)
            data = body_parser
            data.send(ParserControl.START_TEXT if 'filename' not in meta
                                               else ParserControl.START_FILE)
            continue

        elif line[:boundry_len] == boundary:
            if headers:
                meta = headers['content-disposition']['params']
                body = data.send(ParserControl.FINALIZE)
                data.send(None)

                if 'filename' in meta:
                    target = files.setdefault(meta['name'], [])
                    body['filename'] = meta['filename']
                    body['content-type'] = headers['content-type']['type']
                    target.append(body)
                else:
                    target = params.setdefault(meta['name'], [])
                    target.append(body)

            data = header_parser
            headers = {}
            continue

        data.send(line)


class MultipartParser(object):

    @staticmethod
    def from_boundary(multipart_boundary, data, params, files):
        boundary = '--' + multipart_boundary

        protocol = multipart_stream(
            boundary,
            multipart_headers(),
            multipart_body(),
            params,
            files)

        for line in iter(data.readline, ''):
            protocol.send(line)
