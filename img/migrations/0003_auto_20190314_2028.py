# Generated by Django 2.1.7 on 2019-03-14 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('img', '0002_auto_20190314_2010'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('picture', models.ImageField(upload_to='test_pictures')),
            ],
            options={
                'db_table': 'profile',
            },
        ),
        migrations.DeleteModel(
            name='img',
        ),
    ]
