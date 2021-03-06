#!/bin/bash -e

# This script generates a VM image for ConPaaS, to be used for OpenNebula with Xen.
# The script should be run on a Debian or Ubuntu system.
# Before running this script, please make sure that you have the following
# packages / commmands available:

# mount debootstrap chroot umount svn pygrub

##### TO CUSTOMIZE: #####

# The hostname of the VM and the directory in which the image files will be generated.
HOSTNAME=conpaastest-xen
OUTPUT_DIR=/home/cstratan/xen2

# The size of the image file.
FILESIZE=2048 #MB

# The Debian distribution that you wish to install, and the target architecture.
DEBIAN_DIST=squeeze
ARCH=i386

# Choosing a custom kernel version is not supported yet for Xen.
# KERNEL_VERSION=2.6.32-5-686

#########################

# Function for displaying highlighted messages.
function cecho() {
  echo -en "\033[1m"
  echo -n "#" $@
  echo -e "\033[0m"
}

if [ `id -u` -ne 0 ]; then
  cecho 'need root permissions for this script';
  exit 1;
fi

ROOT_DIR=`mktemp -d`
cecho "Using $ROOT_DIR as mount point"

cecho "Creating XEN disk image"
xen-create-image --output $OUTPUT_DIR --hostname $HOSTNAME --dist $DEBIAN_DIST --arch $ARCH --size=${FILESIZE}Mb --pygrub --dir $OUTPUT_DIR --dhcp

cecho "Mounting disk image"
mount -o loop ${OUTPUT_DIR}/domains/${HOSTNAME}/disk.img $ROOT_DIR

cecho "Writing /etc/network/interfaces"
cat <<EOF > $ROOT_DIR/etc/network/interfaces
auto lo
iface lo inet loopback
auto eth0
iface eth0 inet static
EOF
cecho "Removing udev persistent rules"
rm -f $ROOT_DIR/etc/udev/rules.d/70-persistent*

cecho "Mounting /proc in chroot"
#mount -obind /dev $ROOT_DIR/dev
mount -t proc proc $ROOT_DIR/proc

cecho "Running apt-get update"
chroot $ROOT_DIR /bin/bash -c 'apt-get -y update'

# disable auto start after package install
cat <<EOF > $ROOT_DIR/usr/sbin/policy-rc.d
#!/bin/sh
exit 101
EOF
chmod 755 $ROOT_DIR/usr/sbin/policy-rc.d

# Generate a script that will install the dependencies in the system. 
cat <<EOF > $ROOT_DIR/conpaas_install
#!/bin/bash
# set root passwd
echo "root:contrail" | chpasswd

# fix apt sources
sed --in-place 's/main/main contrib non-free/' /etc/apt/sources.list

# install dependencies
apt-get -f -y update
# pre-accept sun-java6 licence
echo "debconf shared/accepted-sun-dlj-v1-1 boolean true" | debconf-set-selections
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --no-install-recommends --no-upgrade \
        install openssh-server \
        python python-pycurl python-cheetah nginx \
        tomcat6-user memcached \
        make gcc g++ sun-java6-jdk erlang ant libxslt1-dev yaws subversion
update-rc.d -f memcached remove
update-rc.d -f nginx remove
update-rc.d -f yaws remove

# add dotdeb repo for php fpm
echo "deb http://packages.dotdeb.org stable all" >> /etc/apt/sources.list
wget -O - http://www.dotdeb.org/dotdeb.gpg 2>/dev/null | apt-key add -
apt-get -f -y update
apt-get -f -y --no-install-recommends --no-upgrade install php5-fpm php5-curl \
              php5-mcrypt php5-mysql php5-odbc \
              php5-pgsql php5-sqlite php5-sybase php5-xmlrpc php5-xsl \
              php5-adodb php5-memcache
update-rc.d -f php5-fpm remove
# remove dotdeb repo
sed --in-place 's%deb http://packages.dotdeb.org stable all%%' /etc/apt/sources.list
apt-get -f -y update

# create directory structure
echo > /var/log/cpsagent.web.log
mkdir /etc/cpsagent.web/
mkdir /var/tmp/cpsagent.web/
mkdir /var/run/cpsagent.web/
mkdir /var/cache/cpsagent.web/
echo > /var/log/cpsmanager.web.log
mkdir /etc/cpsmanager.web/
mkdir /var/tmp/cpsmanager.web/
mkdir /var/run/cpsmanager.web/
mkdir /var/cache/cpsmanager.web/

