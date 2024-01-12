/**
 * 
 */
package io.cpl.cdsp.service;

import java.util.List;

import org.springframework.web.multipart.MultipartFile;

/**
 * @author Anurag Jain, developer advocate Thales Group
 *
 */
public interface AttachmentService {
	String saveAttachment(MultipartFile file) throws Exception;

	void saveFiles(MultipartFile[] files) throws Exception;

	List<String> getAllFiles();
}
