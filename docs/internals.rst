=========
Internals
=========

A ConPaaS service may consist of three main entities: the manager, the
agent and the frontend. The (primary) manager resides in the first VM
that is started by the frontend when the service is created and its role
is to manage the service by providing supporting agents, maintaining a
stable configuration at any time and by permanently monitoring the
service’s performance. An agent resides on each of the other VMs that
are started by the manager. The agent is the one that does all the work.
Note that a service may contain one manager and multiple agents, or
multiple managers that also act as agents.

To implement a new ConPaaS service, you must provide a new manager
service, a new agent service and a new frontend service (we assume that
each ConPaaS service can be mapped on the three entities architecture).
To ease the process of adding a new ConPaaS service, we propose a
framework which implements common functionality of the ConPaaS services.
So far, the framework provides abstraction for the IaaS layer (adding
support for a new cloud provider should not require modifications in any
ConPaaS service implementation) and it also provides abstraction for the
HTTP communication (we assume that HTTP is the preferred protocol for
the communication between the three entities).

ConPaaS directory structure
---------------------------

You can see below the directory structure of the ConPaaS software. The
*core* folder under *src* contains the ConPaaS framework. Any service
should make use of this code. It contains the manager http server, which
instantiates the python manager class that implements the required
service; the agent http server that instantiates the python agent class
(if the service requires agents); the IaaS abstractions and other useful
code.

A new service should be added in a new python module under the
*ConPaaS/src/services* folder.

In the next paragraphs we describe how to add the new ConPaaS service.

Service’s name
==============

The first step in adding a new ConPaaS service is to choose a name for
it. This name will be used to construct, in a standardized manner, the
file names of the scripts required by this service (see below).
Therefore, the names should not contain spaces, nor unaccepted
characters.

Scripts
=======

To function properly, ConPaaS uses a series of configuration files and
scripts. Some of them must be modified by the administrator, i.e. the
ones concerning the cloud infrastructure, and the others are used,
ideally unchanged, by the manager and/or the agent. A newly added
service would ideally function with the default scripts. If, however,
the default scripts are not satisfactory (for example the new service
would need to start something on the VM, like a memcache server) then
the developers must supply a new script/config file, that would be used
instead of the default one. This new script’s name must be preceded by
the service’s chosen name (as described above) and will be selected by
the frontend at run time to generate the contextualization file for the
manager VM. (If the frontend doesn’t find such a script/config file for
a given service, then it will use the default script). **Note that some
scripts provided for a service do not replace the default ones, instead
they will be concatenated to them (see below the agent and manager
configuration scripts).**

Below we give an explanation of the scripts and configuration files used
by a ConPaaS service (there are other configuration files used by the
frontend but these are not relevant to the ConPaaS service). Basically
there are two scripts that a service uses to boot itself up - the
manager contextualization script, which is executed after the manager VM
booted, and the agent contextualization script, which is executed after
the agent VM booted. These scripts are composed of several parts, some
of which are customizable to the needs of the new service.

In the ConPaaS home folder (CONPAAS\_HOME) there is the *config* folder
that contains configuration files in the INI format and the *scripts*
folder that contains executable bash scripts. Some of these files are
specific to the cloud, other to the manager and the rest to the agent.
These files will be concatenated in a single contextualization script,
as described below.

-  Files specific to the Cloud:

   (1) CONPAAS\_HOME/config/cloud/\ *cloud\_name*.cfg, where
   *cloud\_name* refers to the clouds supported by the system (for now
   OpenNebula and EC2). So there is one such file for each cloud the
   system supports. These files are filled in by the administrator. They
   contain information such as the username and password to access the
   cloud, the OS image to be used with the VMs, etc. These files are
   used by the frontend and the manager, as both need to ask the cloud
   to start VMs.

   (2) CONPAAS\_HOME/scripts/cloud/\ *cloud\_name*, where *cloud\_name*
   refers to the clouds supported by the system (for now OpenNebula and
   EC2). So, as above, there is one such file for each cloud the system
   supports. These scripts will be included in the contextualization
   files. For example, for OpenNebula, this file sets up the network.

-  Files specific to the Manager:

   (3) CONPAAS\_HOME/scripts/manager/manager-setup, which prepares the
   environment by copying the ConPaaS source code on the VM, unpacking
   it, and setting up the PYTHONPATH environment variable.

   (4) CONPAAS\_HOME/config/manager/\ *service\_name*-manager.cfg, which
   contains configuration variables specific to the service manager (in
   INI format). If the new service needs any other variables (like a
   path to a file in the source code), it should provide an annex to the
   default manager config file. This annex must be named
   *service\_name*-manager.cfg and will be concatenated to
   default-manager.cfg

   (5) CONPAAS\_HOME/scripts/manager/\ *service\_name*-manager-start,
   which starts the server manager and any other programs the service
   manager might use.

   (6) CONPAAS\_HOME/sbin/manager/\ *service\_name*-cpsmanager (will be
   started by the *service\_name*-manager-start script), which starts
   the manager server, which in turn will start the requested manager
   service.

   Scripts (1), (2), (3), (4) and (5) will be used by the frontend to
   generate the contextualization script for the manager VM. After this
   scripts executes, a configuration file containing the concatenation
   of (1) and (4) will be put in ROOT\_DIR/config.cfg and then (6) is
   started with the config.cfg file as a parameter that will be
   forwarded to the new service.

   Examples:

