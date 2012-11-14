StraitJacket 1.02
=================

This web application is a (hopefully) safe and secure remote execution
environment framework. It builds on top of Linux' AppArmor system calls and as
such won't be able to run on any other operating system.

The end goal is to be able to run someone else's source code in any (configured)
language automatically and not worry about hax.

Design
=====

StraitJacket comes with a number of predetermined AppArmor profiles. When
StraitJacket gets an incoming request to run some code, it will, after calling
fork, but before exec, tell AppArmor that on exec, it wants to switch that
process into a specific profile permanently. AppArmor profiles also provide
standard resource-limit style constraints.

AppArmor really does all the heavy lifting. For more information please see
[AppArmor's wiki](http://wiki.apparmor.net/). A big thanks to Immunix and the
subsequent AppArmor team!

API
===

The API has two calls.

```
GET /info
 * No arguments.
 * This will return, in JSON format, server info, such as what languages are
   currently supported.

POST /execute
 * Takes parameters: language (required), stdin (required, but can be empty),
   source (required), and timelimit (optional, in seconds).
 * Returns, in JSON format, stdout, stderr, exitstatus, time, and error.
```

A sample client library is provided in the samples directory (it's what
[CodeWarden](https://github.com/instructure/codewarden/) uses).

Installation
=====

AMI
-----

If you'd rather just ignore all of the following and use a pre-existing Amazon
Web Services AMI, try looking for ami-8de553e4

Dependencies
-----

You will need to install all of the appropriate files for each language you want
to run. On Ubuntu 12.04, suggested packages include but are not limited to:

gcc, mono-gmcs, g++, guile-1.8, ghc, lua5.1, ocaml, php5, python, ruby,
ruby1.9, scala, racket, golang, openjdk-6-jdk, gfortran

You'll probably want to get nodejs and DMD from elsewhere.
http://dlang.org/download.html
https://github.com/joyent/node/wiki/Installing-Node.js-via-package-manager

Dependencies include:

python-webpy, python-libapparmor, apparmor

Creating AMI from Scratch
=========================

Start with Ubuntu LTS 12.04

Get the codebase from github
****************************
- sudo apt-get update
- sudo apt-get install git
- git clone https://github.com/EliRibble/straitjacket.git

Install apparmor profiles
*************************
- sudo cp -R straitjacket/files/etc/apparmor.d/* /etc/apparmor.d/
- sudo service apparmor reload

Install nginx
*************
- sudo apt-get install nginx
- sudo service nginx start
- At this point you can test that it is working by visiting your
  server with a web browser. You should get the 'Welcome to nginx!' message
- sudo cp -R straitjacket/files/etc/nginx/* /etc/nginx
- sudo rm /etc/nginx/sites-enabled/default
- sudo ln -s /etc/nginx/sites-available/straitjacket /etc/nginx/sites-enabled/
- sudo service nginx reload
- At this point if you test the website it should show a bad gateway

Install uwsgi
*************
- sudo apt-get install uwsgi uwsgi-plugin-python
- sudo cp -R straitjacket/files/etc/uwsgi/* /etc/uwsgi/
- sudo ln -s /etc/uwsgi/apps-available/straitjacket.ini /etc/uwsgi/apps-enabled/

Set up the web app
******************
- sudo apt-get purge apport python-apport
- sudo apt-get install python-pip python-libapparmor
- sudo pip install web.py
- sudo mkdir -p /var/webapps/
- sudo ln -s /home/ubuntu/straitjacket /var/webapps/straitjacket
- sudo service uwsgi restart
- At this point if you test the website you should see the main page but
  no code execution will work

Set up the temp directories
***************************
- sudo mkdir -p /var/local/straitjacket/tmp/source
- sudo mkdir -p /var/local/straitjacket/tmp/compiler
- sudo mkdir -p /var/local/straitjacket/tmp/execute
- sudo chown -R www-data /var/local/straitjacket
- sudo chgrp -R www-data /var/local/straitjacket

Install language support
************************
- sudo pip install pytest
- sudo apt-get install gcc mono-gmcs g++ guile-1.8 ghc lua5.1 ocaml php5 python ruby scala racket golang openjdk-6-jdk gfortran gobjc gnustep gnustep-devel build-essential gnustep-make libgnustep-base-dev tclx ruby1.9.1
- You should be able to run the language tests from the straitjacket directory with 'sudo -u www-data py.test tests/test_languages.py'

Install Clojure support
#######################
- sudo apt-get install unzip
- wget http://repo1.maven.org/maven2/org/clojure/clojure/1.4.0/clojure-1.4.0.zip
- unzip clojure-1.4.0.zip
- sudo mkdir /usr/lib/clojure
- sudo mv clojure-1.4.0/clojure-1.4.0*.jar /usr/lib/clojure
- sudo chown root /usr/lib/clojure/*
- sudo chgrp root /usr/lib/clojure/*
- sudo chmod +r /usr/lib/clojure/*

Install D support
#################
- sudo apt-get install xdg-utils
- Get the dmd installation from http://dlang.org/download.html
- wget http://ftp.digitalmars.com/dmd_2.060-0_amd64.deb
- sudo dpkg dmd_2.060-0_amd64.deb
- sudo apt-get -f install
- sudo dpkg dmd_2.060-0_amd64.deb

Install Javascript support
##########################
- apt-get install python g++ make
- wget -N http://nodejs.org/dist/node-latest.tar.gz
- tar xzvf node-latest.tar.gz 
- cd node-v0.8.14
- ./configure
- make
- sudo make install
- rm -Rf ~/node-v0.8.14

Final Tests
***********

At this point your AMI should be ready. To prove this to yourself you
should run the language tests with

- cd straitjacket
- sudo -u www-data py.test tests/test_languages.py

This will show you a dot for every language test that passes and a whole
bunch of info about ones that fail. If you get nothing but dots, congrats,
stuff is working

Create new AMI
**************

If you are going to use this to create an AMI the following may be helpful
- Make sure you have a secret key and associated signing certificate. Do this on somewhere other than the EC2 instance you are turning into an AMI
    - openssl genrsa 2048 > my_key.pem
    - openssl req -new -key my_key.pem -out my_key.cert
- scp -i some-ssh-key my_key.pem ubuntu@ec2-instance:/home/ubuntu
- scp -i some-ssh-key my_key.cert ubuntu@ec2-instance:/home/ubuntu
- SSH in to the EC2 instance
- sudo mv my_key.* /mnt/
- Enable the multiverse repos by un-commenting the lines in /etc/apt/sources.list
    33 deb http://us-east-1.ec2.archive.ubuntu.com/ubuntu/ precise multiverse
    34 deb-src http://us-east-1.ec2.archive.ubuntu.com/ubuntu/ precise multiverse
    35 deb http://us-east-1.ec2.archive.ubuntu.com/ubuntu/ precise-updates multiverse
    36 deb-src http://us-east-1.ec2.archive.ubuntu.com/ubuntu/ precise-updates multiverse
    59 deb http://security.ubuntu.com/ubuntu precise-security multiverse
    60 deb-src http://security.ubuntu.com/ubuntu precise-security multiverse
- sudo apt-add-repository ppa:awstools-dev/awstools
- sudo apt-get update
- sudo apt-get install ec2-api-tools ec2-ami-tools
- sudo -E ec2-bundle-vol -r x86_64 -d /mnt -p straitjacket-1.0-instance-store -u Your-AWS-user-ID-which-is-a-12-digit-number -k /mnt/my_key.pem -c /mnt/my_key.cert -s 10240 -e /mnt,/root/.ssh,/home/ubuntu/.ssh
- ec2-upload-bundle -b bucket-name -m /mnt/straitjacket-1.0-instance-store.manifest.xml -a AWS-Access-Key -s AWS-Secret-Key
- ec2-register --name 'bucket-name/straitjacket-1.0-instance-store' bucket-name/straitjacket-1.0-instance-store.manifest.xml -K /mnt/my_key.pem -C /mnt/my_key.cert
- This should output the new AMI ID of your brand-new minted AMI!

    

AppArmor
------

There are a number of AppArmor profiles provided in files/etc/apparmor.d.
You should transfer these to wherever your AppArmor profiles are stored.
Additionally, you need to transfer the AppArmor profile abstractions provided in
files/etc/apparmor.d/abstractions similarly.

Once you have successfully installed your AppArmor profiles, make sure to force
AppArmor to reload its configuration.

System directories
-------

There are a number of system directories StraitJacket uses for intermediate
stages of execution, all (configurably) prefixed by /var/local/straitjacket.
Please take a look at both config/global.conf and install.py (which currently
only can be relied upon to make these directories for you, unfortunately).

Web
-----

This application is (mostly) a standard web.py WSGI-capable web app. A sample
Apache configuration is provided in files/etc/apache2/sites-available.

It is recommended that you verify that your server is properly and
safely configured before full use. The only thing to know here is that by
default, StraitJacket will not enable a language unless it passes all of that
language's specific tests, UNLESS you are running in WSGI mode. If you are
running in WSGI mode, this preventative step is disabled.

You can both run tests locally (using server_tests.py) to ensure your system
is correctly set up, or remotely (using remote_server_tests.py).

License
=====

StraitJacket is released under the AGPLv3. Please see COPYRIGHT and LICENSE.
