package com.thales.usersets.tool;

import com.thales.usersets.CMUserSetHelper;
import com.thales.usersets.CMUserSetHelper.UserSetSummary;
import com.thales.usersets.CMUserSetHelper.UserSetSyncResult;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Properties;
import java.util.Set;
import java.util.TreeSet;

public final class IdentityUserSetSyncTool {

    private static final String CONFIG_SYSPROP = "identity.userset.config";
    private static final String CONFIG_ENV = "IDENTITY_USERSET_CONFIG_FILE";

    private IdentityUserSetSyncTool() {
    }

    public static void main(String[] args) throws Exception {
        Path configPath = resolveConfigPath(args);
        Properties props = loadProperties(configPath);

        String cmHost = required(props, "cm.host");
        String cmUser = required(props, "cm.username");
        String cmPassword = required(props, "cm.password");
        boolean debug = Boolean.parseBoolean(props.getProperty("cm.debug", "false"));
        String mode = normalize(props.getProperty("sync.mode", "CHECK"));
        String sourceMode = normalize(props.getProperty("source.mode", "FILE"));
        String sourceType = normalize(props.getProperty("source.type", "LDAP"));
        Path outputFile = optionalPath(props.getProperty("output.file"));
        Path auditDir = optionalPath(props.getProperty("audit.dir"));
        int maxRemovals = integerProperty(props, "sync.maxRemovals", -1);
        double maxRemovalPercent = doubleProperty(props, "sync.maxRemovalPercent", 100.0d);

        String bearerToken = new CMUserSetHelper("placeholder", cmHost, debug).getBearerToken(cmUser, cmPassword);
        String report;
        if ("CHECK".equals(mode)) {
            List<SyncPlan> plans = buildPlans(props, sourceMode, sourceType);
            report = runCheck(cmHost, bearerToken, debug, plans, auditDir);
        } else if ("SYNC".equals(mode)) {
            List<SyncPlan> plans = buildPlans(props, sourceMode, sourceType);
            report = runSync(cmHost, bearerToken, debug, plans, auditDir, maxRemovals, maxRemovalPercent);
        } else if ("ROLLBACK".equals(mode)) {
            report = runRollback(cmHost, bearerToken, debug, props, auditDir, maxRemovals, maxRemovalPercent);
        } else {
            throw new IllegalArgumentException("Unsupported sync.mode: " + mode + ". Expected CHECK, SYNC, or ROLLBACK.");
        }

        if (outputFile != null) {
            Path parent = outputFile.toAbsolutePath().getParent();
            if (parent != null) {
                Files.createDirectories(parent);
            }
            Files.writeString(outputFile, report, StandardCharsets.UTF_8);
            System.out.println("Wrote report to " + outputFile.toAbsolutePath());
        }
        System.out.println(report);
    }

    private static String runCheck(String cmHost, String bearerToken, boolean debug, List<SyncPlan> plans, Path auditDir) throws Exception {
        CMUserSetHelper helper = new CMUserSetHelper("placeholder", cmHost, debug);
        StringBuilder out = new StringBuilder();
        out.append("Identity UserSet Check").append(System.lineSeparator());
        out.append("Generated: ").append(OffsetDateTime.now()).append(System.lineSeparator());
        out.append(System.lineSeparator());

        out.append("Existing CipherTrust UserSets").append(System.lineSeparator());
        List<UserSetSummary> existing = new ArrayList<>(helper.listUserSets(bearerToken));
        existing.sort(Comparator.comparing(summary -> normalize(summary.getName())));
        for (UserSetSummary summary : existing) {
            out.append(summary.getName()).append(" | ").append(summary.getId()).append(System.lineSeparator());
        }

        out.append(System.lineSeparator());
        out.append("Planned Sync Targets").append(System.lineSeparator());
        for (SyncPlan plan : plans) {
            UserSetSummary existingSet = helper.findUserSetByName(plan.userSetName, bearerToken);
            String status = existingSet == null ? "CREATE" : "UPDATE";
            Set<String> desiredUsers = plan.loadUsers();
            Set<String> currentUsers = existingSet == null
                ? new LinkedHashSet<>()
                : new CMUserSetHelper(existingSet.getId(), cmHost, debug).getUsersInUserSet(bearerToken);
            out.append(plan.userSetName)
                .append(" | action=").append(status)
                .append(" | source=").append(plan.source.describe())
                .append(" | users=").append(desiredUsers.size())
                .append(" | current=").append(currentUsers.size())
                .append(System.lineSeparator());
            writeAuditFiles(auditDir, "check", plan.userSetName, currentUsers, desiredUsers, diff(desiredUsers, currentUsers), diff(currentUsers, desiredUsers));
        }
        return out.toString();
    }

