package com.thales.bigid.transformation;

import java.io.IOException;
import java.nio.file.Path;

public interface RemoteDocumentStore {

	boolean matchesAsset(BigIdAsset asset);

	boolean matchesConfiguredPrefix(BigIdAsset asset);

	Path downloadToTempFile(BigIdAsset asset) throws IOException;

	void writeProtectedText(BigIdAsset asset, String protectedText) throws IOException;

	void writeExtractedText(BigIdAsset asset, String extractedText) throws IOException;

	void writeFindingsReport(BigIdAsset asset, String findingsJson) throws IOException;

	String describeTarget(BigIdAsset asset);
}
