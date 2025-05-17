from django.db import models


class Event(models.Model):
    """
    Универсальная запись журнала после нормализации.
    """
    created_at   = models.DateTimeField(auto_now_add=True)
    src_ip       = models.GenericIPAddressField(verbose_name='Источник')
    dst_ip       = models.GenericIPAddressField(verbose_name='Назначение')
    protocol     = models.CharField(max_length=10, blank=True)
    action       = models.CharField(max_length=32, help_text='ALLOW / DROP / etc.')
    raw_message  = models.TextField()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Событие'
        verbose_name_plural = 'События'

    def __str__(self):
        return f'{self.created_at:%H:%M:%S} {self.src_ip} → {self.dst_ip} [{self.action}]'
