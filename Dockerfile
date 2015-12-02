from docker2.molflow.com/devops/hermod_python

# Copy stuff:
copy ./ /src
copy hermod-entrypoint.sh /src/
copy hermod-install.sh /src/
copy .hermod.cfg.secret /root/
# - Fake Kerberos:
copy kinit_fejk /usr/bin/kinit
copy kftp_fejk /usr/bin/kftp

# Setup permissions:
run chmod +x /src/hermod-entrypoint.sh \
    /src/hermod-entrypoint.sh
# - Fake Kerberos:
run chmod +x /usr/bin/kinit \
    /usr/bin/kftp

workdir /src
run ./hermod-install.sh install
#entrypoint ./hermod-entrypoint.sh
cmd /usr/local/bin/hermodlogserver
