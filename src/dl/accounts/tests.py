"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from accounts.models import Student, Company, University, Member

class MemberTest(TestCase):
    def setUp(self):
        self.student_data = {
                'name': u'Name',
                'surname': u'Surname',
                'email': u'name@domain.com',
                'country': u'Country',
                'city': u'City',
                'eestec_member': True,
                'username': u'username',
                'password': u'password',
        }
    def test_username_property(self):
        """
        Tests the behavior of the username property: it needs to
        properly change the user's username and return the new value.
        """
        s = Student(**self.student_data)
        s.save()
        
        m = Member.objects.get(pk=s.pk)
        self.assertEqual(m.username, s.username)

        new_username = 'new_username'
        m.username = 'new_username'
        m.save()
        self.assertEqual(m.username, new_username)

        del m
        m = Member.objects.get(pk=s.pk)
        self.assertEqual(m.username, new_username)

        s = Student.objects.get(pk=m.pk)
        self.assertEqual(m.username, s.userprofile.user.username)

    def test_active_property(self):
        s = Student(**self.student_data)
        s.save()

        m = Member.objects.get(pk=s.pk)
        # Check default
        self.assertFalse(m.active)
        
        m.active = True
        m.save()
        self.assertTrue(m.active)

        del m
        m = Member.objects.get(pk=s.pk)
        self.assertTrue(m.active)

        s = Student.objects.get(pk=m.pk)
        self.assertTrue(s.userprofile.user.is_active)



class StudentTest(TestCase):
    def setUp(self):
        self.student_data = {
                'name': u'Name',
                'surname': u'Surname',
                'email': u'name@domain.com',
                'country': u'Country',
                'city': u'City',
                'eestec_member': True,
                'username': u'username',
                'password': u'password',
        }
    def test_student_save_group(self):
        """
        Tests whether the save method for the Student class properly
        initializes the user's group to Students.
        """
        s = Student(**self.student_data)
        s.save()
        # Just one default group
        self.assertEqual(
                s.userprofile.user.groups.all().count(),
                1,
                "Student not associated with one and only one group.")
        self.assertEqual(
                s.userprofile.user.groups.all()[0].name,
                u'Students',
                "Student not associated with 'Students' group.")
    def test_student_save_userprofile(self):
        """
        Tests whether the save method for the Student class properly
        saves the user profile along with the Student object.
        """
        s = Student(**self.student_data)
        s.save()
        self.assertEquals(
                s.userprofile.user.username,
                self.student_data['username'])

class CompanyTest(TestCase):
    def setUp(self):
        self.company_data = {
                'name': u'Name',
                'email': u'name@domain.com',
                'country': u'Country',
                'city': u'City',
                'address': u'Address',
                'username': u'username',
                'password': u'password',
        }
    def test_company_save_group(self):
        """
        Tests whether the save method for the Company class properly
        initializes the user's group to Companies.
        """
        c = Company(**self.company_data)
        c.save()
        # Just one default group
        self.assertEqual(
                c.userprofile.user.groups.all().count(),
                1,
                "Company not associated with one and only one group.")
        self.assertEqual(
                c.userprofile.user.groups.all()[0].name,
                u'Companies',
                "Company not associated with 'Companies' group.")
    def test_company_save_userprofile(self):
        """
        Tests whether the save method for the Company class properly
        saves the user profile along with the Company object.
        """
        c = Company(**self.company_data)
        c.save()
        self.assertEquals(
                c.userprofile.user.username,
                self.company_data['username'])
    def test_company_username_property(self):
        """
        Tests whether the parent class' username property works from
        the Company class.
        """
        c = Company(**self.company_data)
        c.save()
        self.assertEquals(
                c.username,
                self.company_data['username'])

        new_username = 'new_username'
        c.username = new_username
        c.save()
        self.assertEquals(
                c.username,
                new_username)

        pk = c.pk
        del c
        c = Company.objects.get(pk=pk)
        self.assertEquals(c.username, new_username)

    def test_company_from_member_cast(self):
        """
        Tests whether the cast method of the Member class returns the
        Company object properly.
        """
        c = Company(**self.company_data)
        c.save()
        pk = c.pk
        del c

        m = Member.objects.get(pk=pk)
        self.assertIsInstance(m.cast(), Company)


class UniversityTest(TestCase):
    def setUp(self):
        self.university_data = {
                'name_of_university': u'Name',
                'name_of_faculty': u'Faculty',
                'email': u'name@domain.com',
                'country': u'Country',
                'city': u'City',
                'address': u'Address',
                'username': u'username',
                'password': u'password',
        }
    def test_university_save_group(self):
        """
        Tests whether the save method for the University class properly
        initializes the user's group to Universities.
        """
        u = University(**self.university_data)
        u.save()
        # Just one default group
        self.assertEqual(
                u.userprofile.user.groups.all().count(),
                1,
                "University not associated with one and only one group.")
        self.assertEqual(
                u.userprofile.user.groups.all()[0].name,
                u'Universities',
                "University not associated with 'Universities' group.")
    def test_university_save_userprofile(self):
        """
        Tests whether the save method for the University class properly
        saves the user profile along with the University object.
        """
        u = University(**self.university_data)
        u.save()
        self.assertEquals(
                u.userprofile.user.username,
                self.university_data['username'])
