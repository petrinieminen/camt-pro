from django.db import models
from django.utils import timezone

class ApiResource(models.Model):
    company_name = models.CharField(max_length=30)
    api_base_url = models.CharField(max_length=250, default=None)
    api_service_name = models.CharField(max_length=50, default=None)
    default_company = models.TextField(max_length=30, default=None)
    tenant_id = models.TextField(max_length=30, default=None, null=True, blank=True)
    api_username = models.CharField(max_length=50, default=None)
    api_pass = models.CharField(max_length=50, default=None)
    keepass_uuid = models.TextField()

    log_date = models.DateTimeField("date logged")

    def __str__(self):
        """Returns a string representation of a API location entry."""
        date = timezone.localtime(self.log_date)
        return f"'{self.company_name}' logged on {date.strftime('%A, %d %B, %Y at %X')} creds: {self.api_username}"