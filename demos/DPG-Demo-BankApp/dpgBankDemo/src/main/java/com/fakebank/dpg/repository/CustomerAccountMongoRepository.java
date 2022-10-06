/**
 * 
 */
package com.fakebank.dpg.repository;

import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import com.fakebank.dpg.model.CustomerAccountMongoDocumentBean;

/**
 * @author CipherTrust.io
 *
 */
@Repository
public interface CustomerAccountMongoRepository extends MongoRepository<CustomerAccountMongoDocumentBean, String> {

}
