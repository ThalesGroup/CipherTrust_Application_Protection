package com.thales.bigid.transformation;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

import com.azure.ai.textanalytics.TextAnalyticsClient;
import com.azure.ai.textanalytics.TextAnalyticsClientBuilder;
import com.azure.ai.textanalytics.models.PiiEntity;
import com.azure.ai.textanalytics.models.RecognizePiiEntitiesOptions;
import com.azure.ai.textanalytics.models.RecognizePiiEntitiesResult;
import com.azure.ai.textanalytics.util.RecognizePiiEntitiesResultCollection;
import com.azure.core.credential.AzureKeyCredential;

public class AzureTextAnalyticsService {

	private static final int CHUNK_SIZE = 5000;

	private final RuntimeConfig config;
	private final TextAnalyticsClient client;

	public AzureTextAnalyticsService(RuntimeConfig config) {
		this.config = config;
		this.client = new TextAnalyticsClientBuilder().endpoint(config.azureEndpoint)
				.credential(new AzureKeyCredential(config.azureApiKey))
				.buildClient();
	}

	public List<PiiEntityMatch> findSensitiveSpans(String text) {
		List<PiiEntityMatch> matches = new ArrayList<>();
		if (text == null || text.isBlank()) {
			return matches;
		}

		for (int start = 0; start < text.length(); start += CHUNK_SIZE) {
			int end = Math.min(start + CHUNK_SIZE, text.length());
			String chunk = text.substring(start, end);
			RecognizePiiEntitiesOptions options = new RecognizePiiEntitiesOptions();
			RecognizePiiEntitiesResultCollection results = client.recognizePiiEntitiesBatch(List.of(chunk),
					config.azureLanguage, options);
			for (RecognizePiiEntitiesResult result : results) {
				for (PiiEntity entity : result.getEntities()) {
					if (entity.getConfidenceScore() < config.azureConfidenceThreshold) {
						continue;
					}
					int offset = start + entity.getOffset();
					matches.add(new PiiEntityMatch(offset, entity.getLength(), entity.getText(),
							entity.getCategory().toString(), entity.getConfidenceScore()));
				}
			}
		}

		matches.sort(Comparator.comparingInt(match -> match.offset));
		return removeOverlaps(matches);
	}

	private List<PiiEntityMatch> removeOverlaps(List<PiiEntityMatch> matches) {
		List<PiiEntityMatch> cleaned = new ArrayList<>();
		int lastEnd = -1;
		for (PiiEntityMatch match : matches) {
			if (match.offset >= lastEnd) {
				cleaned.add(match);
				lastEnd = match.offset + match.length;
			}
		}
		return cleaned;
	}
}
