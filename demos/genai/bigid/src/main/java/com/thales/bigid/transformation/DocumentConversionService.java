package com.thales.bigid.transformation;

import java.io.BufferedWriter;
import java.io.File;
import java.io.IOException;
import java.io.StringWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.apache.poi.hssf.usermodel.HSSFWorkbook;
import org.apache.poi.hwpf.HWPFDocument;
import org.apache.poi.hwpf.extractor.WordExtractor;
import org.apache.poi.ss.usermodel.Cell;
import org.apache.poi.ss.usermodel.DateUtil;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.ss.usermodel.Sheet;
import org.apache.poi.ss.usermodel.Workbook;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFParagraph;

public class DocumentConversionService {

	public String extractText(File inputFile) throws IOException {
		String extension = getExtension(inputFile.getName());
		switch (extension) {
		case ".pdf":
			return extractPdf(inputFile);
		case ".docx":
		case ".doc":
			return extractWord(inputFile, extension);
		case ".xlsx":
		case ".xls":
			return extractExcel(inputFile, extension);
		case ".txt":
		case ".csv":
			return Files.readString(inputFile.toPath(), StandardCharsets.UTF_8);
		default:
			throw new IOException("Unsupported file type: " + inputFile.getName());
		}
	}

	private String extractPdf(File inputFile) throws IOException {
		try (PDDocument document = PDDocument.load(inputFile)) {
			return new PDFTextStripper().getText(document);
		}
	}

	private String extractWord(File inputFile, String extension) throws IOException {
		StringBuilder text = new StringBuilder();
		if (".docx".equals(extension)) {
			try (XWPFDocument document = new XWPFDocument(Files.newInputStream(inputFile.toPath()))) {
				for (XWPFParagraph paragraph : document.getParagraphs()) {
					text.append(paragraph.getText()).append(System.lineSeparator());
				}
			}
		} else {
			try (HWPFDocument document = new HWPFDocument(Files.newInputStream(inputFile.toPath()));
					WordExtractor extractor = new WordExtractor(document)) {
				for (String paragraph : extractor.getParagraphText()) {
					text.append(paragraph.trim()).append(System.lineSeparator());
				}
			}
		}
		return text.toString();
	}

	private String extractExcel(File inputFile, String extension) throws IOException {
		try (Workbook workbook = ".xlsx".equals(extension)
				? new XSSFWorkbook(Files.newInputStream(inputFile.toPath()))
				: new HSSFWorkbook(Files.newInputStream(inputFile.toPath()));
				StringWriter stringWriter = new StringWriter();
				BufferedWriter writer = new BufferedWriter(stringWriter)) {
			Sheet sheet = workbook.getSheetAt(0);
			for (Row row : sheet) {
				for (int i = 0; i < row.getLastCellNum(); i++) {
					if (i > 0) {
						writer.write(",");
					}
					Cell cell = row.getCell(i);
					writer.write(escapeCsv(cell == null ? "" : toCellValue(cell)));
				}
				writer.newLine();
			}
			writer.flush();
			return stringWriter.toString();
		}
	}

	private String toCellValue(Cell cell) {
		switch (cell.getCellType()) {
		case STRING:
			return cell.getStringCellValue();
		case NUMERIC:
			return DateUtil.isCellDateFormatted(cell) ? cell.getDateCellValue().toString()
					: String.valueOf(cell.getNumericCellValue());
		case BOOLEAN:
			return String.valueOf(cell.getBooleanCellValue());
		case FORMULA:
			return cell.getCellFormula();
		case BLANK:
		default:
			return "";
		}
	}

	private String escapeCsv(String input) {
		if (input.contains(",") || input.contains("\"") || input.contains("\n")) {
			return "\"" + input.replace("\"", "\"\"") + "\"";
		}
		return input;
	}

	private String getExtension(String fileName) {
		int index = fileName.lastIndexOf('.');
		return index >= 0 ? fileName.substring(index).toLowerCase() : "";
	}
}
