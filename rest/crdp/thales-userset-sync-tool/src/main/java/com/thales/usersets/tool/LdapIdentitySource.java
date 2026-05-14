package com.thales.usersets.tool;

import java.io.IOException;
import java.util.Hashtable;
import java.util.Set;
import java.util.TreeSet;

import javax.naming.Context;
import javax.naming.NamingEnumeration;
import javax.naming.NamingException;
import javax.naming.directory.Attribute;
import javax.naming.directory.Attributes;
import javax.naming.directory.DirContext;
import javax.naming.ldap.InitialLdapContext;
import javax.naming.ldap.LdapContext;
import javax.naming.directory.SearchControls;
import javax.naming.directory.SearchResult;
import javax.naming.ldap.StartTlsRequest;
import javax.naming.ldap.StartTlsResponse;

final class LdapIdentitySource implements IdentitySource {

    private static final int ADS_UF_ACCOUNTDISABLE = 0x0002;

    private final String providerUrl;
    private final String bindDn;
    private final String password;
    private final String searchBase;
    private final String searchFilter;
    private final String userIdAttribute;
    private final boolean subtree;
    private final String transportSecurity;
    private final int connectTimeoutMillis;
    private final int readTimeoutMillis;
    private final boolean excludeDisabledUsers;
    private final String disabledStatusAttribute;

    LdapIdentitySource(
        String providerUrl,
        String bindDn,
        String password,
        String searchBase,
        String searchFilter,
        String userIdAttribute,
        boolean subtree,
        String transportSecurity,
        int connectTimeoutMillis,
        int readTimeoutMillis,
        boolean excludeDisabledUsers,
        String disabledStatusAttribute) {
        this.providerUrl = providerUrl;
        this.bindDn = bindDn;
        this.password = password;
        this.searchBase = searchBase;
        this.searchFilter = searchFilter;
        this.userIdAttribute = userIdAttribute;
        this.subtree = subtree;
        this.transportSecurity = transportSecurity;
        this.connectTimeoutMillis = connectTimeoutMillis;
        this.readTimeoutMillis = readTimeoutMillis;
        this.excludeDisabledUsers = excludeDisabledUsers;
        this.disabledStatusAttribute = disabledStatusAttribute;
    }

    @Override
    public Set<String> loadUsers() throws IOException {
        Hashtable<String, String> env = new Hashtable<>();
        env.put(Context.INITIAL_CONTEXT_FACTORY, "com.sun.jndi.ldap.LdapCtxFactory");
        env.put(Context.PROVIDER_URL, providerUrl);
        env.put(Context.SECURITY_AUTHENTICATION, "simple");
        env.put(Context.SECURITY_PRINCIPAL, bindDn);
        env.put(Context.SECURITY_CREDENTIALS, password);
        env.put("com.sun.jndi.ldap.connect.timeout", String.valueOf(connectTimeoutMillis));
        env.put("com.sun.jndi.ldap.read.timeout", String.valueOf(readTimeoutMillis));
        if ("SSL".equalsIgnoreCase(transportSecurity)) {
            env.put(Context.SECURITY_PROTOCOL, "ssl");
        }

        SearchControls controls = new SearchControls();
        controls.setSearchScope(subtree ? SearchControls.SUBTREE_SCOPE : SearchControls.ONELEVEL_SCOPE);
        if (excludeDisabledUsers) {
            controls.setReturningAttributes(new String[] { userIdAttribute, disabledStatusAttribute });
        } else {
            controls.setReturningAttributes(new String[] { userIdAttribute });
        }

        Set<String> users = new TreeSet<>(String.CASE_INSENSITIVE_ORDER);
        LdapContext context = null;
        StartTlsResponse tls = null;
        try {
            context = new InitialLdapContext(env, null);
            if ("STARTTLS".equalsIgnoreCase(transportSecurity)) {
                tls = (StartTlsResponse) context.extendedOperation(new StartTlsRequest());
                tls.negotiate();
            }
            NamingEnumeration<SearchResult> results = context.search(searchBase, searchFilter, controls);
            while (results.hasMore()) {
                SearchResult result = results.next();
                Attributes attributes = result.getAttributes();
                if (attributes == null) {
                    continue;
                }
                if (excludeDisabledUsers && isDisabled(attributes)) {
                    continue;
                }
                Attribute attribute = attributes.get(userIdAttribute);
                if (attribute == null) {
                    continue;
                }
                NamingEnumeration<?> values = attribute.getAll();
                while (values.hasMore()) {
                    Object value = values.next();
                    if (value != null) {
                        String normalized = value.toString().trim();
                        if (!normalized.isBlank()) {
                            users.add(normalized);
                        }
                    }
                }
            }
        } catch (NamingException e) {
            throw new IOException("LDAP query failed for base " + searchBase + ": " + e.getMessage(), e);
        } finally {
            if (tls != null) {
                try {
                    tls.close();
                } catch (IOException ignored) {
                }
            }
            if (context != null) {
                try {
                    context.close();
                } catch (NamingException ignored) {
                }
            }
        }
        return users;
    }

    @Override
    public String describe() {
        return "ldap:" + providerUrl + "|" + searchBase + "|" + searchFilter + "|security=" + transportSecurity;
    }

    private boolean isDisabled(Attributes attributes) throws NamingException {
        Attribute attribute = attributes.get(disabledStatusAttribute);
        if (attribute == null || attribute.size() == 0) {
            return false;
        }
        Object rawValue = attribute.get();
        if (rawValue == null) {
            return false;
        }

        if ("userAccountControl".equalsIgnoreCase(disabledStatusAttribute)) {
            int numericValue = Integer.parseInt(rawValue.toString());
            return (numericValue & ADS_UF_ACCOUNTDISABLE) == ADS_UF_ACCOUNTDISABLE;
        }

        String normalized = rawValue.toString().trim();
        return "disabled".equalsIgnoreCase(normalized)
            || "true".equalsIgnoreCase(normalized)
            || "1".equals(normalized);
    }
}
