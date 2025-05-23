#*************************************************************************
#*                                                                      **
#* Sample code is provided for educational purposes.                    **
#* No warranty of any kind, either expressed or implied by fact or law. **
#* Use of this item is not restricted by copyright or license terms.    **
#*                                                                      **
#*************************************************************************
#
# This Makefile helps to build samples on *unix system
# Usage : gmake  -- to make the sample binaries
# Usage : gmake clean  -- to clean up the *.o and executables 
# Usage : gmake PASSWORD='your-pin-here' run  -- to run the sample, make sure to replace 'your-pin-here'
#


CC = gcc
LD = gcc -g -o
LIBDL = -ldl

CFLAGS+=-g
ifeq ($(CLI_MODE),true)
	CFLAGS += -DTHALES_CLI_MODE
endif
LDFLAGS = $(LIBDL)

#
# Executables
#
CRKEY = pkcs11_sample_create_key
ENCDEC = pkcs11_sample_encrypt_decrypt
DELKEY = pkcs11_sample_find_delete_key
EXPKEY = pkcs11_sample_find_export_key
CRSIGN = pkcs11_sample_keypair_create_sign
CROBJ = pkcs11_sample_create_object
DIGEST = pkcs11_sample_digest
SIGNVERIFY = pkcs11_sample_sign_verify
ENCDEC_MULTI = pkcs11_sample_en_decrypt_multipart
ATTRS = pkcs11_sample_attributes
GENRANDOM = pkcs11_sample_gen_random
KEYSTATES = pkcs11_sample_key_states
KEYIMPORT = pkcs11_sample_import_key
CLI = pkcs11_sample_cli
GETINFO = pkcs11_sample_getinfo
VERSIONFIND = pkcs11_sample_version_find
HELPEROBJ = pkcs11_sample_helper.o
PASSWORD = your-pin-here

CLI_OBJS=pkcs11_sample_create_key.o  pkcs11_sample_encrypt_decrypt.o pkcs11_sample_find_delete_key.o pkcs11_sample_keypair_create_sign.o pkcs11_sample_find_export_key.o pkcs11_sample_en_decrypt_multipart.o pkcs11_sample_digest.o pkcs11_sample_attributes.o

#
# .c files to build
#
SRCS = $(shell find . -name 'pkcs11_sample*.c')

OBJS = $(SRCS:.c=.o)

ifeq ($(CLI_MODE),true)
all : $(OBJS) $(CLI)
else
all: $(OBJS) $(CRKEY) $(ENCDEC) $(DELKEY) $(EXPKEY) $(CRSIGN) $(CROBJ) $(KEYIMPORT) $(ENCDEC_MULTI) $(ATTRS) $(DIGEST) $(GENRANDOM) $(SIGNVERIFY) $(KEYSTATES) $(GETINFO) $(VERSIONFIND) 
endif

$(ENCDEC_MULTI): pkcs11_sample_en_decrypt_multipart.o $(HELPEROBJ)
	$(LD) $(OUTE)$@ $<  $(HELPEROBJ) $(LDFLAGS)

$(CRKEY): pkcs11_sample_create_key.o $(HELPEROBJ) 
	$(LD) $(OUTE)$@ $<  $(HELPEROBJ) $(LDFLAGS)

$(ENCDEC): pkcs11_sample_encrypt_decrypt.o $(HELPEROBJ) 
	$(LD) $(OUTE)$@ $<  $(HELPEROBJ) $(LDFLAGS)

$(DELKEY): pkcs11_sample_find_delete_key.o $(HELPEROBJ)
	$(LD) $(OUTE)$@ $<  $(HELPEROBJ) $(LDFLAGS)

$(EXPKEY): pkcs11_sample_find_export_key.o $(HELPEROBJ)
	$(LD) $(OUTE)$@ $<  $(HELPEROBJ) $(LDFLAGS)

