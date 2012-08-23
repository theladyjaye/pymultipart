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


import collections
from tempfile import TemporaryFile


class MultipartException(Exception):

    def __init__(self, message):
        self.message = message


class MultipartParser(object):

    def __init__(self, boundary, data):
        self.files = {}
        self.params = {}
        self.current_headers = {}
        self.master_boundary = "--" + boundary
        self.master_boundary_length = len(boundary) + 2
        self.start_processing(data)

    def start_processing(self, data):
        self.validate_master_boundary(data)

    def end_processing(self):
        pass

    def validate_master_boundary(self, data):
        candidate = self._readboundary(data)
        if candidate == self.master_boundary:
            if data.read(2) == b'--':
                self.end_processing()
            else:
                self.current_headers = {}
                self.read_header(data)
        else:
            raise MultipartException("Invalid Boundary")

    def read_boundry(self, data):
        self._readboundary(data)

        if data.read(2) == b'--':
            self.end_processing()
        else:
            self.current_headers = {}
            self.read_header(data)

    def start_body(self, data):
        disposition = self.current_headers.get("content-disposition")
        if disposition and "filename" in disposition:
            self.read_file(data)
        else:
            self.read_body(data)

    def read_header(self, data):
        line = data.readline().decode()
        if line and line != '\r\n':
            line = line.split(":")
            key = line[0].lower().strip()
            value = line[1].strip()

            self.current_headers[key] = None

            if key == "content-disposition":
                self.current_headers[key] = {}
                parts = collections.deque(value.split(";"))
                disposition_type = parts.popleft()

                if disposition_type != "form-data":
                    # RFC 2388 requires the disposition type be "form-data"
                    # anything else is a no op and we should skip this segment/part
                    # http://tools.ietf.org/html/rfc2388
                    raise MultipartException("Invalid Content-Disposition, found {0} expected form-data".format(disposition_type))

                while 1:
                    try:
                        value = parts.popleft().strip().replace("\"", "")
                        k, v = value.split("=")
                        self.current_headers[key][k] = v
                    except IndexError:
                        break
            else:
                self.current_headers[key] = value

            self.read_header(data)
        else:
            self.start_body(data)

    def read_file(self, data):
        with TemporaryFile() as temp_file:
            #temp_file = TemporaryFile()
            if "content-length" in self.current_headers:
                clen = int(self.current_headers["content-length"])
                temp_file.write(data.read(clen))
            else:
                bytes = data.readline()
                while 1:
                    try:
                        if bytes[:2].decode() == '--':
                            break
                    except UnicodeDecodeError:
                        pass
                    temp_file.write(bytes)
                    bytes = data.readline()

            filesize = temp_file.tell()
            if filesize == 0:
                self.read_boundry(data)
                return
            key = self.current_headers["content-disposition"]["name"]
            filename = self.current_headers["content-disposition"].get("filename", "")
            content_type = self.current_headers["content-type"]

            if key not in self.files:
                self.files[key] = []

            temp_file.seek(0)
            self.files[key].append({"filename": filename,
                                    "filesize": filesize,
                                    "content-type": content_type,
                                    "data": temp_file})
        self.read_header(data)

    def read_body(self, data):
        value = ""
        bytes = data.readline().decode()

        while not bytes[-2:] == "\r\n":
            value = value + bytes
            bytes = data.readline().decode()

        value = value + bytes.rstrip()

        key = self.current_headers["content-disposition"]["name"]

        if key not in self.params:
            self.params[key] = []

        self.params[key].append(value)
        self.read_boundry(data)

    def _readboundary(self, data):
        boundary = data.read(self.master_boundary_length).decode()
        return boundary