    private static String runSync(
        String cmHost,
        String bearerToken,
        boolean debug,
        List<SyncPlan> plans,
        Path auditDir,
        int maxRemovals,
        double maxRemovalPercent) throws Exception {
        CMUserSetHelper helper = new CMUserSetHelper("placeholder", cmHost, debug);
        StringBuilder out = new StringBuilder();
        out.append("Identity UserSet Sync").append(System.lineSeparator());
        out.append("Generated: ").append(OffsetDateTime.now()).append(System.lineSeparator());
        out.append(System.lineSeparator());

        for (SyncPlan plan : plans) {
            Set<String> users = plan.loadUsers();
            UserSetSummary existingSet = helper.findUserSetByName(plan.userSetName, bearerToken);
            Set<String> currentUsers = existingSet == null
                ? new LinkedHashSet<>()
                : new CMUserSetHelper(existingSet.getId(), cmHost, debug).getUsersInUserSet(bearerToken);
            Set<String> usersToAdd = diff(users, currentUsers);
            Set<String> usersToRemove = diff(currentUsers, users);
            enforceRemovalGuards(plan.userSetName, currentUsers.size(), usersToRemove.size(), maxRemovals, maxRemovalPercent);
            writeAuditFiles(auditDir, "presync", plan.userSetName, currentUsers, users, usersToAdd, usersToRemove);

            UserSetSyncResult result = helper.ensureAndSyncUsersToNamedUserSet(plan.userSetName, plan.description, users, bearerToken);
            Set<String> finalUsers = new CMUserSetHelper(result.getUserSetId(), cmHost, debug).getUsersInUserSet(bearerToken);
            out.append(plan.userSetName)
                .append(" | created=").append(result.isCreated())
                .append(" | changed=").append(result.isChanged())
                .append(" | add=").append(result.getUsersToAdd().size())
                .append(" | remove=").append(result.getUsersToRemove().size())
                .append(" | desired=").append(result.getDesiredUsers().size())
                .append(System.lineSeparator());
            writeAuditFiles(
                auditDir,
                "postsync",
                plan.userSetName,
                finalUsers,
                result.getDesiredUsers(),
                result.getUsersToAdd(),
                result.getUsersToRemove());
        }
        return out.toString();
    }

