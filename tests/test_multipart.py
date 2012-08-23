import sys, os
sys.path.insert(0, os.path.abspath('..'))

import unittest
from pymultipart import MultipartParser


class MultipartParserTestSuite(unittest.TestCase):

    def test_parsing(self):
        boundary = '----WebKitFormBoundaryeqOqmwCCwUpAZEDi'
        filename = os.getcwd() + '/tests/data-multipart-wireshark.txt'

        with open(filename, 'rb') as data:
            parser = MultipartParser(boundary, data)

        self.assertIsNotNone(parser.params)

        hidden1 = parser.params.get('hidden1')
        password = parser.params.get('password')
        value1 = parser.params.get('value1')
        value2 = parser.params.get('value2')
        value3 = parser.params.get('value3')

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

        self.assertIsNotNone(parser.files)

        image1 = parser.files.get('image1')
        image2 = parser.files.get('image2')

        self.assertIsNotNone(image1)
        self.assertIsNotNone(image2)

        image1 = image1[0]
        image2 = image2[0]

        self.assertEqual(image1.get('content-type'), 'image/jpeg')
        self.assertEqual(image1.get('filesize'), 161736)
        self.assertEqual(image1.get('filename'), 'IMG_0051.JPG')

        self.assertEqual(image2.get('content-type'), 'image/jpeg')
        self.assertEqual(image2.get('filesize'), 161736)
        self.assertEqual(image2.get('filename'), 'IMG_0051.JPG')

        # write the file?
        # with open('test.jpg', 'w+b') as f:
        #     f.write(machine.files['image1'][0]['data'].read())
