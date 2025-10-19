from django.shortcuts import render
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from .forms import CustomUserCreationForm, CustomErrorList
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile
from .forms import ProfileForm, SkillFormSet, LinkFormSet, ExperienceFormSet, EducationFormSet, ResumeForm
from django.shortcuts import get_object_or_404

@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')

def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'accounts/login.html',
            {'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(
            request,
            username = request.POST['username'],
            password = request.POST['password']
        )
        if user is None:
            template_data['error'] ='The username or password is incorrect.'
            return render(request, 'accounts/login.html',
                {'template_data': template_data})
        else:
            auth_login(request, user)
            return redirect('home.index')
        
def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'
    if request.method == 'GET':
        template_data['form'] = CustomUserCreationForm()
        return render(request, 'accounts/signup.html',
            {'template_data': template_data})
    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            user = form.save()
            # auto-login optional, but redirect to profile edit to encourage completion
            return redirect('accounts.profile_edit')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html',
                {'template_data': template_data})

@login_required
def orders(request):
    template_data = {}
    template_data['title'] = 'Orders'
    template_data['orders'] = request.user.order_set.all()
    return render(request, 'accounts/orders.html',
        {'template_data': template_data})


@login_required
def profile_edit(request):
    template_data = {'title': 'Edit Profile'}
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile(user=request.user)
    if request.method == 'GET':
        template_data['form'] = ProfileForm(instance=profile)
        template_data['resume_form'] = ResumeForm(instance=profile)
        template_data['skill_formset'] = SkillFormSet(instance=profile)
        template_data['link_formset'] = LinkFormSet(instance=profile)
        template_data['exp_formset'] = ExperienceFormSet(instance=profile)
        template_data['edu_formset'] = EducationFormSet(instance=profile)
        return render(request, 'accounts/profile_form.html', {'template_data': template_data})
    else:
        form = ProfileForm(request.POST, instance=profile)
        resume_form = ResumeForm(request.POST, request.FILES, instance=profile)
        skill_formset = SkillFormSet(request.POST, instance=profile)
        link_formset = LinkFormSet(request.POST, instance=profile)
        exp_formset = ExperienceFormSet(request.POST, instance=profile)
        edu_formset = EducationFormSet(request.POST, instance=profile)
        if (form.is_valid() and resume_form.is_valid() and skill_formset.is_valid()
                and link_formset.is_valid() and exp_formset.is_valid() and edu_formset.is_valid()):
            form.instance.user = request.user
            form.save()
            resume_form.save()
            skill_formset.save()
            link_formset.save()
            exp_formset.save()
            edu_formset.save()
            return redirect('accounts.profile_detail', username=request.user.username)
        else:
            template_data['form'] = form
            template_data['resume_form'] = resume_form
            template_data['skill_formset'] = skill_formset
            template_data['link_formset'] = link_formset
            template_data['exp_formset'] = exp_formset
            template_data['edu_formset'] = edu_formset
            return render(request, 'accounts/profile_form.html', {'template_data': template_data})


def profile_detail(request, username):
    user = get_object_or_404(User, username=username)
    profile = getattr(user, 'profile', None)
    template_data = {'title': f"{user.username}'s Profile", 'profile_user': user, 'profile': profile}
    return render(request, 'accounts/profile_detail.html', {'template_data': template_data})
