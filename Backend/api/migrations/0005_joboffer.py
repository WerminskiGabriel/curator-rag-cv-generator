from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_documents_file_alter_documents_processed_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobOffer',
            fields=[
                ('slug', models.CharField(max_length=255, primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(max_length=255)),
                ('body', models.TextField(blank=True, default='')),
                ('required_skills', models.JSONField(default=list)),
                ('scraped_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'job_offers',
            },
        ),
    ]
