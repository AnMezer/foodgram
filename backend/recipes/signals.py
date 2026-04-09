from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from recipes.models.recipe import Recipe


@receiver(post_delete, sender=Recipe)
def delete_recipe_image(sender, instance, **kwargs):
    """После удаления рецепта удаляет файл с его изображением"""
    if instance.image:
        instance.image.delete(save=False)


@receiver(pre_save, sender=Recipe)
def delete_old_recipe_image(sender, instance, **kwargs):
    """Перед обновлением рецепта удаляет файл с его старым изображением"""
    if not instance.pk:
        return
    old_instance = Recipe.objects.filter(pk=instance.pk).first()
    if old_instance.image and instance.image:
        old_instance.image.delete(save=False)