    private static String runRollback(
        String cmHost,
        String bearerToken,
        boolean debug,
        Properties props,
        Path auditDir,
        int maxRemovals,
        double maxRemovalPercent) throws Exception {
        String userSetName = required(props, "rollback.userSetName");
        Path snapshotFile = resolveRollbackSnapshotFile(props, auditDir, userSetName);
        String description = props.getProperty("rollback.description", "Rollback restore for " + userSetName);

        Set<String> desiredUsers = loadUsers(snapshotFile);
        CMUserSetHelper helper = new CMUserSetHelper("placeholder", cmHost, debug);
        UserSetSummary existingSet = helper.findUserSetByName(userSetName, bearerToken);
        Set<String> currentUsers = existingSet == null
            ? new LinkedHashSet<>()
            : new CMUserSetHelper(existingSet.getId(), cmHost, debug).getUsersInUserSet(bearerToken);
        Set<String> usersToAdd = diff(desiredUsers, currentUsers);
        Set<String> usersToRemove = diff(currentUsers, desiredUsers);
        enforceRemovalGuards(userSetName, currentUsers.size(), usersToRemove.size(), maxRemovals, maxRemovalPercent);
        writeAuditFiles(auditDir, "rollback-presync", userSetName, currentUsers, desiredUsers, usersToAdd, usersToRemove);

        UserSetSyncResult result = helper.ensureAndSyncUsersToNamedUserSet(userSetName, description, desiredUsers, bearerToken);
        Set<String> finalUsers = new CMUserSetHelper(result.getUserSetId(), cmHost, debug).getUsersInUserSet(bearerToken);
        writeAuditFiles(auditDir, "rollback-postsync", userSetName, finalUsers, desiredUsers, result.getUsersToAdd(), result.getUsersToRemove());

        StringBuilder out = new StringBuilder();
        out.append("Identity UserSet Rollback").append(System.lineSeparator());
        out.append("Generated: ").append(OffsetDateTime.now()).append(System.lineSeparator());
        out.append(System.lineSeparator());
        out.append(userSetName)
            .append(" | snapshot=").append(snapshotFile.toAbsolutePath())
            .append(" | created=").append(result.isCreated())
            .append(" | changed=").append(result.isChanged())
            .append(" | add=").append(result.getUsersToAdd().size())
            .append(" | remove=").append(result.getUsersToRemove().size())
            .append(" | desired=").append(result.getDesiredUsers().size())
            .append(System.lineSeparator());
        return out.toString();
    }

    private static List<SyncPlan> buildPlans(Properties props, String sourceMode, String sourceType) {
        if ("LDAP".equals(sourceType) || "AD".equals(sourceType) || "ACTIVE_DIRECTORY".equals(sourceType)) {
            return buildLdapPlans(props, sourceMode);
        }
        if ("ENTRA".equals(sourceType)) {
            return buildEntraPlans(props, sourceMode);
        }
        if ("OKTA".equals(sourceType)) {
            return buildOktaPlans(props, sourceMode);
        }
        if ("SCIM".equals(sourceType)) {
            return buildScimPlans(props, sourceMode);
        }
        throw new IllegalArgumentException("Unsupported source.type: " + sourceType + ". Expected LDAP, AD, ENTRA, OKTA, or SCIM.");
    }

    private static List<SyncPlan> buildLdapPlans(Properties props, String sourceMode) {
        String baseDn = required(props, "ldap.baseDn");
        List<String> ous = splitCsv(required(props, "ldap.ous"));
        List<SyncPlan> plans = new ArrayList<>();
        boolean liveMode = "LIVE".equals(sourceMode);
        for (String ou : ous) {
            String userSetName = baseDn + "-" + ou;
            String description = "LDAP OU sync for base DN " + baseDn + " and OU " + ou;
            IdentitySource source = liveMode ? buildLiveLdapSource(props, baseDn, ou) : buildFileLdapSource(props, ou);
            plans.add(new SyncPlan(userSetName, description, source));
        }
        return plans;
    }

    private static List<SyncPlan> buildEntraPlans(Properties props, String sourceMode) {
        List<String> namespaces = splitCsv(required(props, "entra.namespaces"));
        List<SyncPlan> plans = new ArrayList<>();
        boolean liveMode = "LIVE".equals(sourceMode);
        for (String namespace : namespaces) {
            String prefix = required(props, "entra.prefix." + namespace);
            List<String> groups = splitCsv(required(props, "entra.groups." + namespace));
            for (String group : groups) {
                String userSetName = prefix + "-" + group;
                String description = "Entra/AD group sync for namespace " + namespace + " and group " + group;
                IdentitySource source = liveMode
                    ? buildLiveEntraSource(props, namespace, group)
                    : buildFileEntraSource(props, namespace, group);
                plans.add(new SyncPlan(userSetName, description, source));
            }
        }
        return plans;
    }

