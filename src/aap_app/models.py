# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from datetime import date, datetime, timedelta
import random
import hashlib
import os


################################################################################

ALERTAS_CRITICIDAD_ALTA = '1'
ALERTAS_CRITICIDAD_MEDIA = '2'
ALERTAS_CRITICIDAD_BAJA = '3'
ALERTAS_CRITICIDAD_CHOICES = (
    (ALERTAS_CRITICIDAD_ALTA, _('ALTA')),
    (ALERTAS_CRITICIDAD_MEDIA, _('MEDIA')),
    (ALERTAS_CRITICIDAD_BAJA, _('BAJA')),
)

LOG_GENERAL_NIVEL_INFO = '1'
LOG_GENERAL_NIVEL_WARN = '2'
LOG_GENERAL_NIVEL_ERROR = '3'
LOG_GENERAL_NIVEL_FATAL = '4'
LOG_GENERAL_NIVEL_CHOICES = (
    (LOG_GENERAL_NIVEL_INFO, _('INFO')),
    (LOG_GENERAL_NIVEL_WARN, _('WARN')),
    (LOG_GENERAL_NIVEL_ERROR, _('ERROR')),
    (LOG_GENERAL_NIVEL_FATAL, _('FATAL')),
)

################################################################################

class TextFieldACE(models.TextField):
    pass

################################################################################

CODIGO_REGLA_EJEMPLO = '''

class PluginDemo(PluginAAP):
    """
    Implementación de clase de ejemplo o demo para plugin, este sería el código 
    fuente de regla de análisis
    //
    Implementation of example or demo class for plugin, this would be the source
    code of the analysis rule
    """

    def validate_config_string(self):
        """
        Validar configuración de instancia; debe retornar verdadero o falso,
        o generar una excepción
        //
        Validate instance configuration; should return true or false, or 
        raise an exception
        """

        config_string = self.get_config_string()
        if not config_string is None and not config_string.strip() == '':
            return True
        # raise ValueError('error desc...')
        return False

    def test_commit(self, commit_obj=None):
        """
        Testear la instancia del objeto commit y agregar línea de resultados
        si la regla y configuración aplican
        //
        Test commit object instance and add test results line if rule and
        configuration apply
        """

        if (commit_obj.author in self.get_config_string().split(',')):
            self.add_test_result('commit: %s - author: %s - date: %s'
                                % (commit_obj.abbr_hash, commit_obj.author, 
                                   commit_obj.author_date))

        return

        """
        Referencia para el uso de la instancia del objeto commit_obj:
        //
        Reference for using commit_obj object instance:
        -----------------------------------------------------------------------
            hash            string: hash of commit
            abbr_hash       string: abbreviated hash of commit
            parent_hash     string: hash of parent commit
            author          string: name of author of commit
            committer       string: name of committer of commit
            author_email    string: email of author
            committer_email string: email of committer
            author_date     datetime: date of author first commit
            committer_date  datetime: date of committer last commit
            subject         string: subject of commit
            body            string: possible multiline, body of commit
            notes           string: possible multiline, notes of commit
            files           array: list of files
            patches         string: possible multiline, raw patch/es source
            branch          string: name of branch tested
            diff_branch     string: name of branch compared against
            local_path      string: local path of repository (branch activated)
        """

    def test_branch(self, local_path=''):
        """
        Alternativa para testear el proyecto completo y agregar resultados si la
        regla y configuración aplican
        //
        Alternative to test project as a whole and add results line if rule and
        configuration apply
        """

        return

'''

################################################################################

class CategoriaProyectoSoftware(models.Model):
    nombre = models.CharField(verbose_name=_('nombre'), help_text=_('Nombre de referencia'), max_length=255, unique=True)
    descripcion = models.TextField(verbose_name=_(u'descripción'), help_text=_(u'Descripción detallada'), blank=True)
    class Meta:
        ordering = ['nombre']
        verbose_name = _(u'categoría de proyecto')
        verbose_name_plural = _(u'categorías de proyectos')
    def __unicode__(self):
        return self.nombre

class SistemaOperativo(models.Model):
    nombre = models.CharField(verbose_name=_('nombre'), help_text=_('Nombre de referencia'), max_length=255, unique=True)
    descripcion = models.TextField(verbose_name=_(u'descripción'), help_text=_(u'Descripción detallada'), blank=True)
    class Meta:
        ordering = ['nombre']
        verbose_name = _('sistema operativo')
        verbose_name_plural = _('sistemas operativos')
    def __unicode__(self):
        return self.nombre

