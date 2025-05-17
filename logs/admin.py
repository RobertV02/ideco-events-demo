from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display  = ('created_at', 'src_ip', 'dst_ip', 'protocol', 'action')
    search_fields = ('src_ip', 'dst_ip', 'raw_message')
    list_filter   = ('action', 'protocol')
    ordering      = ('-created_at',)