    private static List<SyncPlan> buildOktaPlans(Properties props, String sourceMode) {
        List<String> namespaces = splitCsv(required(props, "okta.namespaces"));
        List<SyncPlan> plans = new ArrayList<>();
        boolean liveMode = "LIVE".equals(sourceMode);
        for (String namespace : namespaces) {
            String prefix = required(props, "okta.prefix." + namespace);
            List<String> groups = splitCsv(required(props, "okta.groups." + namespace));
            for (String group : groups) {
                String userSetName = prefix + "-" + group;
                String description = "Okta group sync for namespace " + namespace + " and group " + group;
                IdentitySource source = liveMode
                    ? buildLiveOktaSource(props, namespace, group)
                    : buildFileOktaSource(props, namespace, group);
                plans.add(new SyncPlan(userSetName, description, source));
            }
        }
        return plans;
    }

    private static List<SyncPlan> buildScimPlans(Properties props, String sourceMode) {
        List<String> namespaces = splitCsv(required(props, "scim.namespaces"));
        List<SyncPlan> plans = new ArrayList<>();
        boolean liveMode = "LIVE".equals(sourceMode);
        for (String namespace : namespaces) {
            String prefix = required(props, "scim.prefix." + namespace);
            List<String> groups = splitCsv(required(props, "scim.groups." + namespace));
            for (String group : groups) {
                String userSetName = prefix + "-" + group;
                String description = "SCIM group sync for namespace " + namespace + " and group " + group;
                IdentitySource source = liveMode
                    ? buildLiveScimSource(props, namespace, group)
                    : buildFileScimSource(props, namespace, group);
                plans.add(new SyncPlan(userSetName, description, source));
            }
        }
        return plans;
    }

    private static IdentitySource buildFileLdapSource(Properties props, String ou) {
        String sourceKey = "ldap.file." + ou;
        return new FileIdentitySource(Path.of(required(props, sourceKey)));
    }

    private static IdentitySource buildLiveLdapSource(Properties props, String baseDn, String ou) {
        String url = required(props, "ldap.url");
        String bindDn = required(props, "ldap.bindDn");
        String password = required(props, "ldap.password");
        String rdnAttribute = props.getProperty("ldap.ouRdnAttribute", "ou");
        String searchFilter = props.getProperty("ldap.searchFilter", "(objectClass=person)");
        String userIdAttribute = props.getProperty("ldap.userIdAttribute", "userPrincipalName");
        boolean subtree = Boolean.parseBoolean(props.getProperty("ldap.subtree", "false"));
        String transportSecurity = props.getProperty("ldap.transportSecurity", "NONE");
        int connectTimeoutMillis = integerProperty(props, "ldap.connectTimeoutMillis", 10000);
        int readTimeoutMillis = integerProperty(props, "ldap.readTimeoutMillis", 30000);
        boolean excludeDisabledUsers = Boolean.parseBoolean(props.getProperty("ldap.excludeDisabledUsers", "false"));
        String disabledStatusAttribute = props.getProperty("ldap.disabledStatusAttribute", "userAccountControl");
        String searchBase = props.getProperty("ldap.searchBase." + ou, rdnAttribute + "=" + ou + "," + baseDn);
        return new LdapIdentitySource(
            url,
            bindDn,
            password,
            searchBase,
            searchFilter,
            userIdAttribute,
            subtree,
            transportSecurity,
            connectTimeoutMillis,
            readTimeoutMillis,
            excludeDisabledUsers,
            disabledStatusAttribute);
    }

    private static IdentitySource buildFileEntraSource(Properties props, String namespace, String group) {
        String sourceKey = "entra.file." + namespace + "." + group;
        return new FileIdentitySource(Path.of(required(props, sourceKey)));
    }

    private static IdentitySource buildLiveEntraSource(Properties props, String namespace, String group) {
        String tenantId = required(props, "entra.tenantId");
        String clientId = required(props, "entra.clientId");
        String clientSecret = required(props, "entra.clientSecret");
        String groupId = required(props, "entra.groupId." + namespace + "." + group);
        String userIdAttribute = props.getProperty("entra.userIdAttribute", "userPrincipalName");
        String graphBaseUrl = props.getProperty("entra.graphBaseUrl", "https://graph.microsoft.com/v1.0");
        return new EntraIdentitySource(tenantId, clientId, clientSecret, groupId, userIdAttribute, graphBaseUrl);
    }

