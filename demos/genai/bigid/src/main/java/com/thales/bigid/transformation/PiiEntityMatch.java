package com.thales.bigid.transformation;

public class PiiEntityMatch {

	public final int offset;
	public final int length;
	public final String text;
	public final String category;
	public final double confidence;

	public PiiEntityMatch(int offset, int length, String text, String category, double confidence) {
		this.offset = offset;
		this.length = length;
		this.text = text;
		this.category = category;
		this.confidence = confidence;
	}
}
