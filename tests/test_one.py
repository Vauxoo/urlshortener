#!/usr/bin/env python
# -*- coding: utf-8 -*-

import main
import os
import unittest
from click.testing import CliRunner


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.app = main.app.test_client()
        main.table_check()
        pass

    def tearDown(self):
        os.remove(main.db_path)
        pass

    def test_000_get_next_id(self):
        '''If next number is being done properly'''
        self.assertTrue(main.get_base_next('Z')[0],
                        'The last item should return the next first')
        self.assertFalse(main.get_base_next('z')[0],
                         'The last item should return the next first')
        self.assertFalse(main.get_base_next('0')[0],
                         'The last item should return the next first')
        self.assertTrue(main.next_id('abxHtw') == 'abxHtx',
                        'The nest Item should be "abxHtx"')

    def test_001_db(self):
        self.assertTrue(os.path.isfile(main.db_path),
                        'Database is not being created properly')

    def test_002_home(self):
        '''Home is being rendered properly'''
        rv = self.app.get('/')
        self.assertIn(b'Enter URL to shorten', rv.data,
                      'Home page not retrieved')

    def test_002_shortened(self):
        '''Shorting properly a test url'''
        rv = self.app.post('/', data=dict(
                url='http://google.com',
             ), follow_redirects=True)
        self.assertIn(b'localhost:5000/0', rv.data,
                      'Link Was not shortened')

    def test_003_retrieving(self):
        '''Generating 3 url to check consistency between generated and domains
        genenrated'''
        self.app.post('/', data=dict(
                url='http://google.com',
             ), follow_redirects=True)
        self.app.post('/', data=dict(
                url='http://vauxoo.com',
             ), follow_redirects=True)
        self.app.post('/', data=dict(
                url='http://example.com',
             ), follow_redirects=True)
        rv = self.app.get('/0')
        self.assertIn(b'http://google.com', rv.data,
                      'I did not retrieve properly the right url')
        rv = self.app.get('/1')
        self.assertIn(b'http://vauxoo.com', rv.data,
                      'I did not retrieve properly the right url')
        rv = self.app.get('/2')
        self.assertIn(b'http://example.com', rv.data,
                      'I did not retrieve properly the right url')

    def test_004_cli(self):
        '''Command line'''
        runner = CliRunner()
        result = runner.invoke(main.main, ['--version'])
        assert result.exit_code == 1
        self.assertIn('Your Version is', result.output,
                      'Version is not being printed as expected')


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
