# Generated by Django 4.1.1 on 2022-09-25 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Properties',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('category', models.CharField(max_length=200)),
                ('address', models.CharField(max_length=500)),
                ('price', models.CharField(max_length=20)),
                ('images', models.ImageField(upload_to='uploads/images')),
            ],
        ),
    ]