class LenguajeProgramacion(models.Model):
    nombre = models.CharField(verbose_name=_('nombre'), help_text=_('Nombre de referencia'), max_length=255, unique=True)
    descripcion = models.TextField(verbose_name=_(u'descripción'), help_text=_(u'Descripción detallada'), blank=True)
    class Meta:
        ordering = ['nombre']
        verbose_name = _('lenguaje de desarrollo')
        verbose_name_plural = _('lenguajes de desarrollo')
    def __unicode__(self):
        return self.nombre

class ProyectoSoftware(models.Model):
    categoria_proyecto_software = models.ForeignKey(CategoriaProyectoSoftware, verbose_name=_(u'categoría de proyecto de software'), help_text=_(u'Categoría de proyecto del proyecto de software'), related_name='proyectos')
    sistemas_operativos = models.ManyToManyField(SistemaOperativo, verbose_name=_('sistemas operativos'), help_text=_('Sistemas operativos del proyecto de software'), related_name='proyectos')
    lenguaje_programacion = models.ForeignKey(LenguajeProgramacion, verbose_name=_(u'lenguaje de programación'), help_text=_(u'Lenguaje de progrmación utilizado en el proyecto de software'), related_name='proyectos')
    nombre = models.CharField(verbose_name=_('nombre'), help_text=_('Nombre de referencia'), max_length=255, unique=True)
    descripcion = models.TextField(verbose_name=_(u'descripción'), help_text=_(u'Descripción detallada'), blank=True)
    analistas = models.ManyToManyField(User, verbose_name=_('analistas'), help_text=_('Analistas asignados al proyecto de software'), related_name='proyectos', through='AnalistaAsignado')
    observaciones = models.TextField(verbose_name=_('observaciones'), help_text=_('Observaciones generales'), blank=True)
    class Meta:
        ordering = ['nombre']
        verbose_name = _('proyecto de software')
        verbose_name_plural = _('proyectos de software')
    def __unicode__(self):
        return self.nombre

class AnalistaAsignado(models.Model):
    proyecto_software = models.ForeignKey(ProyectoSoftware, verbose_name=_('proyecto de software'), help_text=_('Proyecto de software asignado'), related_name='analistas_asignados')
    analista = models.ForeignKey(User, verbose_name=_('analista'), help_text=_('Analista asignado al proyecto de softawre'), related_name='analistas_asignados')
    tarea = models.TextField(verbose_name=_('tarea'), help_text=_('Tarea/s asignada/s al analista'), blank=True)
    recibe_emails = models.BooleanField(verbose_name=_('recibe emails'), help_text=_(u'Este analista recibirá emails automáticos?'), default=False)
    fechahora = models.DateTimeField(verbose_name=_(u'fecha de asignación'), help_text=_(u'Fecha y hora de asignación del analista al proyecto de software'), auto_now_add=True)
    class Meta:
        ordering = ['analista']
        verbose_name = _('usuario analista')
        verbose_name_plural = _('usuarios analistas')
    def __unicode__(self):
        return unicode(self.analista)

# xxx - tmp
def get_rnd_ruta_local():
    return os.path.join(settings.AAP_REPOS_DIR, hashlib.md5(str(random.random())[2:]).hexdigest())
def get_fecha_inicial():
    return date.today() - timedelta(days=settings.GIT_INITIAL_LOG_DAYS_BACK)

