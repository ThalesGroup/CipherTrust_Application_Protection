FROM jenkins/jenkins:lts-jdk21

USER root

# Install Docker CLI and tools (no need for daemon configuration)
RUN apt-get update && \
    apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        sudo \
        gosu && \
    install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    chmod a+r /etc/apt/keyrings/docker.gpg && \
    echo \
      "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
      "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
      tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y \
        docker-ce-cli \
        docker-compose-plugin && \
    apt-get clean

# Configure insecure registry for Docker CLI (when needed)
RUN mkdir -p /etc/docker && \
    echo '{"insecure-registries":["registry:5000"]}' > /etc/docker/daemon.json

# Add sudo capability for jenkins user (for gosu/sudo commands)
RUN echo "jenkins ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Install Jenkins plugins
RUN jenkins-plugin-cli --verbose --plugins \
    matrix-auth \
    git \
    gitlab-plugin \
    configuration-as-code \
    workflow-aggregator \
    job-dsl:1.87 \
    kubernetes \
    kubernetes-client-api \
    credentials \
    workflow-step-api \
    structs

USER jenkins
COPY casc.yaml /usr/share/jenkins/casc.yaml
COPY init.groovy.d /usr/share/jenkins/ref/init.groovy.d

# Updated environment variables
ENV JAVA_OPTS="-Xmx1024m -Djenkins.install.runSetupWizard=false -Dhudson.security.csrf.GlobalCrumbIssuerConfiguration.DISABLE_CSRF_PROTECTION=true"
# Note: DOCKER_HOST will be set in docker-compose.yml to tcp://docker-dind:2375