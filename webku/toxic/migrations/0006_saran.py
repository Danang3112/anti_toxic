# Generated by Django 4.0.5 on 2022-08-04 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toxic', '0005_kasar'),
    ]

    operations = [
        migrations.CreateModel(
            name='saran',
            fields=[
                ('id_saran', models.BigAutoField(primary_key=True, serialize=False)),
                ('saran_kata', models.CharField(max_length=20)),
                ('label', models.CharField(max_length=10)),
            ],
        ),
    ]
