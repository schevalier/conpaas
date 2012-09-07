#!/usr/bin/python
'''
Copyright (c) 2010-2012, Contrail consortium.
All rights reserved.

Redistribution and use in source and binary forms, 
with or without modification, are permitted provided
that the following conditions are met:

 1. Redistributions of source code must retain the
    above copyright notice, this list of conditions
    and the following disclaimer.
 2. Redistributions in binary form must reproduce
    the above copyright notice, this list of 
    conditions and the following disclaimer in the
    documentation and/or other materials provided
    with the distribution.
 3. Neither the name of the Contrail consortium nor the
    names of its contributors may be used to endorse
    or promote products derived from this software 
    without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.


Created on Mar 29, 2011

@author: ielhelw
'''

from optparse import OptionParser
import sys, time, urlparse
from inspect import isfunction
from os import environ 

try:
  from conpaas.core import https
  from conpaas.services.webservers.manager import client
except ImportError as e:
  print >>sys.stderr, 'Failed to locate conpaas modules'
  print >>sys.stderr, e
  sys.exit(1)


def get_service_info(args):
  '''Get the state of a deployment'''
  parser = OptionParser(usage='get_service_info')
  _, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.get_service_info(host, port)
    print 'service type:', response['type']
    print 'state:', response['state']

def get_service_history(args):
  '''Get the state change history of a deployment'''
  parser = OptionParser(usage='get_service_history')
  _, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.get_service_history(host, port)
    if response['state_log']:
      for state in response['state_log']:
        print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(state['time'])), state['state'], state['reason']
    else:
      print 'No changes in history'

def startup(args):
  '''Startup a deployment'''
  parser = OptionParser(usage='startup')
  _, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.startup(host, port)
    print response['state']

def shutdown(args):
  '''Shutdown a deployment'''
  parser = OptionParser(usage='shutdown')
  _, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.shutdown(host, port)
    print response['state']

def add_nodes(args):
  '''Add more service nodes to a deployment'''
  parser = OptionParser(usage='add_nodes')
  parser.add_option('-p', '--proxy', dest='proxy', type='int', default=0)
  parser.add_option('-w', '--web', dest='web', type='int', default=0)
  parser.add_option('-b', '--backend', dest='backend', type='int', default=0)
  opts, pargs = parser.parse_args(args)
  if pargs\
  or (opts.proxy == 0 and opts.web == 0 and opts.backend == 0)\
  or opts.proxy < 0 or opts.web < 0 or opts.backend < 0:
    parser.print_help()
  else:
    response = client.add_nodes(host, port, proxy=opts.proxy, web=opts.web, backend=opts.backend)

def remove_nodes(args):
  '''Remove some service nodes from a deployment'''
  parser = OptionParser(usage='remove_nodes')
  parser.add_option('-p', '--proxy', dest='proxy', type='int', default=0)
  parser.add_option('-w', '--web', dest='web', type='int', default=0)
  parser.add_option('-b', '--backend', dest='backend', type='int', default=0)
  opts, pargs = parser.parse_args(args)
  if pargs\
  or (opts.proxy == 0 and opts.web == 0 and opts.backend == 0)\
  or opts.proxy < 0 or opts.web < 0 or opts.backend < 0:
    parser.print_help()
  else:
    response = client.remove_nodes(host, port, proxy=opts.proxy, web=opts.web, backend=opts.backend)

def list_nodes(args):
  '''Get a list of service nodes'''
  parser = OptionParser(usage='list_nodes')
  _, pargs = parser.parse_args(args)
  if len(pargs) != 0:
    parser.print_help()
  else:
    response = client.list_nodes(host, port)
    print '%-20s %s' % ('Service Node', 'Role(s)')
    all = list(set(response['proxy'] + response['web'] + response['backend']))
    for i in all:
      print '%-20s%s' % (i,
                          (i in response['proxy'] and ' PROXY' or '')
                            + (i in response['web'] and ' WEB' or '')
                            + (i in response['backend'] and ' BACKEND' or ''))

def get_node_info(args):
  '''Get information about a single service node'''
  parser = OptionParser(usage='get_node_info <nodeId>')
  _, pargs = parser.parse_args(args)
  if len(pargs) != 1:
    parser.print_help()
  else:
    response = client.get_node_info(host, port, args[0])
    print '%-20s %-20s %s' % ('Service Node', 'Address', 'Role(s)')
    print '%-20s %-20s' % (response['serviceNode']['id'], response['serviceNode']['ip']),
    if  response['serviceNode']['isRunningProxy']: print 'PROXY',
    if  response['serviceNode']['isRunningWeb']: print 'WEB',
    if  response['serviceNode']['isRunningBackend']: print 'BACKEND',
    print

def list_authorized_keys(args):
  '''Get the list of known SSH keys'''
  parser = OptionParser(usage='list_authorized_keys')
  _, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.list_authorized_keys(host, port)
    keys = response['authorizedKeys']
    print len(keys), "keys found"
    for k in keys:
      print k

def list_code_versions(args):
  '''List identifiers of all code versions stored by a deployment'''
  parser = OptionParser(usage='list_code_versions')
  _, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.list_code_versions(host, port)
    print '%-21s %-20s %-20s %-20s %s' % ('Upload Date', 'Identifier', 'Live', 'Name', 'Description')
    for c in response['codeVersions']:
      print '%-21s %-20s %-20s %-20s %s' % (
        time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(c['time'])),
        c['codeVersionId'],
        ('current' in c and c['current'] and 'YES') or '-',
        c['filename'],
        c['description'])

