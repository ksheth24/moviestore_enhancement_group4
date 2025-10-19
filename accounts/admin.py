from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'headline')
	search_fields = ('user__username', 'headline', 'skills')
from .models import Skill, Link, Experience, Education


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
	list_display = ('profile', 'name')


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
	list_display = ('profile', 'label', 'url')


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
	list_display = ('profile', 'title', 'company', 'start_date', 'end_date')


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
	list_display = ('profile', 'school', 'degree', 'start_date', 'end_date')

# Register your models here.
