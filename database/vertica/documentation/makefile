############################
# Makefile to build custom user defined functions
############################

## Set to the location of the SDK installation
SDK_HOME?=/opt/vertica/sdk
SDK_JAR?=/opt/vertica/

ifeq ($(SDK_HOME) , /opt/vertica/sdk)
JAVA_BUILDINFO := $(SDK_HOME)/BuildInfo.java
else
JAVA_BUILDINFO := $(SDK_HOME)/com/vertica/sdk/BuildInfo.java
endif

CXX?=g++
CXXFLAGS:=$(CXXFLAGS) -I $(SDK_HOME)/include -I HelperLibraries -g -Wall -Wno-unused-value -shared -fPIC 

ifdef OPTIMIZE
## UDLs should be compiled with compiler optimizations in release builds
CXXFLAGS:=$(CXXFLAGS) -O3
endif

## Set to the desired destination directory for .so output files
BUILD_DIR?=$(abspath build)

## Set to a valid temporary directory
BUILD_TMPDIR?=$(BUILD_DIR)/tmp

## Set to the path to 
BOOST_INCLUDE ?= /usr/include
CURL_INCLUDE ?= /usr/include
ZLIB_INCLUDE ?= /usr/include
BZIP_INCLUDE ?= /usr/include

JAVA_HOME ?= $(SOURCE)/../third-party/jdk/jdk1.6.0_45

JAVA_PATH := bin/java
JAVAC_PATH := bin/javac
JAR_PATH := bin/jar

JAVA ?= $(JAVA_HOME)/$(JAVA_PATH)
JAVAC ?= $(JAVA_HOME)/$(JAVAC_PATH)
JAR ?= $(JAVA_HOME)/$(JAR_PATH)

ifdef RUN_VALGRIND
VALGRIND=valgrind --leak-check=full
endif

.PHONEY: ScalarFunctions TransformFunctions AnalyticFunctions AggregateFunctions UserDefinedLoad JavaFunctions

all: ScalarFunctions TransformFunctions AnalyticFunctions AggregateFunctions UserDefinedLoad JavaFunctions

$(BUILD_DIR)/.exists:
	test -d $(BUILD_DIR) || mkdir -p $(BUILD_DIR)
	touch $(BUILD_DIR)/.exists

$(BUILD_TMPDIR):
	mkdir -p $(BUILD_TMPDIR)

###
# Scalar Functions
###
ScalarFunctions: $(BUILD_DIR)/ScalarFunctions.so

