FROM jenkins/jenkins:lts-jdk21

USER root
# Install Docker and configure insecure registry
RUN apt-get update && \
    apt-get install -y docker.io curl && \
    apt-get clean && \
    mkdir -p /etc/docker && \
    echo '{"insecure-registries":["registry:5000"]}' > /etc/docker/daemon.json && \
    # Verify Docker can restart (but Jenkins will control the final service start)
    service docker start && docker ps >/dev/null

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

ENV JAVA_OPTS="-Xmx1024m -Djenkins.install.runSetupWizard=false -Dhudson.security.csrf.GlobalCrumbIssuerConfiguration.DISABLE_CSRF_PROTECTION=true"
ENV DOCKER_HOST="unix:///var/run/docker.sock"