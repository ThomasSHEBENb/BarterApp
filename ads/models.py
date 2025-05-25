from django.db import models
from django.contrib.auth.models import User

class Ad(models.Model):
    CONDITION_CHOICES = [
        ('new', 'Новый'),
        ('used', 'Б/У'),
    ]
    CATEGORY_CHOICES = [
    ('books', 'Книги'),
    ('electronics', 'Электроника'),
    ('clothes', 'Одежда'),
    ('transport', 'Транспорт'),
    ('furniture', 'Мебель'),
    ('other', 'Другое')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='ad_images/', blank=True, null=True)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



class ExchangeProposal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('accepted', 'Принята'),
        ('rejected', 'Отклонена'),
    ]

    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exchange_proposals')
    ad_sender = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='sent_proposals')
    ad_receiver = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='received_proposals')
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Обмен: {self.ad_sender} → {self.ad_receiver} ({self.status})'

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Уведомление для {self.user.username}: {self.message}'