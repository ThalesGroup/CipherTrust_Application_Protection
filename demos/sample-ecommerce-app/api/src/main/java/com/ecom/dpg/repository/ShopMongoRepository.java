/**
 * 
 */
package com.ecom.dpg.repository;

import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import com.ecom.dpg.model.OrderDocument;

/**
 * @author Anurag Jain - Developer Advocate
 * 
 */
@Repository
public interface ShopMongoRepository extends MongoRepository<OrderDocument, String> {

}
