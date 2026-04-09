from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save
from django.dispatch import receiver

User = get_user_model()


@receiver(pre_save, sender=User)
def delete_avatar(sender, instance, **kwargs):
    """Удаляет файл аватара"""
    if not instance.pk:
        return
    old_instance = User.objects.filter(pk=instance.pk).first()
    old_instance.avatar.delete(save=False)
