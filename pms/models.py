from django.db import models

class Drug(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    expiration_date = models.DateField(null=True, blank=True, help_text="Format: YYYY-MM-DD")

    def __str__(self):
        return self.name

class Prescription(models.Model):
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
    patient_name = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    prescribed_amount = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.patient_name} - {self.drug.name} (Qty: {self.prescribed_amount})"