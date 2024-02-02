package com.ecom.dpg.repository;

import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;
import org.springframework.stereotype.Repository;

import com.ecom.dpg.model.UserDocument;

/**
 * @author Anurag Jain - Developer Advocate
 * 
 */
@Repository
public interface UserMongoRepository extends MongoRepository<UserDocument, String> {
	@Query("{'username' : ?0}")
	UserDocument findUserByUserName(String userName);
}
