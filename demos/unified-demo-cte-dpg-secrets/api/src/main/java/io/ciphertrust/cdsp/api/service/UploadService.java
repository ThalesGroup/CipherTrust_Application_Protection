package io.ciphertrust.cdsp.api.service;
import java.util.List;
import org.springframework.web.multipart.MultipartFile;

/**
 * @author Anurag Jain, developer advocate Thales Group
 *
 */
public interface UploadService {
    String saveAttachment(MultipartFile file) throws Exception;

	void saveFiles(MultipartFile[] files) throws Exception;
	
    List<String> getAllFiles();    
}
