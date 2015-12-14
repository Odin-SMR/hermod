from docker2.molflow.com/devops/hermod_python

# Create the odinop user
run addgroup --gid 500 gem && \
    adduser --disabled-password --gecos '' --ingroup gem --uid 507 odinop && \
    adduser odinop sudo && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Copy stuff:
copy ./src/ /src/src
copy hermod-entrypoint.sh /src/
copy hermod-install.sh /src/
# - Copy default configs (this should perhaps be done in hermod-install.sh):
copy src/odin.hermod/odin/hermod/hermod.cfg.default /etc/
run chmod +x \
        /src/hermod-entrypoint.sh \
        /src/hermod-entrypoint.sh && \
    cd /src && \
    ./hermod-install.sh install
# - Copy ssh keys for fejk pdc:
copy ./ssh_keys/pdc_rsa /home/odinop/.ssh/id_rsa
run chmod 600 /home/odinop/.ssh/id_rsa && \
    chmod 700 /home/odinop/.ssh && \
    chown -R odinop /home/odinop/.ssh

user odinop
workdir /home/odinop
add ./test_data/datafile.tar.gz /
copy .hermod.cfg.secret ./
run sudo chown odinop:gem .hermod.cfg.secret && \
    chmod 0600 .hermod.cfg.secret && \
    mkdir hermod_systemlogs
run sudo chown -R odinop:gem /odin && \
    chmod 2770 /odin
cmd /usr/local/bin/hermodlogserver
#entrypoint ./hermod-entrypoint.sh
