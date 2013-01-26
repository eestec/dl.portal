"""
Unit tests for the distance_learning application.
"""

from django.test import TestCase
import unittest
import doctest

from distance_learning import utils
from distance_learning.models import Video, VideoType, VideoSubject
from distance_learning.utils import CommaDelimitedTextField
from distance_learning.utils import PrettyPrintList

def suite():
    """
    Defines a custom TestSuite so that the doctests can be tested along
    with TestCases when ./manage.py test is called for this app.
    """
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(utils))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(
        CommaDelimitedTextFieldTest))
    return suite

class CommaDelimitedTextFieldTest(TestCase):
    def setUp(self):
        self.field = CommaDelimitedTextField()

    def test_list_to_field(self):
        self.assertEqual(
                self.field.get_db_prep_value(PrettyPrintList([u'first', u'second', u'3'])),
                u'first,second,3')
    def test_field_to_list(self):
        self.assertEqual(
                self.field.to_python(u'first,   second,3,    4'),
                PrettyPrintList([u'first', u'second', u'3', u'4']))
    def test_sane_inverse(self):
        """
        Tests whether converting a list to a string and then back gives
        the same list.
        """
        l = PrettyPrintList([u'first', u'second', u'3'])
        self.assertEqual(
                self.field.to_python(self.field.get_db_prep_value(l)),
                l)

class VideoTest(TestCase):
    def setUp(self):
        # The fixture makes sure the type and subject exist
        video_type = VideoType.objects.get(pk=1)
        video_subject = VideoSubject.objects.get(pk=1)
        # TODO: Add a test fixture with a user
        user = None
        self.data = {
                'name': 'Name',
                'city': 'City',
                'country': 'Country',
                'event': 'Event',
                'description': 'Description',
                'video_url': 'http://www.youtube.com/watch?v=tfTWHbtv_-Y',
                'lecturer': 'Lecturer',
                'handout': '/home/dummy/dummy.pdf',
                'presentation': '/home/dummy/dummy.ppt',
                'video_type': video_type,
                'keywords': 'key1, word2, stuff',
                'subject': video_subject,
                'user': user,
        }
    def test_admin_notification(self):
        pass