-  Files specific to the Agent

   They are similar to the files described above for the manager, but
   this time the contextualization file is generated by the manager.

Scripts and config files directory structure
--------------------------------------------

Below you can find the directory structure of the scripts and
configuration files described above.

Implementing a new ConPaaS service
==================================

In this section we describe how to implement a new ConPaaS service by
providing an example which can be used as a starting point. The new
service is called *helloworld* and will just generate helloworld
strings. Thus, the manager will provide a method, called get\_helloworld
which will ask all the agents to return a ’helloworld’ string (or
another string chosen by the manager).

We will start by implementing the agent. We will create a class, called
HelloWorldAgent, which implements the required method - get\_helloworld,
and put it in *conpaasservices/helloworld/agent/agent.py* (Note: make
the directory structure as needed and providing empty \_\_init\_\_.py to
make the directory be recognized as a module path). As you can see in
Listing [lst:helloworldagent], this class uses some functionality
provided in the conpaas.core package. The conpaas.core.expose module
provides a python decorator (@expose) that can be used to expose the
http methods that the agent server dispatches. By using this decorator,
a dictionary containing methods for http requests GET, POST or UPLOAD is
filled in behind the scenes. This dictionary is used by the built-in
server in the conpaas.core package to dispatch the HTTP requests. The
module conpaas.core.http contains some useful methods, like
HttpJsonResponse and HttpErrorResponse that are used to respond to the
HTTP request dispatched to the corresponding method. In this class we
also implemented a method called startup, which only changes the state
of the agent. This method could be used, for example, to make some
initializations in the agent. We will describe later the use of the
other method, check\_agent\_process.

Let’s assume that the manager wants each agent to generate a different
string. The agent should be informed about the string that it has to
generate. To do this, we could either implement a method inside the
agent, that will receive the required string, or specify this string in
the configuration file with which the agent is started. We opted for the
second method just to illustrate how a service could make use of the
config files and also, maybe some service agents/managers need some
information before having been started.

Therefore, we will provide the *helloworld-agent.cfg* file (see
Listing [lst:helloworldcfg]) that will be concatenated to the
default-manager.cfg file. It contains a variable ($STRING) which will be
replaced by the manager.

Now let’s implement an http client for this new agent server. See
Listing [lst:helloworldagentclient]. This client will be used by the
manager as a wrapper to easily send requests to the agent. We used some
useful methods from conpaas.core.http, to send json objects to the agent
server.

Next, we will implement the manager in the same manner: we will write
the *HelloWorldManager* class and place it in the file
*conpaas/services/helloworld/manager/manager.py*. To make use of the
IaaS abstractions, we need to instantiate a Controller which controls
all the requests to the clouds on which ConPaaS is running. Note the
lines:

::

    1: self.controller = Controller( config_parser)
    2: self.controller.generate_context('helloworld')

The first line instantiates a Controller. The controller maintains a
list of cloud objects generated from the *config\_parser* file. There
are several functions provided by the controller which are documented in
the doxygen documentation of file *controller.py*. The most important
ones, which are also used in the Hello World service implementation,
are: *generate\_context* (which generates a template of the
contextualization file); *update\_context* (which takes the
contextualization template and replaces the variables with the supplied
values); *create\_nodes* (which asks for additional nodes from the
specified cloud or the default one) and *delete\_nodes* (which deletes
the specified nodes).

Note that the *create\_nodes* function accepts as a parameter a function
(in our case *check\_agent\_process*) that tests if the agent process
started correctly in the agent VM. If an exception is generated during
the calls to this function for a given period of time, then the manager
assumes that the agent process didn’t start correctly and tries to start
the agent process on a different agent VM.

We can also implement a client for the manager server (see
Listing [lst:helloworldmanagerclient]). This will allow us to use the
command line interface to send requests to the manager, if the frontend
integration is not available.

The last step is to register the new service to the conpaas core. One
entry must be added to file *conpaas/core/services.py*, as it is
indicated in Listing [lst:helloworldservices]. Because the java and php
services use the same code for the agent, there is only one entry in the
agent services, called *web* which is used by both webservices.

Integrating the new service with the frontend
=============================================

So far there is no easy way to add a new frontend service. Each service
may require distinct graphical elements. In this section we explain how
the Hello World frontend service has been created.

Manager states
--------------

As you have noticed in the Hello World manager implementation, we used
some standard states, e.g. INIT, ADAPTING, etc. By calling the
*get\_service\_info* function, the frontend knows in which state the
manager is. Why do we need these standardized stated? As an example, if
the manager is in the ADAPTING state, the frontend would know to draw a
loading icon on the interface and keep polling the manager.

Files to be modified
--------------------

Several lines of code must be added to the two files above for the new
service to be recognized. If you look inside these files, you’ll see
that knowing where to add the lines and what lines to add is
self-explanatory.

Files to be added
-----------------

