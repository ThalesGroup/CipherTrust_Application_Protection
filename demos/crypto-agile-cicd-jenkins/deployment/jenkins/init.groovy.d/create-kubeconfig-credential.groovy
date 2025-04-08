import jenkins.model.*
import com.cloudbees.plugins.credentials.*
import com.cloudbees.plugins.credentials.domains.*
import org.jenkinsci.plugins.kubernetes.credentials.*

def home = System.getenv("JENKINS_HOME")
def kubeConfigFile = new File("$home/kubeconfig")

if (!kubeConfigFile.exists()) {
    println "[WARN] Kubeconfig file not found at $home/kubeconfig. Skipping credential setup."
    return
}

def store = Jenkins.instance.getExtensionList('com.cloudbees.plugins.credentials.SystemCredentialsProvider')[0].getStore()

def kubeCred = new FileKubeconfigCredentialsImpl(
    CredentialsScope.GLOBAL,
    "docker-desktop-kubeconf",
    "Auto-added kubeconfig credential from init.groovy.d",
    kubeConfigFile.absolutePath
)

store.addCredentials(Domain.global(), kubeCred)

println "✅ Jenkins init script created kubeconfig credential successfully"
