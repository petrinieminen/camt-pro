from django.db import models
from django.utils import timezone

class ApiResource(models.Model):
    company_name = models.CharField(max_length=30)
    api_url = models.TextField()
    api_username = models.CharField(max_length=50)
    api_pass = models.CharField(max_length=50)
    keepass_uuid = models.TextField()

    description = models.CharField(max_length=300)
    log_date = models.DateTimeField("date logged")

    def __str__(self):
        """Returns a string representation of a message."""
        date = timezone.localtime(self.log_date)
        return f"'{self.company_name}' logged on {date.strftime('%A, %d %B, %Y at %X')} creds: {self.api_username}"