    private static IdentitySource buildFileOktaSource(Properties props, String namespace, String group) {
        String sourceKey = "okta.file." + namespace + "." + group;
        return new FileIdentitySource(Path.of(required(props, sourceKey)));
    }

    private static IdentitySource buildLiveOktaSource(Properties props, String namespace, String group) {
        String baseUrl = required(props, "okta.baseUrl");
        String apiToken = required(props, "okta.apiToken");
        String groupId = required(props, "okta.groupId." + namespace + "." + group);
        String userIdAttribute = props.getProperty("okta.userIdAttribute", "profile.login");
        boolean activeUsersOnly = Boolean.parseBoolean(props.getProperty("okta.activeUsersOnly", "true"));
        int pageLimit = integerProperty(props, "okta.pageLimit", 200);
        return new OktaIdentitySource(baseUrl, apiToken, groupId, userIdAttribute, activeUsersOnly, pageLimit);
    }

    private static IdentitySource buildFileScimSource(Properties props, String namespace, String group) {
        String sourceKey = "scim.file." + namespace + "." + group;
        return new FileIdentitySource(Path.of(required(props, sourceKey)));
    }

    private static IdentitySource buildLiveScimSource(Properties props, String namespace, String group) {
        String baseUrl = required(props, "scim.baseUrl");
        String bearerToken = required(props, "scim.bearerToken");
        String groupId = props.getProperty("scim.groupId." + namespace + "." + group);
        String groupDisplayName = props.getProperty("scim.groupDisplayName." + namespace + "." + group, group);
        String userIdAttribute = props.getProperty("scim.userIdAttribute", "display");
        int pageSize = integerProperty(props, "scim.pageSize", 100);
        return new ScimIdentitySource(baseUrl, bearerToken, groupId, groupDisplayName, userIdAttribute, pageSize);
    }

    private static Path resolveConfigPath(String[] args) {
        if (args != null && args.length > 0 && args[0] != null && !args[0].isBlank()) {
            return Path.of(args[0]);
        }
        String configured = firstNonBlank(System.getProperty(CONFIG_SYSPROP), System.getenv(CONFIG_ENV));
        if (configured == null) {
            throw new IllegalStateException(
                "Missing sync config file. Pass it as the first argument or set " + CONFIG_SYSPROP + " / " + CONFIG_ENV + ".");
        }
        return Path.of(configured);
    }

    private static Properties loadProperties(Path configPath) throws IOException {
        if (!Files.exists(configPath)) {
            throw new IllegalStateException("Config file not found: " + configPath.toAbsolutePath());
        }
        Properties props = new Properties();
        try (InputStream input = Files.newInputStream(configPath)) {
            props.load(input);
        }
        return props;
    }

    private static String required(Properties props, String key) {
        String value = props.getProperty(key);
        if (value == null || value.isBlank()) {
            throw new IllegalStateException("Missing required property: " + key);
        }
        return value.trim();
    }

    private static String normalize(String value) {
        return value == null ? "" : value.trim().toUpperCase(Locale.ROOT);
    }

    private static List<String> splitCsv(String csv) {
        List<String> values = new ArrayList<>();
        for (String part : csv.split(",")) {
            String trimmed = part.trim();
            if (!trimmed.isBlank()) {
                values.add(trimmed);
            }
        }
        return values;
    }

    private static String firstNonBlank(String... values) {
        for (String value : values) {
            if (value != null && !value.isBlank()) {
                return value;
            }
        }
        return null;
    }

    private static Path optionalPath(String configuredPath) {
        if (configuredPath == null || configuredPath.isBlank()) {
            return null;
        }
        return Path.of(configuredPath.trim());
    }

