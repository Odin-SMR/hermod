from docker2.molflow.com/devops/hermod_python
copy ./ /src
copy hermod-entrypoint.sh /src/
copy hermod-install.sh /src/
copy .hermod.cfg.secret /root/
run chmod +x /src/hermod-entrypoint.sh \
    /src/hermod-entrypoint.sh
workdir /src
run ./hermod-install.sh install
#entrypoint ./hermod-entrypoint.sh
cmd /usr/local/bin/hermodlogserver
