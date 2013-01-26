from django.contrib import admin
from django import forms
from django.core import urlresolvers

from accounts.models import Member, Student, Company, University

class AdminMemberForm(forms.Form):
    active = forms.BooleanField()

class MemberAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'is_active',
        'edit_link',
    )

    list_filter = (
        'userprofile__user__is_active',
    )

    actions = (
        'delete_selected',
        'activate_selected',
    )

    def delete_selected(self, request, queryset):
        """
        A custom delete action implementation.  It is needed to make sure that
        the delete method is called on all model instances since it has a
        custom implementation for the Member class.
        Otherwise, the default implementation calls delete on the QuerySet
        which does not yield desired behavior.
        """
        cnt = queryset.count()
        if cnt == 0:
            self.message_user(request, 'No items selected.')
            return
        message = 'member'
        if cnt > 1:
            message = 'members'
        for obj in queryset:
            obj.delete()
        self.message_user(request, 'Successfully deleted %d %s.' % (cnt,
                                                                    message))
    delete_selected.short_description = 'Delete selected members'

    def activate_selected(self, request, queryset):
        """
        A custom action which activates all the user account for all the
        selected Members.
        It enables bulk activation of accounts instead of forcing the admin to
        manually open & save all of them.
        """
        cnt = queryset.count()
        if cnt == 0:
            self.message_user(request, 'No items selected.')
            return
        message = 'member'
        if cnt > 1:
            message = 'members'
        for obj in queryset:
            obj.active = True
            obj.save()
        self.message_user(request, 'Successfully activated %d %s.' % (cnt,
                                                                      message))
    activate_selected.short_description = 'Activate selected member accounts.'

    def is_active(self, instance):
        """
        A method which returns a boolean indicating whether the Member's
        account is active or not.  Delegates to the active property.
        """
        return instance.active
    is_active.boolean = True

    def edit_link(self, instance):
        """
        A method which returns the link in the admin where the user can
        edit the Member.
        """
        URL_PATTERN = '<a href="%(url)s">Edit</a>'
        return URL_PATTERN % {
                'url' : instance.cast().get_admin_url()
        }
    edit_link.allow_tags = True

class MemberAdminForm(forms.ModelForm):
    active = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(MemberAdminForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        if instance is not None:
            self.fields['active'].initial = instance.active

    def save(self, force_insert=False, force_update=False, commit=True, *args, **kwargs):
        m = super(MemberAdminForm, self).save(commit=False, *args, **kwargs)
        m.active = self.cleaned_data['active']
        if commit:
            m.save()
        return m

class StudentAdminForm(MemberAdminForm):
    class Meta:
        model = Student

class CompanyAdminForm(MemberAdminForm):
    class Meta:
        model = Company

class UniversityAdminForm(MemberAdminForm):
    class Meta:
        model = University

class StudentAdmin(MemberAdmin):
    form = StudentAdminForm
class CompanyAdmin(MemberAdmin):
    form = CompanyAdminForm
class UniversityAdmin(MemberAdmin):
    form = UniversityAdminForm

admin.site.register(Member, MemberAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(University, UniversityAdmin)
