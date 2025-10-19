# Generated manually to add amount_left field
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0002_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='amount_left',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
