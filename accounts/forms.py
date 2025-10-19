from django.contrib.auth.forms import UserCreationForm
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
from django import forms
from .models import Profile
from .models import Skill, Link, Experience, Education
from django.forms import inlineformset_factory

class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([
            f'<div class="alert alert-danger" role="alert">{e}</div>' for e in self]))

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'password1',
        'password2']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update(
                {'class': 'form-control'}
            )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['headline']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.update({'class': 'form-control'})


# New structured forms
class ResumeForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['resume']


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name']


class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ['url', 'label']


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['title', 'company', 'start_date', 'end_date', 'description']


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['school', 'degree', 'start_date', 'end_date', 'description']


SkillFormSet = inlineformset_factory(Profile, Skill, form=SkillForm, extra=1, can_delete=True)
LinkFormSet = inlineformset_factory(Profile, Link, form=LinkForm, extra=1, can_delete=True)
ExperienceFormSet = inlineformset_factory(Profile, Experience, form=ExperienceForm, extra=1, can_delete=True)
EducationFormSet = inlineformset_factory(Profile, Education, form=EducationForm, extra=1, can_delete=True)