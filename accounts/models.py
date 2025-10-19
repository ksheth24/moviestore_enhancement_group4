from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.utils import OperationalError, ProgrammingError


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	headline = models.CharField(max_length=255, blank=True)
	resume = models.FileField(upload_to='resumes/', blank=True, null=True)

	def __str__(self):
		return f"Profile: {self.user.username}"


class Skill(models.Model):
	profile = models.ForeignKey(Profile, related_name='skills', on_delete=models.CASCADE)
	name = models.CharField(max_length=100)

	def __str__(self):
		return self.name


class Link(models.Model):
	profile = models.ForeignKey(Profile, related_name='links', on_delete=models.CASCADE)
	url = models.URLField()
	label = models.CharField(max_length=255, blank=True)

	def __str__(self):
		return self.label or self.url


class Experience(models.Model):
	profile = models.ForeignKey(Profile, related_name='experiences', on_delete=models.CASCADE)
	title = models.CharField(max_length=255)
	company = models.CharField(max_length=255, blank=True)
	start_date = models.DateField(blank=True, null=True)
	end_date = models.DateField(blank=True, null=True)
	description = models.TextField(blank=True)

	def __str__(self):
		return f"{self.title} at {self.company}" if self.company else self.title


class Education(models.Model):
	profile = models.ForeignKey(Profile, related_name='educations', on_delete=models.CASCADE)
	school = models.CharField(max_length=255)
	degree = models.CharField(max_length=255, blank=True)
	start_date = models.DateField(blank=True, null=True)
	end_date = models.DateField(blank=True, null=True)
	description = models.TextField(blank=True)

	def __str__(self):
		return f"{self.degree} at {self.school}" if self.degree else self.school


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		try:
			Profile.objects.create(user=instance)
		except (OperationalError, ProgrammingError):
			# The Profile table may not exist yet (migrations haven't been run).
			# Skip creating the profile for now — running migrations will allow
			# profiles to be created later or can be created manually.
			pass
