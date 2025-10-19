from django.contrib import admin
from django import forms
from .models import Movie, Review


class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['name', 'price', 'description', 'image', 'amount_left']

    def clean_amount_left(self):
        new = self.cleaned_data.get('amount_left')
        # If editing an existing instance, fetch previous value
        if self.instance and self.instance.pk:
            try:
                old = Movie.objects.get(pk=self.instance.pk)
            except Movie.DoesNotExist:
                old = None
            # If previously out of stock (0) do not allow changing to any other value
            if old and old.amount_left == 0 and new != 0:
                raise forms.ValidationError(
                    'Cannot change stock from 0 to another value. Contact support or adjust workflow.'
                )
        # Disallow negative amounts
        if new is not None and new < 0:
            raise forms.ValidationError('amount_left cannot be negative.')
        return new


class MovieAdmin(admin.ModelAdmin):
    form = MovieForm
    ordering = ['name']
    search_fields = ['name']
    list_display = ['name', 'price', 'amount_left']
    fields = ['name', 'price', 'description', 'image', 'amount_left']


admin.site.register(Movie, MovieAdmin)
admin.site.register(Review)