package io.ciphertrust.cdsp.api.service;

import java.io.FileOutputStream;
import java.io.File;
import java.util.Arrays;
import java.util.List;
import org.springframework.web.multipart.MaxUploadSizeExceededException;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

/**
 * @author Anurag Jain, developer advocate Thales Group
 *
 */
@Service
public class UploadServiceImpl implements UploadService {

	@Override
	public String saveAttachment(MultipartFile file) throws Exception {
		String fileName = StringUtils.cleanPath(file.getOriginalFilename());
		try {
			if (fileName.contains("..")) {
				throw new Exception("Filename contains invalid path sequence " + fileName);
			}
			if (file.getBytes().length > (1024 * 1024)) {
				throw new Exception("File size exceeds maximum limit");
			}
			File path = new File(System.getenv("PV_UPLOAD_PATH") + file.getOriginalFilename());
			path.createNewFile();
			FileOutputStream output = new FileOutputStream(path);
			output.write(file.getBytes());
			output.close();
			return file.getOriginalFilename();
		} catch (MaxUploadSizeExceededException e) {
			throw new MaxUploadSizeExceededException(file.getSize());
		} catch (Exception e) {
			throw new Exception("Could not save File: " + fileName);
		}
	}

	@Override
	public void saveFiles(MultipartFile[] files) throws Exception {
		Arrays.asList(files).forEach(file -> {
			try {
				saveAttachment(file);
			} catch (Exception e) {
				throw new RuntimeException(e);
			}
		});
	}

	@Override
	public List<String> getAllFiles() {
		// TODO Auto-generated method stub
		return null;
	}    
}
