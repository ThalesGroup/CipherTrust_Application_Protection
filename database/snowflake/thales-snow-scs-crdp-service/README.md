## **README.md**

### **Snowflake CRDP Service: Thales CipherTrust Integration**

This project provides a **Spring Boot** application that implements protection of sensitive data in Snowflake and exposes the Thales protection and reveal operations as a web service. Leveraging **Snowpark Container Services** (SPCS), the service runs within Snowflake to protect and reveal sensitive data by integrating with the **Thales CipherTrust REST Data Protection** (CRDP) service.

This service supports bulk operations for three data types: `character`, `number-character`, and `number-number`, aligning with the protection policies of the Thales CRDP service.

### **Features**

* **Bulk Data Processing**: Efficiently handles large volumes of data for both protection and revelation.
* **Dynamic Policy Selection**: Automatically selects the appropriate protection policy based on the data type (`char`, `nbr-char`, `nbr-nbr`) and the request's mode (`internal` or `external`).
* **Configurable Environment**: Customizable via environment variables and application properties for flexible deployment.
* **Robust Error Handling**: Gracefully handles missing or invalid data, returning a configurable "bad data" tag.
* **User Context Awareness**: For reveal operations, the service extracts the Snowflake user from the request header (`sf-context-current_user`) to enforce access control based on Thales policies.

***

### **Getting Started**

#### **Prerequisites**

* **Java 17+**
* **Maven**
* **Docker** (for containerized deployment)
* **Access to a Thales CipherTrust Manager** with CRDP enabled and appropriate policies configured.
* **Snowflake Account** with permissions to create external functions or Snowpark Container Services.


The service exposes several **POST** endpoints to handle data protection and revelation. Each endpoint corresponds to a specific data type.

#### **Protection Endpoints**

* `POST /protectbulkchar`
* `POST /protectbulknbrchar`
* `POST /protectbulknbrnbr`

#### **Revelation Endpoints**

* `POST /revealbulkchar`
* `POST /revealbulknbrchar`
* `POST /revealbulknbrnbr`

***

### **Snowflake Integration**

Please review the documentation folder for more content on how to deploy the service.