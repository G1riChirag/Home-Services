from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import UserProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_profile_on_user_create(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(pre_delete, sender=UserProfile)
def delete_vaccination_file_on_profile_delete(sender, instance, **kwargs):
    """
    Ensure uploaded vaccination PDF is deleted from storage when the profile is deleted.
    """
    if instance.vaccination_proof:
        # delete without saving model
        instance.vaccination_proof.delete(save=False)