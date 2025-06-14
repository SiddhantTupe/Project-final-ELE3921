# Generated by Django 5.1.5 on 2025-06-01 09:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("medapp", "0011_remove_admissionrecord_added_by_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="admissionrecord",
            name="patient",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="admissions",
                to="medapp.patient",
            ),
        ),
    ]
