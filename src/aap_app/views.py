# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.template import RequestContext
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as __
from django.utils.html import strip_tags
from django.utils.html import escape
from models import *
from datetime import datetime


###############################################################################

#@login_required
#@staff_member_required
#def index(request):
#    return redirect('/admin/')

@login_required(login_url='/login/')
def index(request):
	'''
	Home, index, "/"
	'''

	###########################################################################
	if 'rev' in request.GET:
		alerta = Alerta.objects.get(id=request.GET['rev'])
		alerta.revisada = True
		alerta.save()
		LogGeneral.objects.create(fechahora=datetime.now(),
								  log=": ".join(("WEB",
								  				 __("ALERTA REVISADA"),
								  				 str(alerta.id),
								  				 __("usuario analista"),
								  				 request.user.username)),
								  detalle="",
								  nivel=LOG_GENERAL_NIVEL_INFO)
		return redirect('/')

	###########################################################################
	if 'aid' in request.POST:
		alerta = Alerta.objects.get(id=request.POST['aid'])
		tit = escape(request.POST['tit'])
		con = escape(request.POST['con'])
		nota = Nota.objects.create(autor=request.user, alerta=alerta, titulo=tit, contenido=con)
		LogGeneral.objects.create(fechahora=datetime.now(),
								  log=": ".join(("WEB",
								  				 __("AGREGAR NOTA"),
								  				 str(nota.id),
								  				 __("alerta"),
								  				 str(alerta.id),
								  				 __("usuario analista"),
								  				 request.user.username)),
								  detalle="",
								  nivel=LOG_GENERAL_NIVEL_INFO)
		return redirect('/')

	###########################################################################
	###########################################################################

	ctx = {}

	###########################################################################
	ctx['alertas'] = []
	for alerta in Alerta.objects.filter(revisada=False):
		ctx['alertas'].append(alerta)

	###########################################################################
	ctx['repositorios'] = []
	for repositorio in Repositorio.objects.filter(activo=True):
		if request.user not in repositorio.proyecto_software.analistas.all():
			continue
		ctx['repositorios'].append(repositorio)

	###########################################################################
	ctx['reglas'] = []
	for regla in ReglaAnalisis.objects.filter(activa=True):
		ctx['reglas'].append(regla)

	return render(request, 'aap/index.html', ctx)

###############################################################################

@login_required
def dashboard(request):
	'''
	Dashboard
	'''

	ctx = {}

	ctx['chart1_title'] = _(u'Proyectos por Categorías')
	ctx['chart1_col_name'] = _(u'Categoría')
	ctx['chart1_col_data'] = _('Cantidad')
	ctx['chart1_data'] = ''
	for categoria in CategoriaProyectoSoftware.objects.all():
		cnt = ProyectoSoftware.objects.filter(categoria_proyecto_software=categoria).count()
		if ctx['chart1_data'] != '':
			ctx['chart1_data'] = ctx['chart1_data'] + ','
		ctx['chart1_data'] = ctx['chart1_data'] + '["' + categoria.nombre.replace('"', '') + '", ' + str(cnt) + ']'

	ctx['chart2_title'] = _(u'Proyectos por Lenguajes/Tecnologías')
	ctx['chart2_col_name'] = _(u'Lenguaje')
	ctx['chart2_col_data'] = _('Cantidad')
	ctx['chart2_data'] = ''
	for lenguaje in LenguajeProgramacion.objects.all():
		cnt = ProyectoSoftware.objects.filter(lenguaje_programacion=lenguaje).count()
		if ctx['chart2_data'] != '':
			ctx['chart2_data'] = ctx['chart2_data'] + ','
		ctx['chart2_data'] = ctx['chart2_data'] + '["' + lenguaje.nombre.replace('"', '') + '", ' + str(cnt) + ']'

	ctx['chart3_title'] = _(u'Proyectos por Sistemas Operativos')
	ctx['chart3_col_name'] = _(u'Sistema Operativo')
	ctx['chart3_col_data'] = _('Cantidad')
	ctx['chart3_data'] = ''
	for so in SistemaOperativo.objects.all():
		cnt = ProyectoSoftware.objects.filter(sistemas_operativos=so).count()
		if ctx['chart3_data'] != '':
			ctx['chart3_data'] = ctx['chart3_data'] + ','
		ctx['chart3_data'] = ctx['chart3_data'] + '["' + so.nombre.replace('"', '') + '", ' + str(cnt) + ']'

	return render(request, 'aap/dashboard.html', ctx)

###############################################################################

#@login_required
#@staff_member_required
def status(request):
    #return HttpResponse("OK", content_type="text/plain")
    data = {'status': "OK"}
    return JsonResponse(data)


###############################################################################
