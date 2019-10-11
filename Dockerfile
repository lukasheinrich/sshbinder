FROM gitlab-registry.cern.ch/linuxsupport/cc7-base:20191002

# Start from empty cache
RUN yum clean all

# Base packages
RUN yum install -y \
    man-pages \
    openafs-krb5 \
    passwd \
    python3-pip \
    yum-plugin-priorities


RUN yum -y install openssh-server passwd sudo
ARG NB_USER=jovyan
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV HOME /home/${NB_USER}
ENV SHELL bash
ENV PS1 "$JUPYTERHUB_USER \w $ "
RUN adduser --uid ${NB_UID} ${NB_USER} && echo "1234" | passwd --stdin ${NB_USER}
RUN ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key -N '' 
RUN chown ${USER} -R /etc/ssh
RUN echo "${USER} ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Cleanup caches to reduce image size
RUN yum clean all

# Jupyter environment setup
RUN pip3 install --no-cache --upgrade pip && \
    pip3 install --no-cache jupyterhub && \
    pip3 install --no-cache jupyterlab && \
    pip3 install --no-cache notebook

ARG NB_USER=jovyan
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV HOME /home/${NB_USER}
ENV SHELL bash
ENV PS1 "$JUPYTERHUB_USER \w $ "

WORKDIR ${HOME}
USER ${USER}