def upload_code_version(args):
  '''Upload a new code version'''
  parser = OptionParser(usage='upload_code_version <filename>')
  _, pargs = parser.parse_args(args)
  if len(pargs) != 1:
    parser.print_help()
  else:
    response = client.upload_code_version(host, port, args[0])
    print 'codeVersionId:', response['codeVersionId']

def upload_authorized_key(args):
  '''Upload the given SSH public key'''
  parser = OptionParser(usage='upload_authorized_key <filename>')
  _, pargs = parser.parse_args(args)
  if len(pargs) != 1:
    parser.print_help()
  else:
    response = client.upload_authorized_key(host, port, args[0])
    print response['outcome']

def get_configuration(args):
  '''Get the configuration of a deployment'''
  parser = OptionParser(usage='get_configuration')
  _, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.get_configuration(host, port)
    print 'Current codeVersions:', response['codeVersionId']
    print 'PHP configuration:'
    for i in response['phpconf']:
      print '  %s:' % i, response['phpconf'][i]

def update_php_configuration(args):
  '''Update the configuration of a PHP deployment'''
  parser = OptionParser(usage='update_php_configuration')
  parser.add_option('-c', '--code', dest='codeVersionId', type='string', default=None)
  parser.add_option('-p', '--phpconfig', action='append', dest='phpconfig', type='string', default=[], help='Multiple "-p" options can be supplied each of the form "key=value"')
  opts, pargs = parser.parse_args(args)
  php = {}
  for config in opts.phpconfig:
    pair = config.split('=', 1)
    if len(pair) != 2:
      parser.print_help()
      sys.exit(1)
    php[pair[0]] = pair[1]
  if pargs or (not opts.phpconfig and opts.codeVersionId == None):
    parser.print_help()
  else:
    response = client.update_php_configuration(host, port, codeVersionId=opts.codeVersionId, phpconf=php)

def update_java_configuration(args):
  '''Update the configuration of a Java deployment'''
  parser = OptionParser(usage='update_java_configuration')
  parser.add_option('-c', '--code', dest='codeVersionId', type='string', default=None)
  opts, pargs = parser.parse_args(args)
  if pargs or opts.codeVersionId == None:
    parser.print_help()
  else:
    response = client.update_java_configuration(host, port, opts.codeVersionId)

def get_service_performance(args):
  '''Get the average request rate and throughput'''
  parser = OptionParser(usage='get_service_performance')
  _, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.get_service_performance(host, port)
    print 'Avg. Throughput:', response['avg_throughput']
    print 'Avg. Request rate:', response['avg_throughput']
    print 'Avg. Error rate:', response['avg_throughput']

def getLog(args):
  '''Get raw logging'''
  parser = OptionParser(usage='getLog')
  _, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.getLog(host, port)
    print response['log']

def git_push_hook(args):
  parser = OptionParser(usage='git_push_hook')
  _, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.git_push_hook(host, port)
    print "Code version %s successfully uploaded" % response['codeVersionId']

def help(args=[]):
  '''Print the help menu'''
  l = ['add_nodes',
       'get_configuration',
       'get_service_performance',
       'getLog',
       'get_node_info',
       'get_service_info',
       'get_service_history',
       'help',
       'list_authorized_keys',
       'list_code_versions',
       'list_nodes',
       'remove_nodes',
       'shutdown',
       'startup',
       'update_php_configuration',
       'update_java_configuration',
       'upload_code_version',
       'upload_authorized_key']
  l.sort()
  module = sys.modules[__name__]
  l = [ getattr(module, i) for i in l ]
  print 'Usage:', sys.argv[0], 'URL ACTION [options]'
  print
  print 'Action could be one of:'
  print ' %-25s   %s' % ('[ACTION]', '[DESCRIPTION]')
  for func in l:
    print ' %-25s   %s' % (func.__name__, func.__doc__)

if __name__ == '__main__':
  if len(sys.argv) < 3:
    help()
    sys.exit(1)
  
  try:  
    certs_dir = environ['CONPAAS_CERTS_DIR']
  except KeyError: 
    print "Please set the environment variable CONPAAS_CERTS_DIR"
    sys.exit(1)

  try:
      https.client.conpaas_init_ssl_ctx(certs_dir, 'user')
  except Exception as e:
      print e
  
  global host, port
  try:
    url = urlparse.urlparse(sys.argv[1], scheme='http')
    host = url.hostname
    port = url.port or 443 
    if not host: raise Exception()
  except:
    print >>sys.stderr, 'Invalid URL'
    sys.exit(1)

  if hasattr(sys.modules[__name__], sys.argv[2]):
    func = getattr(sys.modules[__name__], sys.argv[2])
    if not isfunction(func):
      help()
      sys.exit(1)
    try:
      func(sys.argv[3:])
    except client.ClientError as e:
      if len(e.args) == 1: print >>sys.stderr, e.args[0]
      else: print >>sys.stderr, e.args[1]
    except Exception as e:
      print >>sys.stderr, e
  else:
    help()
    sys.exit(1)
    