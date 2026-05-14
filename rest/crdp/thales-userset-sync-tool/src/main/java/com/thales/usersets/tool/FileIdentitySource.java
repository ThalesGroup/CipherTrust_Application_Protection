package com.thales.usersets.tool;

import java.io.IOException;
import java.nio.file.Path;
import java.util.Set;

final class FileIdentitySource implements IdentitySource {

    private final Path sourceFile;

    FileIdentitySource(Path sourceFile) {
        this.sourceFile = sourceFile;
    }

    @Override
    public Set<String> loadUsers() throws IOException {
        return IdentityUserSetSyncTool.loadUsers(sourceFile);
    }

    @Override
    public String describe() {
        return sourceFile.toString();
    }
}
