from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Company(models.Model):
    name = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, unique=True)  # exemplo BR
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    companies = models.ManyToManyField(Company, related_name="superusers", blank=True)

    def __str__(self):
        return f"{self.user.username} profile"
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class RenewableDoc(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="renewable_docs")
    id=models.AutoField(primary_key=True)
    doc_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    os_number = models.CharField(max_length=50)
    renewed_at = models.DateField()
    expiration_date = models.DateField()
    doc_url = models.URLField()
    alert_sent = models.BooleanField(default=False)

    def __str__(self):
        return self.doc_name


class Budget(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="budgets")
    id=models.AutoField(primary_key=True)
    os_number = models.CharField(max_length=50)
    service_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    scheduled_date = models.DateField()
    service_provider = models.CharField(max_length=255)
    doc_url = models.URLField()


    def __str__(self):
        return f"{self.service_name} - {self.os_number}"


class Finance(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="finances")
    id=models.AutoField(primary_key=True)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    invoice = models.URLField()
    contract = models.URLField()

    def __str__(self):
        return f"Invoice {self.invoice}"


class ConstitutiveDocument(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="constitutive_documents")
    id=models.AutoField(primary_key=True)
    doc_name = models.CharField(max_length=255)
    doc_url = models.URLField()

    def __str__(self):
        return self.doc_url