# add cloudera repo for hadoop
echo "deb http://archive.cloudera.com/debian $DEBIAN_DIST-cdh3 contrib" >> /etc/apt/sources.list
wget -O - http://archive.cloudera.com/debian/archive.key 2>/dev/null | apt-key add -
apt-get -f -y update
apt-get -f -y --no-install-recommends --no-upgrade install \
  hadoop-0.20 hadoop-0.20-namenode hadoop-0.20-datanode \
  hadoop-0.20-secondarynamenode hadoop-0.20-jobtracker  \
  hadoop-0.20-tasktracker hadoop-pig hue-common  hue-filebrowser \
  hue-jobbrowser hue-jobsub hue-plugins dnsutils
update-rc.d -f hadoop-0.20-namenode remove
update-rc.d -f hadoop-0.20-datanode remove
update-rc.d -f hadoop-0.20-secondarynamenode remove
update-rc.d -f hadoop-0.20-jobtracker remove
update-rc.d -f hadoop-0.20-tasktracker remove
update-rc.d -f hue remove
# create a default config dir
mkdir -p /etc/hadoop-0.20/conf.contrail
update-alternatives --install /etc/hadoop-0.20/conf hadoop-0.20-conf /etc/hadoop-0.20/conf.contrail 99
# remove cloudera repo
sed --in-place 's%deb http://archive.cloudera.com/debian $DEBIAN_DIST-cdh3 contrib%%' /etc/apt/sources.list
apt-get -f -y update


# add scalaris repo
echo "deb http://download.opensuse.org/repositories/home:/scalaris/Debian_6.0 /" >> /etc/apt/sources.list
wget -O - http://download.opensuse.org/repositories/home:/scalaris/Debian_6.0/Release.key 2>/dev/null | apt-key add -
apt-get -f -y update
apt-get -f -y --no-install-recommends --no-upgrade install scalaris screen
update-rc.d -f scalaris remove
# remove scalaris repo
sed --in-place 's%deb http://download.opensuse.org/repositories/home:/scalaris/Debian_6.0 /%%' /etc/apt/sources.list
apt-get -f -y update


# add xtreemfs repo
echo "deb http://download.opensuse.org/repositories/home:/xtreemfs:/unstable/Debian_6.0 /" >> /etc/apt/sources.list
wget -O - http://download.opensuse.org/repositories/home:/xtreemfs:/unstable/Debian_6.0/Release.key 2>/dev/null | apt-key add -
apt-get -f -y update
apt-get -f -y --no-install-recommends --no-upgrade install xtreemfs-server xtreemfs-client
update-rc.d -f xtreemfs-osd remove
update-rc.d -f xtreemfs-mrc remove
update-rc.d -f xtreemfs-dir remove
# remove xtreemfs repo
sed --in-place 's%deb http://download.opensuse.org/repositories/home:/xtreemfs:/unstable/Debian_6.0 /%%' /etc/apt/sources.list
apt-get -f -y update


apt-get -f -y clean
exit 0
EOF

# Execute the script for installing the dependencies.
chmod a+x $ROOT_DIR/conpaas_install
chroot $ROOT_DIR /bin/bash /conpaas_install
rm -f $ROOT_DIR/conpaas_install

rm -f $ROOT_DIR/usr/sbin/policy-rc.d

##### TO CUSTOMIZE: #####
# This part is for OpenNebula contextualization. The contextualization scripts (and possibly
# other necessary files) will be provided through OpenNebula to the VM as an ISO image.
# We need to mount this image and execute the contextualization scripts. You might need
# to change the dev file associated with the CD-ROM inside your virtual machine from
# "/dev/xvdb" to something else (depending on your operating system and on the virtualization 
# software, it can be /dev/hdb, /dev/sdb etc.). You can check this in a VM that is already running
# in your OpenNebula system and that has been configured with contextualization.

cat <<"EOF" > $ROOT_DIR/etc/rc.local
#!/bin/sh
mount -t iso9660 /dev/xvdb /mnt
 
if [ -f /mnt/context.sh ]; then
  . /mnt/context.sh
  if [ -n "$USERDATA" ]; then
    echo "$USERDATA" | /usr/bin/xxd -p -r | /bin/sh
  elif [ -e /mnt/init.sh ]; then
    . /mnt/init.sh
  fi
fi
 
umount /mnt

exit 0
EOF

cecho "Umounting proc"
#umount $ROOT_DIR/dev
umount $ROOT_DIR/proc
sleep 1s
cecho "Umounting $ROOT_DIR"
umount $ROOT_DIR
sleep 1s
rm -r $ROOT_DIR
cecho "Done"