$(BUILD_DIR)/ScalarFunctions.so: ScalarFunctions/*.cpp $(SDK_HOME)/include/Vertica.cpp $(SDK_HOME)/include/BuildInfo.h $(BUILD_DIR)/.exists
	$(CXX) $(CXXFLAGS) -o $@ ScalarFunctions/*.cpp $(SDK_HOME)/include/Vertica.cpp

###
# Transform Functions
###
TransformFunctions: $(BUILD_DIR)/TransformFunctions.so

$(BUILD_DIR)/TransformFunctions.so: TransformFunctions/*.cpp $(SDK_HOME)/include/Vertica.cpp $(SDK_HOME)/include/BuildInfo.h $(BUILD_DIR)/.exists
	$(CXX) $(CXXFLAGS) -o $@ TransformFunctions/*.cpp $(SDK_HOME)/include/Vertica.cpp 

###
# Analytic Functions
###
AnalyticFunctions: $(BUILD_DIR)/AnalyticFunctions.so

$(BUILD_DIR)/AnalyticFunctions.so: AnalyticFunctions/*.cpp $(SDK_HOME)/include/Vertica.cpp $(SDK_HOME)/include/BuildInfo.h $(BUILD_DIR)/.exists
	$(CXX) $(CXXFLAGS) -o $@ AnalyticFunctions/*.cpp $(SDK_HOME)/include/Vertica.cpp

###
# Aggregate Functions
###
AggregateFunctions: $(BUILD_DIR)/AggregateFunctions.so

$(BUILD_DIR)/AggregateFunctions.so: AggregateFunctions/*.cpp $(SDK_HOME)/include/Vertica.cpp $(SDK_HOME)/include/BuildInfo.h $(BUILD_DIR)/.exists
	$(CXX) $(CXXFLAGS) -o $@ AggregateFunctions/*.cpp $(SDK_HOME)/include/Vertica.cpp

###
# UDL Functions
###

## Individual targets for each of the UDL examples
## Some of them are intended to be usable as-is, so they should be in
## separate libraries so they can be used individually
UserDefinedLoad: $(BUILD_DIR)/IconverterLib.so \
				 $(BUILD_DIR)/GZipLib.so \
				 $(BUILD_DIR)/BZipLib.so \
				 $(BUILD_DIR)/cURLLib.so \
				 $(BUILD_DIR)/MultiFileCurlSource.so \
				 $(BUILD_DIR)/SearchAndReplaceFilter.so \
				 $(BUILD_DIR)/filelib.so \
				 $(BUILD_DIR)/BasicIntegerParser.so \
				 $(BUILD_DIR)/ContinuousIntegerParser.so \
				 $(BUILD_DIR)/ExampleDelimitedParser.so \
				 $(BUILD_DIR)/FilePortionSource.so \
				 $(BUILD_DIR)/DelimFilePortionParser.so \
				 $(BUILD_DIR)/NativeIntegerParser.so \
				 $(BUILD_DIR)/TraditionalCsvParser.so \
				 $(BUILD_DIR)/Rfc4180CsvParser.so \
				 $(BUILD_DIR)/NoOpSource.so

$(BUILD_DIR)/IconverterLib.so: FilterFunctions/Iconverter.cpp $(SDK_HOME)/include/Vertica.cpp  $(SDK_HOME)/include/BuildInfo.h $(BUILD_DIR)/.exists
	$(CXX) $(CXXFLAGS) -o $@ FilterFunctions/Iconverter.cpp $(SDK_HOME)/include/Vertica.cpp

$(BUILD_DIR)/GZipLib.so: FilterFunctions/GZip.cpp $(SDK_HOME)/include/Vertica.cpp  $(SDK_HOME)/include/BuildInfo.h $(BUILD_DIR)/.exists
	@if echo "#include <zlib.h>" | $(CXX) -lz -x c++ -shared -fPIC -o/dev/stdout >/dev/null 2>&1 ;\
	then \
		echo $(CXX) $(CXXFLAGS) -I $(ZLIB_INCLUDE) -o $@ FilterFunctions/GZip.cpp $(SDK_HOME)/include/Vertica.cpp -lz ;\
		$(CXX) $(CXXFLAGS) -I $(ZLIB_INCLUDE) -o $@ FilterFunctions/GZip.cpp $(SDK_HOME)/include/Vertica.cpp -lz ;\
	else \
		echo "WARNING: zlib headers or library not found.  GZip.so example will not be built." ; \
		echo "(Hint:  Try installing the 'zlib-devel' package or equivalent for your platform.)" ; \
		echo "Set the ZLIB_INCLUDE environment variable if the headers are installed to a nonstandard location." ;\
		echo "Note that the zlib library MUST be in the standard library search path on ALL NODES of the cluster." ;\
		echo "See the documentation or manpage for 'ld.so' on your system for details." ;\
	fi

$(BUILD_DIR)/BZipLib.so: FilterFunctions/BZip.cpp $(SDK_HOME)/include/Vertica.cpp  $(SDK_HOME)/include/BuildInfo.h $(BUILD_DIR)/.exists
	@if echo "#include <bzip.h>" | $(CXX) -lbz2 -x c++ -shared -fPIC -o/dev/stdout >/dev/null 2>&1 ;\
	then \
		echo $(CXX) $(CXXFLAGS) -I $(BZIP_INCLUDE) -o $@ FilterFunctions/BZip.cpp $(SDK_HOME)/include/Vertica.cpp -lbz2 ; \
		$(CXX) $(CXXFLAGS) -I $(BZIP_INCLUDE) -o $@ FilterFunctions/BZip.cpp $(SDK_HOME)/include/Vertica.cpp -lbz2 ;\
	else \
		echo "WARNING: bzip2 headers or library not found.  BZip.so example will not be built." ; \
		echo "(Hint:  Try installing the 'libbz2-devel' package or equivalent for your platform.)" ; \
		echo "Set the BZIP_INCLUDE environment variable if the headers are installed to a nonstandard location." ;\
		echo "Note that the bz2 library MUST be in the standard library search path on ALL NODES of the cluster." ;\
		echo "See the documentation or manpage for 'ld.so' on your system for details." ;\
	fi

# Depends on libcurl
$(BUILD_DIR)/cURLLib.so: SourceFunctions/cURL.cpp SourceFunctions/curl_fopen.cpp $(SDK_HOME)/include/Vertica.cpp  $(SDK_HOME)/include/BuildInfo.h $(BUILD_DIR)/.exists
	@if echo "#include <curl/curl.h>" | $(CXX) `curl-config --libs` -x c++ -shared -fPIC -o/dev/stdout >/dev/null 2>&1 ;\
	then \
		echo "$(CXX) $(CXXFLAGS) -I $(CURL_INCLUDE) -I SourceFunctions -o $@ SourceFunctions/cURL.cpp SourceFunctions/curl_fopen.cpp $(SDK_HOME)/include/Vertica.cpp" `curl-config --libs` ;\
		$(CXX) $(CXXFLAGS) -I $(CURL_INCLUDE) -I SourceFunctions -o $@ SourceFunctions/cURL.cpp SourceFunctions/curl_fopen.cpp $(SDK_HOME)/include/Vertica.cpp `curl-config --libs` ;\
	else \
		echo "WARNING: cURL headers or library not found.  cURLLib.so example will not be built." ; \
		echo "Set the CURL_INCLUDE environment variable if the headers are installed to a nonstandard location." ;\
		echo "Note that the libcurl library MUST be in the standard library search path on ALL NODES of the cluster." ;\
		echo "See the documentation or manpage for 'ld.so' on your system for details." ;\
	fi

# Depends on libcurl
$(BUILD_DIR)/MultiFileCurlSource.so: SourceFunctions/MultiFileCurlSource.cpp SourceFunctions/curl_support/CoroutineStream.cpp SourceFunctions/curl_support/VDistLib.cpp HelperLibraries/*.h $(SDK_HOME)/include/Vertica.cpp  $(SDK_HOME)/include/BuildInfo.h $(BUILD_DIR)/.exists
	@if echo "#include <curl/curl.h>" | $(CXX) `curl-config --libs` -x c++ -shared -fPIC -o/dev/null >/dev/null 2>&1 ;\
	then \
		echo "$(CXX) $(CXXFLAGS) -I $(CURL_INCLUDE) -o $@ SourceFunctions/MultiFileCurlSource.cpp SourceFunctions/curl_support/CoroutineStream.cpp SourceFunctions/curl_support/VDistLib.cpp $(SDK_HOME)/include/Vertica.cpp" `curl-config --libs` ;\
		$(CXX) $(CXXFLAGS) -I $(CURL_INCLUDE) -o $@ SourceFunctions/MultiFileCurlSource.cpp SourceFunctions/curl_support/CoroutineStream.cpp SourceFunctions/curl_support/VDistLib.cpp $(SDK_HOME)/include/Vertica.cpp `curl-config --libs` ;\
	else \
		echo "WARNING: cURL headers or library not found.  cURLLib.so example will not be built." ; \
		echo "Set the CURL_INCLUDE environment variable if the headers are installed to a nonstandard location." ;\
		echo "Note that the libcurl library MUST be in the standard library search path on ALL NODES of the cluster." ;\
		echo "See the documentation or manpage for 'ld.so' on your system for details." ;\
	fi

$(BUILD_DIR)/SearchAndReplaceFilter.so: FilterFunctions/SearchAndReplaceFilter.cpp $(SDK_HOME)/include/Vertica.cpp  $(SDK_HOME)/include/BuildInfo.h $(BUILD_DIR)/.exists
	$(CXX) $(CXXFLAGS) -o $@ FilterFunctions/SearchAndReplaceFilter.cpp $(SDK_HOME)/include/Vertica.cpp

$(BUILD_DIR)/filelib.so: SourceFunctions/filelib.cpp $(SDK_HOME)/include/Vertica.cpp  $(SDK_HOME)/include/BuildInfo.h $(BUILD_DIR)/.exists
	$(CXX) $(CXXFLAGS) -o $@ SourceFunctions/filelib.cpp $(SDK_HOME)/include/Vertica.cpp

$(BUILD_DIR)/BasicIntegerParser.so: ParserFunctions/BasicIntegerParser.cpp $(SDK_HOME)/include/Vertica.cpp  $(SDK_HOME)/include/BuildInfo.h $(BUILD_DIR)/.exists
	$(CXX) $(CXXFLAGS) -o $@ ParserFunctions/BasicIntegerParser.cpp $(SDK_HOME)/include/Vertica.cpp

$(BUILD_DIR)/ContinuousIntegerParser.so: ParserFunctions/ContinuousIntegerParser.cpp $(SDK_HOME)/include/Vertica.cpp  $(SDK_HOME)/include/BuildInfo.h $(BUILD_DIR)/.exists
	$(CXX) $(CXXFLAGS) -o $@ ParserFunctions/ContinuousIntegerParser.cpp $(SDK_HOME)/include/Vertica.cpp

$(BUILD_DIR)/ExampleDelimitedParser.so: ParserFunctions/ExampleDelimitedParser.cpp ParserFunctions/ExampleDelimitedChunker.cpp $(SDK_HOME)/include/Vertica.cpp  $(SDK_HOME)/include/BuildInfo.h $(BUILD_DIR)/.exists
	$(CXX) $(CXXFLAGS) -o $@ ParserFunctions/ExampleDelimitedChunker.cpp ParserFunctions/ExampleDelimitedParser.cpp $(SDK_HOME)/include/Vertica.cpp

$(BUILD_DIR)/FilePortionSource.so: ApportionLoadFunctions/FilePortionSource.cpp $(SDK_HOME)/include/Vertica.cpp  SourceFunctions/filelib.cpp $(SDK_HOME)/include/BuildInfo.h $(BUILD_DIR)/.exists
	$(CXX) $(CXXFLAGS) -o $@ ApportionLoadFunctions/FilePortionSource.cpp $(SDK_HOME)/include/Vertica.cpp

$(BUILD_DIR)/DelimFilePortionParser.so: ApportionLoadFunctions/DelimFilePortionParser.cpp $(SDK_HOME)/include/Vertica.cpp  $(SDK_HOME)/include/BuildInfo.h $(BUILD_DIR)/.exists
	$(CXX) $(CXXFLAGS) -o $@ ApportionLoadFunctions/DelimFilePortionParser.cpp $(SDK_HOME)/include/Vertica.cpp

$(BUILD_DIR)/NativeIntegerParser.so: ApportionLoadFunctions/NativeIntegerParser.cpp $(SDK_HOME)/include/Vertica.cpp $(SDK_HOME)/include/BuildInfo.h $(BUILD_DIR)/.exists
	$(CXX) $(CXXFLAGS) -o $@ ApportionLoadFunctions/NativeIntegerParser.cpp $(SDK_HOME)/include/Vertica.cpp

# Depends boost headers but not libs
$(BUILD_DIR)/TraditionalCsvParser.so: ParserFunctions/TraditionalCsvParser.cpp $(SDK_HOME)/include/Vertica.cpp $(SDK_HOME)/include/BuildInfo.h $(BUILD_DIR)/.exists
	@if echo '#include <boost/tokenizer.hpp>' | $(CXX) -I $(BOOST_INCLUDE) -x c++ -shared -fPIC -o /dev/stdout - >/dev/null 2>&1 ;\
	then \
		echo "$(CXX) $(CXXFLAGS) -I $(BOOST_INCLUDE) -o $@ ParserFunctions/TraditionalCsvParser.cpp $(SDK_HOME)/include/Vertica.cpp" ;\
		$(CXX) $(CXXFLAGS) -I $(BOOST_INCLUDE) -o $@ ParserFunctions/TraditionalCsvParser.cpp $(SDK_HOME)/include/Vertica.cpp ;\
	else \
		echo "WARNING: Boost headers not found.  CsvParser.so example will not be compiled." ; \
		echo "Set the BOOST_INCLUDE environment variable if the headers are installed to a nonstandard location." ;\
	fi

# Helper target 
$(BUILD_TMPDIR)/libcsv-3.0.1/.exists: $(BUILD_TMPDIR)
	tar xzf ParserFunctions/libcsv/libcsv-3.0.1.tar.gz -C $(BUILD_TMPDIR)
	touch $(BUILD_TMPDIR)/libcsv-3.0.1/.exists

$(BUILD_DIR)/Rfc4180CsvParser.so: ParserFunctions/Rfc4180CsvParser.cpp $(BUILD_TMPDIR)/libcsv-3.0.1/.exists $(SDK_HOME)/include/Vertica.cpp $(SDK_HOME)/include/BuildInfo.h $(BUILD_DIR)/.exists
	$(MAKE) -C $(BUILD_TMPDIR)/libcsv-3.0.1 libcsv.a
	$(CXX) $(CXXFLAGS) -I $(BUILD_TMPDIR)/libcsv-3.0.1 -o $@ ParserFunctions/Rfc4180CsvParser.cpp $(BUILD_TMPDIR)/libcsv-3.0.1/libcsv.a $(SDK_HOME)/include/Vertica.cpp

$(BUILD_DIR)/NoOpSource.so: SourceFunctions/NoOpSource.cpp $(SDK_HOME)/include/Vertica.cpp  $(SDK_HOME)/include/BuildInfo.h $(BUILD_DIR)/.exists
	$(CXX) $(CXXFLAGS) -o $@ SourceFunctions/NoOpSource.cpp $(SDK_HOME)/include/Vertica.cpp

# Build Java Libraries
JavaFunctions: $(BUILD_DIR)/JavaScalarLib.jar $(BUILD_DIR)/JavaTransformLib.jar $(BUILD_DIR)/JavaUDlLib.jar $(BUILD_DIR)/JavaUDAnLib.jar

$(BUILD_DIR)/JavaScalarLib.jar : JavaUDx/ScalarFunctions/com/vertica/JavaLibs/*.java $(JAVA_BUILDINFO) $(BUILD_DIR)/.exists
	-rm -rf $(BUILD_DIR)/JavaScalarLib
	mkdir $(BUILD_DIR)/JavaScalarLib
	$(JAVAC) -g -cp $(SDK_JAR)/bin/VerticaSDK.jar:$(SDK_JAR)/bin/asm-1.0.2.jar:$(SDK_JAR)/bin/commons-codec-1.7.jar:$(SDK_JAR)/bin/commons-lang-2.6.jar:$(SDK_JAR)/bin/javax.ws.rs-api-2.0-m10.jar:$(SDK_JAR)/bin/json-path-0.8.1.jar:$(SDK_JAR)/bin/json-smart-2.1.0.jar $(JAVA_BUILDINFO) -d $(BUILD_DIR)/JavaScalarLib
	cd JavaUDx/ScalarFunctions; $(JAVAC) -g -cp $(SDK_JAR)/bin/VerticaSDK.jar:$(SDK_JAR)/bin/asm-1.0.2.jar:$(SDK_JAR)/bin/commons-codec-1.7.jar:$(SDK_JAR)/bin/commons-lang-2.6.jar:$(SDK_JAR)/bin/javax.ws.rs-api-2.0-m10.jar:$(SDK_JAR)/bin/json-path-0.8.1.jar:$(SDK_JAR)/bin/json-smart-2.1.0.jar com/vertica/JavaLibs/*.java -d $(BUILD_DIR)/JavaScalarLib
	cd $(BUILD_DIR)/JavaScalarLib; $(JAR) cf $(BUILD_DIR)/JavaScalarLib.jar .

$(BUILD_DIR)/JavaTransformLib.jar : JavaUDx/TransformFunctions/com/vertica/JavaLibs/*.java $(JAVA_BUILDINFO) $(BUILD_DIR)/.exists
	-rm -rf $(BUILD_DIR)/JavaTransformLib
	mkdir $(BUILD_DIR)/JavaTransformLib
	$(JAVAC) -g -cp $(SDK_JAR)/bin/VerticaSDK.jar $(JAVA_BUILDINFO) -d $(BUILD_DIR)/JavaTransformLib
	cd JavaUDx/TransformFunctions; $(JAVAC) -g -cp $(SDK_JAR)/bin/VerticaSDK.jar com/vertica/JavaLibs/*.java -d $(BUILD_DIR)/JavaTransformLib
	cd $(BUILD_DIR)/JavaTransformLib; $(JAR) cf $(BUILD_DIR)/JavaTransformLib.jar .

$(BUILD_DIR)/JavaUDlLib.jar : JavaUDx/UDLFunctions/com/vertica/JavaLibs/*.java $(JAVA_BUILDINFO) $(BUILD_DIR)/.exists
	-rm -rf $(BUILD_DIR)/JavaUDlLib
	mkdir $(BUILD_DIR)/JavaUDlLib
	$(JAVAC) -g -cp $(SDK_JAR)/bin/VerticaSDK.jar $(JAVA_BUILDINFO) -d $(BUILD_DIR)/JavaUDlLib
	cd JavaUDx/UDLFunctions;  $(JAVAC) -g -cp $(SDK_JAR)/bin/VerticaSDK.jar com/vertica/JavaLibs/*.java -d $(BUILD_DIR)/JavaUDlLib
	cd $(BUILD_DIR)/JavaUDlLib; $(JAR) cf $(BUILD_DIR)/JavaUDlLib.jar .

$(BUILD_DIR)/JavaUDAnLib.jar : JavaUDx/UDAnalytics/com/vertica/JavaLibs/*.java $(JAVA_BUILDINFO) $(BUILD_DIR)/.exists
	-rm -rf $(BUILD_DIR)/JavaUDAnLib
	mkdir $(BUILD_DIR)/JavaUDAnLib
	$(JAVAC) -g -cp $(SDK_JAR)/bin/VerticaSDK.jar $(JAVA_BUILDINFO) -d $(BUILD_DIR)/JavaUDAnLib
	cd JavaUDx/UDAnalytics;  $(JAVAC) -g -cp $(SDK_JAR)/bin/VerticaSDK.jar com/vertica/JavaLibs/*.java -d $(BUILD_DIR)/JavaUDAnLib
	cd $(BUILD_DIR)/JavaUDAnLib; $(JAR) cf $(BUILD_DIR)/JavaUDAnLib.jar .


clean:
	rm -rf $(BUILD_TMPDIR)
	rm -f $(BUILD_DIR)/*.so 
	rm -f $(BUILD_DIR)/*.jar
	rm -rf $(BUILD_DIR)/Java*
	-rmdir $(BUILD_DIR) >/dev/null 2>&1 || true
