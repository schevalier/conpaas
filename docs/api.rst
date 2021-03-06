=================================
Application Programming Interface
=================================

ConPaaS services are composed by a manager and one or more agents: the
manager’s role is to oversee the functioning of a specific service. ConPaaS
managers are responsible, among other things, for starting up and shutting down
ConPaaS agents, which in turn provide the functionality offered by a specific
service.

ConPaaS services are created and administered exclusively through an HTTP /
JSON Application Programing Interface exposed by a web service called ConPaaS
Director. This document provides a description of such an API.

Python API
==========
.. toctree::
   :maxdepth: 3
   
   api/conpaas.core
   api/conpaas.services
   api/cpsdirector

RESTful API
===========

Let us list the ConPaaS API methods, together with a brief description
of their behavior.

::

    POST /new_user

        Create a new ConPaaS user. The method expects the following parameters:

        'username', 'fname', 'lname', 'email', 'affiliation', 'password', 'credit'
        
        A dictionary of user values is returned upon successful user creation.
        The following dictionary is returned on failure:

        {
         'error': True,
         'msg': 'An explainatory error message' 
        }

    POST /login

        Authenticates the given user. The following parameters are expected:
        'username', 'password'

        A dictionary of user values is returned upon successful authentication.
        False is returned otherwise.

    POST /get_user_certs

        Create and send SSL certificates for the given user. 'username' and
        'password' are the expected parameters. A zip archive containing the SSL
        certificates is returned on success, False otherwise.
        
    GET /available_services

        Return a list of available service types. For example: 
        ['scalaris', 'selenium', 'hadoop', 'mysql', 'java', 'php']

    POST /start/<servicetype>

        Return a dictionary with service data (manager's vmid and IP address,
        service name and ID) in case of correct service creation. False is returned
        otherwise. Only service types returned by the 'available_services' method
        described above are allowed. 

        This method requires the client to present a valid SSL certificate.

    POST /stop/<serviceid>

        Return a boolean value. True in case of proper service termination, false
        otherwise. <serviceid> has to be an integer representing the service id of a
        running service.

        This method requires the client to present a valid SSL certificate.

    POST /rename/<serviceid>

        Rename the given service. The new name 'name' is the only required
        argument. Return true on successful renaming, false otherwise.

    GET  /list

        List running ConPaaS services. Return data as a list of dictionaries
        (associative arrays).

        This method requires the client to present a valid SSL certificate.

    GET  /download/ConPaaS.tar.gz

        Used by ConPaaS services. Download a tarball with the ConPaaS source code.

    POST /callback/decrementUserCredit.php
        
        Used by ConPaaS services. 'sid' and 'decrement' are the required parameters.

        Decrement user credit and check if it is enough.  Return a dictionary with
        the 'error' attribute set to false if the user had enough credit, true
        otherwise.

        This method requires the client to present a valid SSL certificate of type
        'manager'. The 'serviceLocator' field in the supplied certificate has to match
        the 'sid'.

    POST /ca/get_cert.php

        Used by ConPaaS services. The only required argument is a file called 'csr'
        holding a certificate signing request. A certificate is returned.

        This method requires the client to present a valid SSL certificate of type
        'manager'..

The first three methods, namely **new\_user**, **login** and
**get\_user\_certs** do not need a client SSL certificate to be called.

**available\_services**, **start**, **stop**, **rename** and **list**
all need a valid user certificate in order to be called.

The last two methods are used by ConPaaS managers to decrement users’
credit and create agent certificates. They both need a valid manager
certificate to be called.
