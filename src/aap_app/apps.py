# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class AapAppConfig(AppConfig):
    name = 'aap_app'
    label = 'aap'
    verbose_name = _(u'Análisis de parches')

