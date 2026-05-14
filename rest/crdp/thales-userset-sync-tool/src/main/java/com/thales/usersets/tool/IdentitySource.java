package com.thales.usersets.tool;

import java.io.IOException;
import java.util.Set;

interface IdentitySource {
    Set<String> loadUsers() throws IOException;

    String describe();
}
