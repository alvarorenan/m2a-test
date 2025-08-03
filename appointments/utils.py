"""
Utilitários para o app appointments
"""

from django.utils import timezone


def get_local_now():
    """
    Retorna o datetime atual no timezone configurado (America/Sao_Paulo)
    """
    return timezone.localtime(timezone.now())


def get_local_today():
    """
    Retorna a data atual no timezone configurado (America/Sao_Paulo)
    """
    return get_local_now().date()
