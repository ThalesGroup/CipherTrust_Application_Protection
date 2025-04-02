FROM jenkins/jenkins:lts

USER root
RUN apt-get update && apt-get install -y docker.io && apt-get clean

USER jenkins
COPY casc.yaml /usr/share/jenkins/casc.yaml
COPY init.groovy.d /usr/share/jenkins/ref/init.groovy.d

# Install required plugins, including job-dsl
RUN jenkins-plugin-cli --verbose --plugins \
    git \
    gitlab-plugin \
    configuration-as-code \
    workflow-aggregator \
    job-dsl:1.87

ENV JAVA_OPTS="-Xmx1024m -Djenkins.install.runSetupWizard=false"