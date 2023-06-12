from django.db.models import signals
from django.dispatch import receiver
from .models import Doctor, DocWorkDay, Patient

# pre_save method signal
# @receiver(signals.pre_save, sender=DocWorkDay)
# def check_product_description(sender, instance, **kwargs):
#     if not instance.description:
#         instance.description = 'This is Default Description'
    
# post_save method
@receiver(signals.post_save, sender=DocWorkDay) 
def create_product(sender, instance, created, **kwargs):
    
    print("Save method is called") 