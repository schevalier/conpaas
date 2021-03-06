# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

from os import chown
from pwd import getpwnam
from os.path import join, devnull, lexists
from subprocess import Popen, PIPE
from Cheetah.Template import Template
from conpaas.core.log import create_logger
from conpaas.core.misc import run_cmd
import time

S_INIT        = 'INIT'
S_STARTING    = 'STARTING'
S_RUNNING     = 'RUNNING'
S_STOPPING    = 'STOPPING'
S_STOPPED     = 'STOPPED'

logger = create_logger(__name__)

MRC_STARTUP = None
DIR_STARTUP = None
OSD_STARTUP = None
OSD_REMOVE = None
ETC = None

def init(config_parser):
    global MRC_STARTUP,DIR_STARTUP,OSD_STARTUP,OSD_REMOVE,XTREEM_TMPL
    MRC_STARTUP = config_parser.get('mrc','MRC_STARTUP')
    DIR_STARTUP = config_parser.get('dir','DIR_STARTUP')
    OSD_STARTUP = config_parser.get('osd','OSD_STARTUP')
    OSD_REMOVE  = config_parser.get('osd','OSD_REMOVE')
    global ETC
    ETC = config_parser.get('agent','ETC')

class DIR():
    def __init__(self, uuid):
        self.state = S_INIT         
        self.start_args = [DIR_STARTUP,'start']
        self.stop_args = [DIR_STARTUP, 'stop']
        self.config_template = join(ETC,'dirconfig.properties')
        logger.info('DIR server initialized.')
        self.uuid = uuid
        self.configure()
        self.start()

    def start(self):
        self.state = S_STARTING
        devnull_fd = open(devnull,'w')
        proc = Popen(self.start_args, stdout = devnull_fd, stderr = devnull_fd, close_fds = True)
        if proc.wait() != 0:
            logger.critical('Failed to start DIR service:(code=%d)' %proc.returncode)
        logger.info('DIR Service started.') 
        self.state = S_RUNNING

    def stop(self):
        if self.state == S_RUNNING:
            self.state = S_STOPPING
            devnull_fd = open(devnull,'w')
            # stop MRC
            proc = Popen(self.stop_args, stdout = devnull_fd, stderr = devnull_fd, close_fds = True)
            if proc.wait() != 0:
                logger.critical('Failed to stop DIR service:(code=%d)' %proc.returncode)
            logger.info('DIR Service stopped.') 
            self.state = S_STOPPED
        else:
            logger.warning('Request to stop DIR service while it is not running')      

    def configure(self):
        self._write_config()

    def _write_config(self):
        tmpl = open(self.config_template).read()
        template = Template(tmpl,{
                            'uuid' : self.uuid
                        })
        conf_fd = open('/etc/xos/xtreemfs/dirconfig.properties','w')
        conf_fd.write(str(template))
        conf_fd.close()

class MRC:
    def __init__(self, dir_serviceHost, uuid):
        self.state = S_INIT         
        self.start_args = [MRC_STARTUP,'start']        
        self.stop_args = [MRC_STARTUP, 'stop']
        self.config_template = join(ETC,'mrcconfig.properties')
        logger = create_logger(__name__)
        logger.info('MRC server initialized.')
        self.uuid = uuid
        self.configure(dir_serviceHost)
        self.start()

    def start(self):
        self.state = S_STARTING
        devnull_fd = open(devnull,'w')
        proc = Popen(self.start_args, stdout = devnull_fd, stderr = devnull_fd, close_fds = True)
        if proc.wait() != 0:
            logger.critical('Failed to start mrc service:(code=%d)' %proc.returncode)
        logger.info('MRC Service started.') 
        self.state = S_RUNNING
    
    def stop(self):
        if self.state == S_RUNNING:
            self.state = S_STOPPING
            devnull_fd = open(devnull,'w')
            # stop MRC
            proc = Popen(self.stop_args, stdout = devnull_fd, stderr = devnull_fd, close_fds = True)
            if proc.wait() != 0:
                logger.critical('Failed to stop mrc service:(code=%d)' %proc.returncode)
            logger.info('MRC Service stopped.') 
            self.state = S_STOPPED
        else:
            logger.warning('Request to stop MRC service while it is not running')      
        
    def configure(self, dir_serviceHost):
        self.dir_serviceHost = dir_serviceHost    
        self._write_config()
        
    def _write_config(self):
        tmpl = open(self.config_template).read()
        template = Template(tmpl,{
                            'dir_serviceHost' : self.dir_serviceHost,
                            'uuid' : self.uuid
                        })
        conf_fd = open('/etc/xos/xtreemfs/mrcconfig.properties','w')
        conf_fd.write(str(template))
        conf_fd.close()

class OSD:
    def __init__(self, dir_serviceHost, uuid, mkfs):
        self.state = S_INIT         
        self.uuid = uuid
        self.dir_serviceHost = dir_serviceHost
        self.config_template = join(ETC, 'osdconfig.properties')
        self.dir_servicePort = 32638
        self.dev_name = "/dev/sdb"
        self.mount_point = "/media/xtreemfs-objs"

        # To be filled once we get a dev_name
        self.prepare_args = [] 
        self.mount_args = [] 

