from docker2.molflow.com/devops/hermod_python

# Copy stuff:
copy ./ /src
copy hermod-entrypoint.sh /src/
copy hermod-install.sh /src/
# - Copy default configs (this should perhaps be done in hermod-install.sh):
copy .hermod.cfg.secret /root/
copy src/odin.hermod/odin/hermod/hermod.cfg.default /etc/

run chmod +x \
        /src/hermod-entrypoint.sh \
        /src/hermod-entrypoint.sh && \
    chmod 0600 /root/.hermod.cfg.secret && \
    cd /src && \
    ./hermod-install.sh install
#entrypoint ./hermod-entrypoint.sh
cmd /usr/local/bin/hermodlogserver
