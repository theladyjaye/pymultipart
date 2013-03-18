import sys, os

sys.path.insert(0, os.path.abspath('..'))

import unittest
from pymultipart import MultipartParser


class MultipartParserTestSuite(unittest.TestCase):

    def test_parsing2(self):

        boundary = '===============0950808015=='
        filename = os.getcwd() + '/tests/data-circuits.txt'

        with open(filename, 'rb') as data:
            params = {}
            files = {}
            MultipartParser.from_boundary(boundary, data, params, files)

        self.assertIsNotNone(params)
        self.assertEqual(params['description'][0], 'Hello World!')

        file1 = files.get('file')
        self.assertIsNotNone(file1)

        file1 = file1[0]

        self.assertEqual(file1.get('content-type'), 'text/plain')
        self.assertEqual(file1.get('filesize'), 12)
        self.assertEqual(file1.get('filename'), 'helloworld.txt')

    def test_parsing1(self):
        boundary = '----WebKitFormBoundaryeqOqmwCCwUpAZEDi'
        filename = os.getcwd() + '/tests/data-multipart-wireshark.txt'

        with open(filename, 'rb') as data:
            params = {}
            files = {}
            MultipartParser.from_boundary(boundary, data, params, files)

        self.assertIsNotNone(params)

        hidden1 = params.get('hidden1')
        password = params.get('password')
        value1 = params.get('value1')
        value2 = params.get('value2')
        value3 = params.get('value3')

        self.assertIsNotNone(hidden1)
        self.assertIsNotNone(password)
        self.assertIsNotNone(value1)
        self.assertIsNotNone(value2)
        self.assertIsNotNone(value3)

        self.assertEqual(hidden1[0], 'secret!')
        self.assertEqual(password[0], '12345')
        self.assertEqual(value3[0], 'Bird')
        self.assertEqual(value2[0], 'Ollie')
        self.assertEqual(value1[0], 'Lucy')

        self.assertIsNotNone(files)

        image1 = files.get('image1')
        image2 = files.get('image2')

        self.assertIsNotNone(image1)
        self.assertIsNotNone(image2)

        image1 = image1[0]
        image2 = image2[0]

        self.assertEqual(image1.get('content-type'), 'image/jpeg')
        self.assertEqual(image1.get('filesize'), 161734)
        self.assertEqual(image1.get('filename'), 'IMG_0051.JPG')

        self.assertEqual(image2.get('content-type'), 'image/jpeg')
        self.assertEqual(image2.get('filesize'), 161734)
        self.assertEqual(image2.get('filename'), 'IMG_0051.JPG')

        #write the file?
        # print(image1.get('filesize'))
        # with open('test.jpg', 'w+b') as f:
        #     f.write(files['image1'][0]['data'].read())
