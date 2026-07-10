package com.example;

import org.json.JSONArray;
import org.json.JSONObject;

public class ProcessedContentArtifacts {

	public final int recordCount;
	public final String extractedText;
	public final String outputText;
	public final JSONArray findings;

	public ProcessedContentArtifacts(int recordCount, String extractedText, String outputText, JSONArray findings) {
		this.recordCount = recordCount;
		this.extractedText = extractedText;
		this.outputText = outputText;
		this.findings = findings == null ? new JSONArray() : findings;
	}

	public String findingsReport(String mode, String sourceId) {
		JSONObject report = new JSONObject();
		report.put("sourceId", sourceId);
		report.put("mode", mode);
		report.put("recordCount", recordCount);
		report.put("findingCount", findings.length());
		report.put("findings", findings);
		return report.toString(2);
	}
}
