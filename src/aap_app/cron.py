# -*- coding: utf-8 -*-

#from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as _
from django.utils import timezone, translation
from django.conf import settings
from django.core.mail import send_mail
from datetime import date, datetime, timedelta
import dateutil.parser
import re
import hashlib
import pickle, functools, operator
from nltk.util import ngrams
from nltk.corpus import stopwords
from nltk.tokenize import wordpunct_tokenize
import subprocess, shlex
import os
from models import *

CRON_DEBUG = settings.DEBUG

def actualizar_y_analizar_repos():
    """
    Proceso principal para la actualización de repositorios y ejecución de los análisis.
    """

    # establecer idioma según configuración
    translation.activate(settings.CRON_PROCESS_LANGUAGE_CODE)

    # registro de inicio
    log_general(_(u'Proceso cron inciado'))

    # cargar reglas / código de plugin
    reglas_ok = 0
    for regla in ReglaAnalisis.objects.filter(activa=True):
      codigo_regla = re.sub('^class\s+\w+\(', 'class PluginClassId' + str(regla.id) + '(', regla.codigo_regla, flags=re.MULTILINE)
      try:
        #ns = dict(globals())
        #code = compile(codigo_regla', '<string>', 'exec')
        #exec code in ns
        #exec(code, globals(), locals())
        exec(codigo_regla, globals(), locals())
        reglas_ok = reglas_ok + 1
      except Exception as ex:
        log_general(_(u'Error al cargar código de regla/plugin: %s: %s') % (regla.nombre, ex.message), str(ex), nivel=LOG_GENERAL_NIVEL_ERROR)
        return
    log_general(_(u'Código de reglas/plugins cargados: %s') % str(reglas_ok))

    # por cada rama o branch...
    for rama in Rama.objects.filter(activa=True):

      # repo activo?
      if not rama.repositorio.activo:
        log_general(_(u'Repositorio %s desactivado') % rama.repositorio.url)
        continue

      # procesar rama/branch
      log_general(_(u'Se procesará rama o branch %s de %s') % (rama.rama, rama.repositorio.url))
      
      # ya clonado?
      if not rama.repositorio.clonado:

        # clonar repo
        log_general(_(u'Repositorio %s aún no clonado') % rama.repositorio.url)
        repo_url = rama.repositorio.url
        if rama.repositorio.usuario != '' and rama.repositorio.contrasena != '' and repo_url.startswith('http'):
          repo_url = repo_url.replace('//', '//' + rama.repositorio.usuario + ':' + rama.repositorio.contrasena + '@', 1)
        (stdout, stderr, ret) = ejecutar('git clone %s %s' % (repo_url, rama.repositorio.ruta_local))
        if ret != 0:
          log_general(_(u'Error al clonar repositorio'), stderr, nivel=LOG_GENERAL_NIVEL_ERROR)
          return
        else:
          rama.repositorio.clonado = True
          rama.repositorio.save()
          log_general(_(u'Repositorio clonado exitosamente'))

          # hacer checkout de cada uno de sus branches
          for rama_co in rama.repositorio.ramas.all(): # no sólo la activa
            (stdout, stderr, ret) = ejecutar('git checkout %s' % rama_co.rama, rama.repositorio.ruta_local)
            if ret != 0:
              log_general(_(u'Error al ejecutar checkout inicial de %s') % rama_co.rama, stderr, nivel=LOG_GENERAL_NIVEL_ERROR)
              return

      # actualizar repo
      (stdout, stderr, ret) = ejecutar('git pull', rama.repositorio.ruta_local)
      if ret != 0:
        log_general(_(u'Error al ejecutar pull de %s') % rama.repositorio.url, stderr, nivel=LOG_GENERAL_NIVEL_ERROR)
        return
      rama.repositorio.fechahora_ult_pull = timezone.now()
      rama.repositorio.save()

      # hacer checkout de la rama
      (stdout, stderr, ret) = ejecutar('git checkout %s' % rama.rama, rama.repositorio.ruta_local)
      if ret != 0:
        log_general(_(u'Error al ejecutar checkout de %s') % rama.rama, stderr, nivel=LOG_GENERAL_NIVEL_ERROR)
        return

      # ya se procesaron commits de la rama?
      if rama.hash_ult_commit != '':
        git_commits_filter = rama.hash_ult_commit + '..'
      else:
        #git_commits_filter = '--since "' + (date.today() - timedelta(days=settings.GIT_INITIAL_LOG_DAYS_BACK)).isoformat() + '"'
        git_commits_filter = '--since "' + rama.repositorio.fecha_inicial.isoformat() + '"'

      # obtener últimos commits (no procesados)
      commit_lines = ''
      rama_actualizada = False
      (stdout, stderr, ret) = ejecutar('git log --pretty=format:"%%H||%%h||%%P||%%an||%%cn||%%ae||%%ce||%%ai||%%ci||%%s||%s" %s' % (rama.rama, git_commits_filter), rama.repositorio.ruta_local)
      if ret != 0:
        log_general(_(u'Error al recuperar últimos commits de %s') % rama.rama, stderr, nivel=LOG_GENERAL_NIVEL_ERROR)
        return
      if stdout:
        commit_lines = commit_lines + stdout
        rama_actualizada = True

      # obtener también commits de diferencias entre ramas?
      if rama.default and rama.repositorio.compara_ramas:
        # diferencias desde último análisis
        if rama.fechahora_ult_analisis:
          git_commits_filter_diff = '--since "' + rama.fechahora_ult_analisis.date().isoformat() + '"'
        else:
          git_commits_filter_diff = '--since "' + rama.repositorio.fecha_inicial.isoformat() + '"'
        for rama_diff in rama.repositorio.ramas.all(): # no sólo las activas
          if rama_diff.rama == rama.rama:
            continue
          (stdout, stderr, ret) = ejecutar('git log --pretty=format:"%%H||%%h||%%P||%%an||%%cn||%%ae||%%ce||%%ai||%%ci||%%s||%s" %s %s...%s' % (rama_diff.rama, git_commits_filter_diff, rama.rama, rama_diff.rama), rama.repositorio.ruta_local)
          if ret != 0:
            log_general(_(u'Error al recuperar últimos commits de %s') % rama.rama, stderr, nivel=LOG_GENERAL_NIVEL_ERROR)
            return
          if stdout:
            if commit_lines != '':
              commit_lines = commit_lines + '\n'
            commit_lines = commit_lines + stdout

      # instancias, reglas y asignaciones de plugins
      plugin_objs = {}
      plugin_reglas = {}
      plugin_reglas_conf = {}
      # recuperar código y configuraciones de plugins/reglas
      for regla_configurada in rama.reglas_configuradas.filter(activa=True):
        regla = ReglaAnalisis.objects.get(id=regla_configurada.regla.id)
        if not regla.activa:
          continue
        #tmp_plugin_key = hashlib.md5(str(regla_configurada.regla.id) + regla_configurada.configuracion).hexdigest()
        tmp_plugin_key = str(regla_configurada.id)
        try:
          plugin_objs[tmp_plugin_key] = eval('PluginClassId' + str(regla_configurada.regla.id) + '(regla_configurada.configuracion)')
        except Exception as ex:
          log_general(_(u'Error al instanciar regla/plugin: %s: %s') % (regla.nombre, ex.message), str(ex), nivel=LOG_GENERAL_NIVEL_ERROR)
          return
        plugin_reglas[tmp_plugin_key] = regla
        plugin_reglas_conf[tmp_plugin_key] = regla_configurada

      # por cada commit...
      lines = commit_lines.splitlines()
      for line in lines:
        
        try:

          # obtener hash, autor, committer, fechas, ... de commit
          arr_line = line.split('||')
          commit_hash = arr_line[0]
          commit_abbr_hash = arr_line[1]
          commit_parent_hash = arr_line[2]
          commit_author = arr_line[3]
          commit_committer = arr_line[4]
          commit_author_email = arr_line[5]
          commit_committer_email = arr_line[6]
          commit_author_date = arr_line[7]
          commit_committer_date = arr_line[8]
          commit_subject  = arr_line[9]
          commit_diff_branch  = arr_line[10]

          # obtener body de commit
          (stdout, stderr, ret) = ejecutar('git log --pretty=format:"%%b" -1 %s' % commit_hash, rama.repositorio.ruta_local)
          if ret != 0:
            log_general(_(u'Error al recuperar body de commit de %s') % rama.rama, stderr, nivel=LOG_GENERAL_NIVEL_ERROR)
            return
          commit_body = stdout

          # obtener notas de commit
          (stdout, stderr, ret) = ejecutar('git log --pretty=format:"%%N" -1 %s' % commit_hash, rama.repositorio.ruta_local)
          if ret != 0:
            log_general(_(u'Error al recuperar notes de commit de %s') % rama.rama, stderr, nivel=LOG_GENERAL_NIVEL_ERROR)
            return
          commit_notes = stdout

          # obtener archivos modificados
          (stdout, stderr, ret) = ejecutar('git log --pretty="format:" --name-only -1 %s' % commit_hash, rama.repositorio.ruta_local)
          if ret != 0:
            log_general(_(u'Error al recuperar notes de commit de %s') % rama.rama, stderr, nivel=LOG_GENERAL_NIVEL_ERROR)
            return
          commit_files = stdout

          # obtener diferencias/parches de commit
          (stdout, stderr, ret) = ejecutar('git log --pretty="format:" -p -1 %s' % commit_hash, rama.repositorio.ruta_local)
          if ret != 0:
            log_general(_(u'Error al recuperar parches de commit de %s') % rama.rama, stderr, nivel=LOG_GENERAL_NIVEL_ERROR)
            return
          commit_patches = stdout

          # objeto commit para plugins/reglas
          commit = CommitAAP(commit_hash=commit_hash,
                             commit_abbr_hash=commit_abbr_hash,
                             commit_parent_hash=commit_parent_hash,
                             commit_author=commit_author,
                             commit_committer=commit_committer,
                             commit_author_email=commit_author_email,
                             commit_committer_email=commit_committer_email,
                             commit_author_date=commit_author_date,
                             commit_committer_date=commit_committer_date,
                             commit_subject=commit_subject,
                             commit_body=commit_body,
                             commit_notes=commit_notes,
                             commit_files=commit_files,
                             commit_patches=commit_patches,
                             commit_branch=rama.rama,
                             commit_diff_branch=commit_diff_branch,
                             commit_local_path=rama.repositorio.ruta_local)

          # ejecutar testeo en plugins
          for tmp_key in plugin_objs:
            try:
              plugin_objs[tmp_key].test_commit(commit)
            except Exception as ex:
              log_general(_(u'Error al ejecutar testeo vía plugin: %s: %s') % (plugin_reglas[tmp_key].nombre, ex.message), line + '\n\n' + str(ex), nivel=LOG_GENERAL_NIVEL_ERROR)
              return

        except Exception as ex:
          log_general(_(u'Error al procesar commit: %s: %s') % (rama.rama, ex.message), line + '\n\n' + str(ex), nivel=LOG_GENERAL_NIVEL_ERROR)
          return

      # si hubieron actualizaciones (commits), ejecutar test general de la rama
      if rama_actualizada:
        for tmp_key in plugin_objs:
          try:
            plugin_objs[tmp_key].test_branch(rama.repositorio.ruta_local)
          except Exception as ex:
            log_general(_(u'Error al ejecutar testeo vía plugin: %s: %s') % (rama.repositorio.ruta_local, ex.message), str(ex), nivel=LOG_GENERAL_NIVEL_ERROR)
            return

      # procesados los commits y la rama, plugins generaron alertas?
      test_results_mail = ''
      for tmp_key in plugin_objs.keys():
        tmp_test_results = plugin_objs[tmp_key]._get_test_results()
        if tmp_test_results != '':
          log_general(_(u'Se registrará alerta: %s: %s') % (rama.rama, plugin_reglas[tmp_key].nombre))
          Alerta.objects.create(rama=rama, mensaje=_(u'regla de análisis').upper() + ': ' + plugin_reglas[tmp_key].nombre, descripcion=tmp_test_results, criticidad=plugin_reglas[tmp_key].criticidad_regla)
          if test_results_mail != '':
            test_results_mail = test_results_mail + '\n\n'
          test_results_mail = test_results_mail + _(u'repositorio').upper() + ': ' + rama.repositorio.url + '\n'
          test_results_mail = test_results_mail + _(u'rama o branch').upper() + ': ' + rama.rama + '\n'
          test_results_mail = test_results_mail + _(u'regla de análisis').upper() + ': ' + plugin_reglas[tmp_key].nombre + '\n'
          test_results_mail = test_results_mail + _(u'configuración').upper() + ': ' + plugin_reglas_conf[tmp_key].configuracion + '\n\n'
          test_results_mail = test_results_mail + tmp_test_results

      if test_results_mail != '':
        for analista in rama.repositorio.proyecto_software.analistas.all():
          analista_asignado = AnalistaAsignado.objects.get(proyecto_software=rama.repositorio.proyecto_software, analista=analista)
          if analista_asignado.recibe_emails:
            log_general(_(u'Se enviará mail a: %s') % analista.email)
            try:
              send_mail(_(u'AAP - Aviso de alerta'), test_results_mail, settings.EMAIL_HOST_USER + '@' + settings.EMAIL_HOST, [analista.email], fail_silently=False)
            except Exception as ex:
              log_general(_(u'Error al enviar mail: %s: %s') % (analista.email, ex.message), str(ex), nivel=LOG_GENERAL_NIVEL_ERROR)

      # registrar hash de último commit y fecha de último análisis
      (stdout, stderr, ret) = ejecutar('git log -n 1 --pretty=format:"%%H" %s' % rama.rama, rama.repositorio.ruta_local)
      if ret != 0:
        log_general(_(u'Error al recuperar último commit de %s') % rama.rama, stderr, nivel=LOG_GENERAL_NIVEL_ERROR)
        return
      rama.hash_ult_commit = stdout.strip()
      rama.fechahora_ult_analisis = timezone.now()
      rama.save()

      # rama procesada
      log_general(_(u'Rama %s del repositorio %s procesada.') % (rama.rama, rama.repositorio.url), 'commits #: ' + str(len(lines)))

    # fin del proceso
    log_general(_(u'Proceso cron finalizado.'))


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

