# forms.py
from django import forms
from .models import Proffesor_Profile, Student_Profile, Documents, Courses

class ProffessorProfileForm(forms.ModelForm):
    class Meta:
        model = Proffesor_Profile
        fields = ['profile_image', 'course', 'branch', 'subject', 'address','phone_number']

 
class StudentProfileForm(forms.ModelForm):
    class Meta:
        model =Student_Profile
        fields = ['profile_image', 'course', 'branch', 'subjects', 'address','phone_number']


class DocumentForm(forms.ModelForm):
    course = forms.ModelChoiceField(queryset=Courses.objects.all(), label="Course", required=True)

    class Meta:
        model = Documents
        fields = ['name', 'document', 'course']
        labels = {
            'name': 'Document Name',
            'document': 'Upload Document',
        }

    def __init__(self, *args, **kwargs):
        # Optionally, you could restrict course selection to only those the professor teaches
        super().__init__(*args, **kwargs)