$(CRSIGN): pkcs11_sample_keypair_create_sign.o $(HELPEROBJ)
	$(LD) $(OUTE)$@ $<  $(HELPEROBJ) $(LDFLAGS)

$(CROBJ): pkcs11_sample_create_object.o $(HELPEROBJ)
	$(LD) $(OUTE)$@ $<  $(HELPEROBJ) $(LDFLAGS)

$(DIGEST): pkcs11_sample_digest.o $(HELPEROBJ)
	$(LD) $(OUTE)$@ $< $(HELPEROBJ) $(LDFLAGS)
 
$(SIGNVERIFY): pkcs11_sample_sign_verify.o $(HELPEROBJ)
	$(LD) $(OUTE)$@ $< $(HELPEROBJ) $(LDFLAGS)
 
$(ATTRS): pkcs11_sample_attributes.o $(HELPEROBJ)
	$(LD) $(OUTE)$@ $< $(HELPEROBJ) $(LDFLAGS)

$(KEYSTATES): pkcs11_sample_key_states.o $(HELPEROBJ) 
	$(LD) $(OUTE)$@ $<  $(HELPEROBJ) $(LDFLAGS)

$(KEYIMPORT): pkcs11_sample_import_key.o $(HELPEROBJ)
	$(LD) $(OUTE)$@ $<  $(HELPEROBJ) $(LDFLAGS) 
	
$(GENRANDOM): pkcs11_sample_gen_random.o $(HELPEROBJ)
	$(LD) $(OUTE)$@ $< $(HELPEROBJ) $(LDFLAGS)    

$(GETINFO): pkcs11_sample_getinfo.o $(HELPEROBJ)
	$(LD) $(OUTE)$@ $< $(HELPEROBJ) $(LDFLAGS)    

$(VERSIONFIND): pkcs11_sample_version_find.o $(HELPEROBJ)
	$(LD) $(OUTE)$@ $< $(HELPEROBJ) $(LDFLAGS)    

$(CLI): pkcs11_sample_cli.o $(HELPEROBJ) $(OBJS)
	$(LD) $(OUTE)$@ $< $(HELPEROBJ) $(CLI_OBJS) $(LDFLAGS)    


clean:
	$(RM) $(OBJS) $(CRKEY) $(ENCDEC) $(DELKEY) $(EXPKEY) $(CRSIGN) $(CROBJ) $(KEYIMPORT) $(ENCDEC_MULTI) $(META_LOGGING) $(DIGEST) $(ATTRS) $(GENRANDOM) $(SIGNVERIFY) $(KEYSTATES) $(GETINFO) $(CLI) $(VERSIONFIND)


run:
	./pkcs11_sample_find_delete_key -p ${PASSWORD} -k testkey 
	./pkcs11_sample_create_key -p ${PASSWORD} -k testkey  
	./pkcs11_sample_key_states -p ${PASSWORD} -k testkey -ks 3
	./pkcs11_sample_create_object -p ${PASSWORD} -k testkey2 
	./pkcs11_sample_find_delete_key -p ${PASSWORD} -k testkey2 
	./pkcs11_sample_keypair_create_sign -p ${PASSWORD} -kp testRSAkey 
	./pkcs11_sample_encrypt_decrypt -p ${PASSWORD} -k testkey3 
	./pkcs11_sample_en_decrypt_multipart -p ${PASSWORD} -k testkey4 -f ./pkcs11_sample_create_key
	./pkcs11_sample_create_object -p ${PASSWORD} -k wrappingKey 
	./pkcs11_sample_find_export_key -p ${PASSWORD} -k testkey -w wrappingKey
	./pkcs11_sample_metadata_logging -p ${PASSWORD} -k testkey4 
	./pkcs11_sample_attributes -p ${PASSWORD} -k testkey  
	./pkcs11_sample_digest -p ${PASSWORD} -k testkey
	./pkcs11_sample_sign_verify -p ${PASSWORD} -k newtestkey
	./pkcs11_sample_gen_random -p ${PASSWORD} -d 1234 -z 7