class Repositorio(models.Model):
    proyecto_software = models.ForeignKey(ProyectoSoftware, verbose_name=_('proyecto de software'), help_text=_('Proyecto de software del repositorio'), related_name='repositorios')
    url = models.URLField(verbose_name=_('Git URL'), help_text=_('URL del repositorio (https:// o file://)'), unique=True)
    usuario = models.CharField(verbose_name=_('usuario'), help_text=_('Nombre de usuario para acceder a URL'), max_length=255, blank=True)
    contrasena = models.CharField(verbose_name=_(u'contraseña'), help_text=_(u'Contraseña para acceder a URL'), max_length=255, blank=True)
    ruta_local = models.CharField(verbose_name=_('ruta local'), help_text=_(u'Ruta/path local donde será clonado el repositorio'), max_length=255, default=get_rnd_ruta_local, unique=True)
    compara_ramas = models.BooleanField(verbose_name=_('compara ramas'), help_text=_(u'Se comparará la rama o branch default contra el resto de ramas?'), default=False)
    observaciones = models.TextField(verbose_name=_('observaciones'), help_text=_('Observaciones generales'), blank=True)
    fecha_inicial = models.DateField(verbose_name=_(u'fecha inicial'), help_text=_(u'Fecha inicial de análisis (a partir de cuándo analizar repositorio)'), blank=False, null=False, default=get_fecha_inicial)
    clonado = models.BooleanField(verbose_name=_('clonado'), help_text=_('Ya fue clonado?'), default=False)
    fechahora_ult_pull = models.DateTimeField(verbose_name=_(u'fecha de último pull'), help_text=_(u'Fecha y hora de la última vez que se actualizó el repositorio'), blank=True, null=True)
    activo = models.BooleanField(verbose_name=_('activo'), help_text=_('Se encuentra activo?'), default=True)
    class Meta:
        ordering = ['url']
        verbose_name = _('repositorio')
        verbose_name_plural = _('repositorios')
    def __unicode__(self):
        return self.url

class ReglaAnalisis(models.Model):
    nombre = models.CharField(verbose_name=_('nombre'), help_text=_('Nombre de referencia'), max_length=255, unique=True)
    descripcion = models.TextField(verbose_name=_(u'descripción'), help_text=_(u'Descripción detallada'), blank=True)
    codigo_regla = TextFieldACE(verbose_name=_(u'código de regla'), help_text=_(u'Código fuente (python) de la implementación de la regla'), blank=True, default=CODIGO_REGLA_EJEMPLO)
    criticidad_regla = models.CharField(verbose_name=_('criticidad de regla'), help_text=_(u'Criticidad de regla para alertas'), max_length=2, choices=ALERTAS_CRITICIDAD_CHOICES, default=ALERTAS_CRITICIDAD_BAJA)
    configuracion_default = models.TextField(verbose_name=_(u'configuración default/ejemplo'), help_text=_(u'Configuración de ejemplo, default o por defecto de la regla'), blank=True)
    activa = models.BooleanField(verbose_name=_('activa'), help_text=_('Se encuentra activa?'), default=True)
    class Meta:
        ordering = ['nombre']
        verbose_name = _(u'regla de análisis')
        verbose_name_plural = _(u'reglas de análisis')
    def __unicode__(self):
        return self.nombre

class Rama(models.Model):
    repositorio =  models.ForeignKey(Repositorio, verbose_name=_('repositorio'), help_text=_('Repositorio de esta rama o branch'), related_name='ramas')
    rama = models.CharField(verbose_name=_('rama'), help_text=_('Nombre de la rama o branch del repositorio'), max_length=255, default='master')
    default = models.BooleanField(verbose_name=_('rama default'), help_text=_(u'Es la rama por defecto o default? (típicamente llamada master)'), default=False)
    reglas = models.ManyToManyField(ReglaAnalisis, verbose_name=_('reglas'), help_text=_('Reglas configuradas para la rama o branch'), related_name='ramas', through='ReglaConfigurada')
    observaciones = models.TextField(verbose_name=_('observaciones'), help_text=_('Observaciones generales'), blank=True)
    fechahora_ult_analisis = models.DateTimeField(verbose_name=_(u'fecha de último análisis'), help_text=_(u'Fecha y hora del último análisis realizado a esta rama o branch del repositorio'), blank=True, null=True)
    hash_ult_commit = models.CharField(verbose_name=_(u'Hash de último commit'), help_text=_(u'Hash de último commit analizado de esta rama o branch del repositorio'), max_length=255, blank=True)
    activa = models.BooleanField(verbose_name=_('activa'), help_text=_('Se encuentra activa?'), default=True)
    class Meta:
        ordering = ['rama']
        verbose_name = _('rama o branch')
        verbose_name_plural = _('ramas o branches')
        unique_together = ('repositorio', 'rama',)
    def __unicode__(self):
        #xxx
        return self.repositorio.url + ' - ' + self.rama

