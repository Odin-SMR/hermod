from docker2.molflow.com/devops/hermod_python
copy /src /src
copy hermod-entrypoint.sh /usr/local/bin/
copy hermod-install.sh /usr/local/bin/
workdir /src
run ./hermod-install.sh install
entrypoint /usr/bin/local/hermod-entrypoint.sh
cmd /usr/local/bin/hermodlogserver
