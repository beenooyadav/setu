from django.contrib.auth.models import User
from django.db import models


class TransactionLog(models.Model):
    """
    Record is maintained in following manner
    contact_a gives contact_b amount.
    """
    contact_a = models.ForeignKey(User, related_name='giver', on_delete=models.CASCADE)
    contact_b = models.ForeignKey(User, related_name='borrower', on_delete=models.CASCADE)
    amount = models.FloatField()
    is_settled = models.BooleanField(default=False)
    created_time = models.DateTimeField(auto_now_add=True)
