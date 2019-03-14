# Generated by Django 2.1.7 on 2019-03-14 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0007_auto_20190314_2010'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allsort',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='object',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterUniqueTogether(
            name='sortobject',
            unique_together={('sort', 'object')},
        ),
        migrations.AlterUniqueTogether(
            name='takenrecord',
            unique_together={('user1', 'user2', 'object')},
        ),
        migrations.AlterUniqueTogether(
            name='userobject',
            unique_together={('object', 'user')},
        ),
    ]
