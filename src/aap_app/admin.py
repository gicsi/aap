# -*- coding: utf-8 -*-

from django.contrib import admin
from django_ace import AceWidget
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as __
from models import *
from datetime import datetime



###############################################################################
###############################################################################

class AnalistaAsignadoInline(admin.StackedInline): # TabularInline
    model = AnalistaAsignado
    extra = 1

class RamaInline(admin.StackedInline): # TabularInline
    model = Rama
    extra = 1

class ReglaConfiguradaInline(admin.StackedInline): # TabularInline
    model = ReglaConfigurada
    extra = 1

###############################################################################
###############################################################################

class CategoriaProyectoSoftwareAdmin(admin.ModelAdmin):
	# list_per_page = 100
	# list_display = ()
	# list_filter = []
	# search_fields = []
	# list_editable = False
	# fields = []
	# readonly_fields = []
	# inlines = []
	list_per_page = 10
	search_fields = ['nombre']
admin.site.register(CategoriaProyectoSoftware, CategoriaProyectoSoftwareAdmin)

###############################################################################

class SistemaOperativoAdmin(admin.ModelAdmin):
	list_per_page = 10
	search_fields = ['nombre']
admin.site.register(SistemaOperativo, SistemaOperativoAdmin)

###############################################################################

class LenguajeProgramacionAdmin(admin.ModelAdmin):
	list_per_page = 10
	search_fields = ['nombre']
admin.site.register(LenguajeProgramacion, LenguajeProgramacionAdmin)

###############################################################################

class ProyectoSoftwareAdmin(admin.ModelAdmin):
	list_per_page = 10
	search_fields = ['nombre']
	list_display = ('nombre', 'categoria_proyecto_software', 'lenguaje_programacion')
	inlines = (AnalistaAsignadoInline,)
admin.site.register(ProyectoSoftware, ProyectoSoftwareAdmin)

###############################################################################

class AnalistaAsignadoAdmin(admin.ModelAdmin):
	list_per_page = 10
	search_fields = ['analista', 'proyecto_software']
	list_display = ('analista', 'proyecto_software', 'tarea')
admin.site.register(AnalistaAsignado, AnalistaAsignadoAdmin)

###############################################################################

class RepositorioAdmin(admin.ModelAdmin):
	list_per_page = 10
	search_fields = ['url']
	list_display = ('url', 'fechahora_ult_pull', 'activo')
	readonly_fields = ('fechahora_ult_pull',)
	inlines = [RamaInline]
admin.site.register(Repositorio, RepositorioAdmin)

###############################################################################

class RamaAdmin(admin.ModelAdmin):
	list_per_page = 10
	search_fields = ['rama', 'repositorio']
	list_display = ('rama', 'repositorio', 'fechahora_ult_analisis', 'activa')
	readonly_fields = ('fechahora_ult_analisis',)
	inlines = (ReglaConfiguradaInline,)
admin.site.register(Rama, RamaAdmin)

###############################################################################

class AlertaAdmin(admin.ModelAdmin):
	list_per_page = 10
	search_fields = ['mensaje', 'descripcion']
	list_display = ('id', 'fechahora', 'rama', 'mensaje')

	def save_model(self, request, obj, form, change):
		obj.save()
		LogGeneral.objects.create(fechahora=datetime.now(),
								  log=": ".join(("ADMIN",
								  				 __("alerta"),
								  				 str(obj.id),
								  				 __("usuario analista"),
								  				 request.user.username)),
								  detalle="",
								  nivel=LOG_GENERAL_NIVEL_INFO)

admin.site.register(Alerta, AlertaAdmin)

###############################################################################

class NotaAdmin(admin.ModelAdmin):
	list_per_page = 10
	search_fields = ['titulo', 'contenido']
	list_display = ('id', 'fechahora', 'autor', 'titulo')

	def save_model(self, request, obj, form, change):
		obj.save()
		LogGeneral.objects.create(fechahora=datetime.now(),
								  log=": ".join(("ADMIN",
								  				 __("nota"),
								  				 str(obj.id),
								  				 __("usuario analista"),
								  				 request.user.username)),
								  detalle="",
								  nivel=LOG_GENERAL_NIVEL_INFO)

admin.site.register(Nota, NotaAdmin)

###############################################################################

class LogGeneralAdmin(admin.ModelAdmin):
	list_per_page = 10
	search_fields = ['log', 'detalle']
	list_display = ('fechahora', 'log', 'nivel')
	list_filter = ['nivel', 'fechahora']

	actions = None
	#readonly_fields = LogGeneral._meta.get_all_field_names()
	def get_readonly_fields(self, request, obj=None):
		return self.fields or [f.name for f in self.model._meta.fields] 
	def has_add_permission(self, request, obj=None):
		return False
	def has_change_permission(self, request, obj=None):
		if request.method not in ('GET', 'HEAD'):
			return False
		return super(LogGeneralAdmin, self).has_change_permission(request, obj)
	#def has_delete_permission(self, request, obj=None):
	#	return False
	def change_view(self, request, object_id, form_url='', extra_context=None):
		extra_context = extra_context or {}
		extra_context['show_save_and_add_another'] = False
		extra_context['show_save_and_continue'] = False
		extra_context['show_save'] = False
		return super(LogGeneralAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)
admin.site.register(LogGeneral, LogGeneralAdmin)

###############################################################################

class ReglaAnalisisAdmin(admin.ModelAdmin):
	list_per_page = 10
	search_fields = ['nombre']
	formfield_overrides = {
		TextFieldACE: {'widget': AceWidget(mode='python', theme='monokai', width="100%")},
	}
admin.site.register(ReglaAnalisis, ReglaAnalisisAdmin)

###############################################################################

class ReglaConfiguradaAdmin(admin.ModelAdmin):
	list_per_page = 10
	search_fields = ['rama', 'regla']
	list_display = ('rama', 'regla', 'configuracion')
admin.site.register(ReglaConfigurada, ReglaConfiguradaAdmin)



###############################################################################
###############################################################################
###############################################################################


#https://bitcalm.com/blog/making-custom-report-tables-using-angularjs-and-django-in-10-minutes/
#http://blog.tryolabs.com/2012/06/18/django-administration-interface-non-staff-users/

###############################################################################
###############################################################################
###############################################################################

from django.contrib.admin.templatetags.admin_modify import *
from django.contrib.admin.templatetags.admin_modify import submit_row as original_submit_row

@register.inclusion_tag('admin/submit_line.html', takes_context=True)
def submit_row(context):
	ctx = original_submit_row(context)
	ctx.update({
		'show_save_and_add_another': context.get('show_save_and_add_another', ctx['show_save_and_add_another']),
		'show_save_and_continue': context.get('show_save_and_continue', ctx['show_save_and_continue']),
		'show_save': context.get('show_save', ctx['show_save'])
	})
	return ctx