#        self.mkdir_args = ['mkdir', '-p', self.mount_point]
        self.mkdir_cmd = "mkdir -p %s" % self.mount_point
        self.umount_args = ['umount', self.mount_point]
        self.start_args = [OSD_STARTUP, 'start']
        self.stop_args = [OSD_STARTUP, 'stop']
        self.remove_args = [OSD_REMOVE, '-dir ' + str(self.dir_serviceHost) + ':' + str(self.dir_servicePort), 'uuid:' + str(self.uuid)]
        self._write_config()
        logger.info('OSD server initialized.')
        self.start(mkfs)

    def start(self, mkfs):
        self.state = S_STARTING
        devnull_fd = open(devnull,'w')
        # waiting for our block device to be available
        dev_found = False

        for attempt in range(1, 11):
            logger.info("OSD node waiting for block device %s" % self.dev_name)
            if lexists(self.dev_name):
                dev_found = True
                break
            else:
                # On EC2 the device name gets changed 
                # from /dev/sd[a-z] to /dev/xvd[a-z]
                self.dev_name = self.dev_name.replace('sd', 'xvd')
                if lexists(self.dev_name):
                    dev_found = True
                    break
                else:
                    self.dev_name = self.dev_name.replace('xvd', 'sd')

            time.sleep(10)

        # create mount point
        run_cmd(self.mkdir_cmd)

        if dev_found:
            logger.info("OSD node has now access to %s" % self.dev_name)

            # prepare block device
            if mkfs:
                logger.info("Creating new file system on %s" % self.dev_name)
                self.prepare_args = ['mkfs.ext4', '-q', '-m0', self.dev_name]
                proc = Popen(self.prepare_args, stdin=PIPE, stdout=devnull_fd,
                        stderr=devnull_fd, close_fds=True)

                proc.communicate(input="y") # answer interactive question with y
                if proc.wait() != 0:
                    logger.critical('Failed to prepare storage device:(code=%d)' %
                            proc.returncode)
                else:
                    logger.info('File system created successfully')
            else:
                logger.info(
                  "Not creating a new file system on %s" % self.dev_name)
                time.sleep(10)

            # mount
            self.mount_args = ['mount', self.dev_name, self.mount_point]
            mount_cmd = ' '.join(self.mount_args)
            logger.debug('Running command %s' % mount_cmd)
            _, err = run_cmd(mount_cmd)

            if err:
                logger.critical('Failed to mount storage device: %s' % err)
            else:
                logger.info("OSD node has prepared and mounted %s" % self.dev_name)
        else:
            logger.critical("Block device %s unavailable, falling back to image space" 
                    % self.dev_name)

        # must be owned by xtreemfs:xtreemfs
        xtreemfs_user = getpwnam("xtreemfs")
        chown(self.mount_point, xtreemfs_user.pw_uid, xtreemfs_user.pw_gid)

        logger.debug(str(self.start_args))

        devnull_fd = open(devnull,'w')
        proc = Popen(self.start_args, stdout = devnull_fd, stderr = devnull_fd, close_fds = True)
        if proc.wait() != 0:
            logger.critical('Failed to start osd service:(code=%d)' %proc.returncode)
        logger.info('OSD Service started.') 
        self.state = S_RUNNING

    def _write_config(self):
        tmpl = open(self.config_template).read()
        template = Template(tmpl,{
                            'dir_serviceHost' : self.dir_serviceHost,
                            'uuid' : self.uuid,
                            'object_dir' : self.mount_point
                        })
        conf_fd = open('/etc/xos/xtreemfs/osdconfig.properties','w')
        conf_fd.write(str(template))
        conf_fd.close()

    def stop(self, drain = True):
        if self.state == S_RUNNING:
            self.state = S_STOPPING
            devnull_fd = open(devnull,'w')
            if drain:
                # remove (drain) OSD to avoid data loss
                logger.info('OSD Service remove commandline: ' + str(self.remove_args))
                logger.info('OSD Service stop commandline: ' + str(self.stop_args))  
                proc = Popen(self.remove_args, stdout = devnull_fd, stderr = devnull_fd, close_fds = True)
                if proc.wait() != 0:
                    logger.critical('Failed to remove OSD service:(code=%d)' %proc.returncode)
                logger.info('OSD Service removed.') 
            # stop OSD
            proc = Popen(self.stop_args, stdout = devnull_fd, stderr = devnull_fd, close_fds = True)
            if proc.wait() != 0:
                logger.critical('Failed to stop OSD service:(code=%d)' %proc.returncode)
            logger.info('OSD Service stopped.') 
            # unmount storage block device
            proc = Popen(self.umount_args, stdout = devnull_fd, stderr = devnull_fd, close_fds = True)
            if proc.wait() != 0:
                logger.critical('Failed to unmount storage device:(code=%d)' %proc.returncode)
            logger.info('Storage block device unmounted.') 

            self.state = S_STOPPED
        else:
            logger.warning('Request to stop OSD service while it is not running')      