class ReglaConfigurada(models.Model):
    rama = models.ForeignKey(Rama, verbose_name=_('rama o branch'), help_text=_('Rama configurada'), related_name='reglas_configuradas')
    regla = models.ForeignKey(ReglaAnalisis, verbose_name=_('regla'), help_text=_('Regla configurada'), related_name='reglas_configuradas')
    configuracion = models.TextField(verbose_name=_(u'configuración'), help_text=_(u'Configuración particular de la regla de análisis'), blank=True)
    fechahora = models.DateTimeField(verbose_name=_(u'fecha de configuración'), help_text=_(u'Fecha y hora de configuración de la regla'), auto_now_add=True)
    activa = models.BooleanField(verbose_name=_('activa'), help_text=_('Se encuentra activa?'), default=True)
    class Meta:
        ordering = ['rama']
        verbose_name = _('regla configurada')
        verbose_name_plural = _('reglas configuradas')
    def __unicode__(self):
        return unicode(self.regla.nombre + ' -> ' + self.rama.repositorio.url + ' - ' + self.rama.rama)

class Alerta(models.Model):
    rama =  models.ForeignKey(Rama, verbose_name=_('rama'), help_text=_('Rama o branch de alerta'), related_name='alertas')
    fechahora = models.DateTimeField(verbose_name=_('fecha'), help_text=_('Fecha y hora de registro de alerta'), auto_now_add=True)
    criticidad = models.CharField(verbose_name=_('criticidad'), help_text=_(u'Criticidad de alerta'), max_length=2, choices=ALERTAS_CRITICIDAD_CHOICES, default=ALERTAS_CRITICIDAD_BAJA)
    mensaje = models.CharField(verbose_name=_('mensaje'), help_text=_('Mensaje de alerta'), max_length=255)
    descripcion = models.TextField(verbose_name=_(u'descripción'), help_text=_(u'Descripción detallada de alerta'), blank=True)
    revisada = models.BooleanField(verbose_name=_('revisada'), help_text=_('Alerta revisada?'), default=False)
    class Meta:
        ordering = ['fechahora']
        verbose_name = _('alerta')
        verbose_name_plural = _('alertas')
    def __unicode__(self):
        return self.mensaje

class Nota(models.Model):
    alerta = models.ForeignKey(Alerta, verbose_name=_('alerta'), help_text=_('Alerta relacionada a nota'), related_name='notas', blank=True, null=True)
    proyecto_software = models.ForeignKey(ProyectoSoftware, verbose_name=_('proyecto de software'), help_text=_('Proyecto de software relacionado a nota'), related_name='notas', blank=True, null=True)
    repositorio =  models.ForeignKey(Repositorio, verbose_name=_('repositorio'), help_text=_('Repositorio relacionado a nota'), related_name='notas', blank=True, null=True)
    rama =  models.ForeignKey(Rama, verbose_name=_('rama'), help_text=_('Rama o branch relacionada a nota'), related_name='notas', blank=True, null=True)
    autor = models.ForeignKey(User, verbose_name=_('autor'), help_text=_('Autor de la nota'), related_name='notas')
    fechahora = models.DateTimeField(verbose_name=_('fecha'), help_text=_('Fecha y hora de registro de nota'), auto_now_add=True)
    titulo = models.CharField(verbose_name=_(u'título'), help_text=_(u'Título de la nota'), max_length=255)
    contenido = models.TextField(verbose_name=_('contenido'), help_text=_('Contenido de la nota'), blank=True)
    importante = models.BooleanField(verbose_name=_('importante'), help_text=_('Nota importante?'), default=False)
    class Meta:
        ordering = ['fechahora']
        verbose_name = _('nota de analista')
        verbose_name_plural = _('notas de analistas')
    def __unicode__(self):
        return self.titulo

class LogGeneral(models.Model):
    fechahora = models.DateTimeField(verbose_name=_('fecha'), help_text=_('Fecha y hora de registro del log'), auto_now_add=True)
    log = models.CharField(verbose_name=_('log'), help_text=_(u'Línea de log'), max_length=255)
    detalle = models.TextField(verbose_name=_('detalle'), help_text=_('Detalle de log'), blank=True)
    nivel = models.CharField(verbose_name=_('nivel'), help_text=_(u'Nivel de log'), max_length=2, choices=LOG_GENERAL_NIVEL_CHOICES, default=LOG_GENERAL_NIVEL_INFO)
    class Meta:
        ordering = ['fechahora']
        verbose_name = _('log general')
        verbose_name_plural = _('logs generales')
    def __unicode__(self):
        return self.log



