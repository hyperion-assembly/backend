# Generated by Django 4.2.7 on 2023-12-16 11:15

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Contributor",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("email", models.EmailField(blank=True, max_length=255, verbose_name="Email")),
                ("github_username", models.CharField(blank=True, max_length=255, verbose_name="Github Username")),
                ("github_id", models.CharField(blank=True, max_length=255, verbose_name="Github Username")),
                (
                    "onchain_address",
                    models.CharField(
                        blank=True,
                        help_text="EVM compatible onchain address in hexadecimal format, e.g., 0xc93e3....8a5d",
                        max_length=42,
                        verbose_name="Onchain Address",
                    ),
                ),
            ],
            options={
                "verbose_name": "Contributor",
                "verbose_name_plural": "Contributors",
                "db_table": "contributor",
            },
        ),
        migrations.CreateModel(
            name="Project",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255, verbose_name="Name of Project")),
                ("source_url", models.CharField(blank=True, max_length=255, verbose_name="Source URL")),
                ("description", models.CharField(blank=True, max_length=255, verbose_name="Description")),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="projects",
                        to="data_model.contributor",
                    ),
                ),
            ],
            options={
                "verbose_name": "Project",
                "verbose_name_plural": "Projects",
                "db_table": "project",
            },
        ),
        migrations.CreateModel(
            name="WorkPlace",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255, verbose_name="Name of Work Place")),
                ("github_repo_id", models.CharField(blank=True, max_length=255, verbose_name="Github Repo ID")),
                ("is_active", models.BooleanField(default=True, verbose_name="is_active")),
                (
                    "work_place_type",
                    models.CharField(
                        blank=True,
                        choices=[("github", "GitHub")],
                        default="github",
                        max_length=16,
                        verbose_name="Work Place Type",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="work_places",
                        to="data_model.project",
                    ),
                ),
            ],
            options={
                "verbose_name": "Work Place",
                "verbose_name_plural": "Work Places",
                "db_table": "work_place",
            },
        ),
        migrations.CreateModel(
            name="WorkItem",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255, verbose_name="Name of Work Item")),
                ("source_url", models.CharField(blank=True, max_length=255, verbose_name="Source URL")),
                ("github_issue_id", models.CharField(blank=True, max_length=255, verbose_name="Github Issue ID")),
                ("data", models.JSONField(blank=True, null=True, verbose_name="Data")),
                (
                    "token_amount",
                    models.DecimalField(
                        blank=True,
                        decimal_places=0,
                        help_text="Total amount",
                        max_digits=78,
                        null=True,
                        verbose_name="Total Amount",
                    ),
                ),
                (
                    "onchain_transfer_tx",
                    models.CharField(blank=True, max_length=255, verbose_name="Onchain Transfer Tx"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("work_pending", "Work Pending"),
                            ("work_canceled", "Work Canceled"),
                            ("work_confirmed", "Work Confirmed"),
                            ("work_done", "Work Done"),
                            ("transfer_pending", "Transfer Pending"),
                            ("transfer_failed", "Transfer Failed"),
                            ("transfer_done", "Transfer Done"),
                        ],
                        default="work_pending",
                        max_length=16,
                        verbose_name="Status",
                    ),
                ),
                (
                    "contributors",
                    models.ManyToManyField(
                        blank=True,
                        db_table="contributors_to_work_items",
                        related_name="work_items",
                        to="data_model.contributor",
                    ),
                ),
                (
                    "workplace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="work_items",
                        to="data_model.workplace",
                    ),
                ),
            ],
            options={
                "verbose_name": "Work Item",
                "verbose_name_plural": "Work Items",
                "db_table": "work_item",
            },
        ),
        migrations.CreateModel(
            name="Treasury",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(blank=True, max_length=255, verbose_name="Name of Treasury")),
                (
                    "address",
                    models.CharField(
                        blank=True,
                        help_text="EVM compatible onchain address in hexadecimal format, e.g., 0xc93e3....8a5d",
                        max_length=42,
                        verbose_name="Address",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="treasuries", to="data_model.project"
                    ),
                ),
            ],
            options={
                "verbose_name": "Treasury",
                "verbose_name_plural": "Treasuries",
                "db_table": "treasury",
            },
        ),
        migrations.CreateModel(
            name="Token",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(blank=True, max_length=255, verbose_name="Name")),
                ("onchain_address", models.CharField(blank=True, max_length=255, verbose_name="Onchain Address")),
                ("symbol", models.CharField(blank=True, max_length=255, verbose_name="Symbol")),
                (
                    "total_supply",
                    models.DecimalField(
                        blank=True,
                        decimal_places=0,
                        help_text="Total supply",
                        max_digits=78,
                        null=True,
                        verbose_name="Total Supply",
                    ),
                ),
                (
                    "project",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, related_name="token", to="data_model.project"
                    ),
                ),
            ],
            options={
                "verbose_name": "Token",
                "verbose_name_plural": "Tokens",
                "db_table": "token",
            },
        ),
        migrations.AddConstraint(
            model_name="workplace",
            constraint=models.UniqueConstraint(fields=("github_repo_id",), name="unique_github_repo_id"),
        ),
    ]