def log_general(log, detalle='', nivel=LOG_GENERAL_NIVEL_INFO):
  """
  Función para el logueo general
  """

  log = 'CRON: ' + log
  if CRON_DEBUG:
    if detalle is None or detalle == '':
      detalle = "-"
    print str(datetime.now()) + ': ' + log + ': ' + detalle
  LogGeneral.objects.create(fechahora=datetime.now(), log=log, detalle=detalle, nivel=nivel)

# -----------------------------------------------------------------------------

def ejecutar(cmd, cwd='/tmp'):
  """
  Función para la ejecución de comandos a sistema
  """

  args = shlex.split(cmd)
  p = subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  (stdout, stderr) = p.communicate()
  return (stdout, stderr, p.returncode)

# -----------------------------------------------------------------------------

class PluginAAP(object):
  """
  Definición de clase general para plugins / código de reglas
  """

  def __init__(self, config_string=''):
    self._plugin_config_str = config_string
    self._test_results_str = ''
    try:
      if not self.validate_config_string():
        raise ValueError('validate_config_string(): False')
    except Exception as ex:
      raise ValueError('Plugin config error: ' + ex.message + ': ' + str(ex))

  def _get_test_results(self):
    return self._test_results_str

  def get_config_string(self):
    return self._plugin_config_str

  def validate_config_string(self):
    return True

  def test_commit(self, commit_obj=None):
    return

  def test_branch(self, local_path=''):
    return

  def add_test_result(self, test_result_str=''):
    if self._test_results_str != '':
      self._test_results_str = self._test_results_str + '\n'
    self._test_results_str = self._test_results_str + test_result_str
    return

class CommitAAP(object):
  """
  Definición de clase para describir un "commit"
  """

  def __init__(self,
               commit_hash='',
               commit_abbr_hash='',
               commit_parent_hash='',
               commit_author='',
               commit_committer='',
               commit_author_email='',
               commit_committer_email='',
               commit_author_date='',
               commit_committer_date='',
               commit_subject='',
               commit_body='',
               commit_notes='',
               commit_files='',
               commit_patches='',
               commit_branch='',
               commit_diff_branch='',
               commit_local_path=''):
    self.hash = commit_hash
    self.abbr_hash = commit_abbr_hash
    self.parent_hash = commit_parent_hash
    self.author = commit_author
    self.committer = commit_committer
    self.author_email = commit_author_email
    self.committer_email = commit_committer_email
    self.author_date = dateutil.parser.parse(commit_author_date)
    self.committer_date = dateutil.parser.parse(commit_committer_date)
    self.subject = commit_subject
    self.body = commit_body
    self.notes = commit_notes
    #self.files = commit_files.splitlines()[1:]
    self.files = commit_files.splitlines()

    self.patches = commit_patches
    self.branch = commit_branch
    self.diff_branch = commit_diff_branch
    self.local_path = commit_local_path


# -----------------------------------------------------------------------------

