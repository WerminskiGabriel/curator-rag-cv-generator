from django.db import models


class Offer(models.Model):
	title = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	remote = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.title