    private static Path resolveRollbackSnapshotFile(Properties props, Path auditDir, String userSetName) {
        Path explicitFile = optionalPath(props.getProperty("rollback.snapshot.file"));
        if (explicitFile != null) {
            return explicitFile;
        }
        if (auditDir == null) {
            throw new IllegalStateException("Missing rollback.snapshot.file and audit.dir is not configured.");
        }
        String phase = props.getProperty("rollback.snapshot.phase", "presync");
        String type = props.getProperty("rollback.snapshot.type", "current");
        return auditDir.resolve(safeName(userSetName)).resolve(phase + "-" + type + ".txt");
    }

    private static int integerProperty(Properties props, String key, int defaultValue) {
        String value = props.getProperty(key);
        if (value == null || value.isBlank()) {
            return defaultValue;
        }
        return Integer.parseInt(value.trim());
    }

    private static double doubleProperty(Properties props, String key, double defaultValue) {
        String value = props.getProperty(key);
        if (value == null || value.isBlank()) {
            return defaultValue;
        }
        return Double.parseDouble(value.trim());
    }

    private static void enforceRemovalGuards(
        String userSetName,
        int currentCount,
        int removalCount,
        int maxRemovals,
        double maxRemovalPercent) {
        if (maxRemovals >= 0 && removalCount > maxRemovals) {
            throw new IllegalStateException(
                "Aborting sync for " + userSetName + ": planned removals " + removalCount + " exceed sync.maxRemovals=" + maxRemovals);
        }
        if (currentCount > 0) {
            double removalPercent = (removalCount * 100.0d) / currentCount;
            if (removalPercent > maxRemovalPercent) {
                throw new IllegalStateException(
                    "Aborting sync for " + userSetName + ": planned removals "
                        + removalCount
                        + " are "
                        + String.format(Locale.ROOT, "%.2f", removalPercent)
                        + "% of current users, above sync.maxRemovalPercent="
                        + maxRemovalPercent);
            }
        }
    }

    private static Set<String> diff(Set<String> left, Set<String> right) {
        Set<String> result = new TreeSet<>(String.CASE_INSENSITIVE_ORDER);
        result.addAll(left);
        result.removeAll(right);
        return result;
    }

    static Set<String> loadUsers(Path sourceFile) throws IOException {
        if (!Files.exists(sourceFile)) {
            throw new IllegalStateException("Source file not found: " + sourceFile.toAbsolutePath());
        }
        Set<String> users = new TreeSet<>(String.CASE_INSENSITIVE_ORDER);
        try (InputStream input = Files.newInputStream(sourceFile);
             InputStreamReader reader = new InputStreamReader(input, StandardCharsets.UTF_8);
             BufferedReader buffered = new BufferedReader(reader)) {
            String line;
            while ((line = buffered.readLine()) != null) {
                String normalized = line.trim();
                if (!normalized.isBlank()) {
                    users.add(normalized);
                }
            }
        }
        return users;
    }

    private static void writeAuditFiles(
        Path auditDir,
        String phase,
        String userSetName,
        Set<String> currentUsers,
        Set<String> desiredUsers,
        Set<String> usersToAdd,
        Set<String> usersToRemove) throws IOException {
        if (auditDir == null) {
            return;
        }
        Path runDir = auditDir.resolve(safeName(userSetName));
        Files.createDirectories(runDir);
        writeLines(runDir.resolve(phase + "-current.txt"), currentUsers);
        writeLines(runDir.resolve(phase + "-desired.txt"), desiredUsers);
        writeLines(runDir.resolve(phase + "-add.txt"), usersToAdd);
        writeLines(runDir.resolve(phase + "-remove.txt"), usersToRemove);
    }

    private static void writeLines(Path path, Set<String> values) throws IOException {
        Files.write(path, values, StandardCharsets.UTF_8);
    }

    private static String safeName(String value) {
        return value.replaceAll("[^A-Za-z0-9._-]", "_");
    }

    private static final class SyncPlan {
        private final String userSetName;
        private final String description;
        private final IdentitySource source;

        private SyncPlan(String userSetName, String description, IdentitySource source) {
            this.userSetName = userSetName;
            this.description = description;
            this.source = source;
        }

        private Set<String> loadUsers() throws IOException {
            return source.loadUsers();
        }
    }
}
