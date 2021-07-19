#*************************************************************************
#*                                                                      **
#* Copyright(c) 2012 - 2014                       Confidential Material **
#*                                                                      **
#* This file is the property of Vormetric Inc.                          **
#* The contents are proprietary and confidential.                       **
#* Unauthorized use, duplication, or dissemination of this document,    **
#* in whole or in part, is forbidden without the express consent of     **
#* Vormetric, Inc..                                                     **
#*                                                                      **
#*************************************************************************
#
# This Makefile helps to build samples on *unix system
# Usage : gmake  -- to make the sample binaries
# Usage : gmake clean  -- to clean up the *.o and executables 
# Usage : gmake PASSWORD='your-pin-here' run  -- to run the sample, make sure to replace 'your-pin-here'
#
UNAME = $(shell uname)
CCFLAGS =

ifeq ($(UNAME),AIX)
  CCFLAGS := -maix64 -pthread
endif
ifeq ($(UNAME),HP-UX)
  CCFLAGS := -mlp64 -pthread
endif

CC = gcc $(CCFLAGS)
LD = gcc $(CCFLAGS) -g -o
LIBDL = -ldl

CFLAGS = -g
LDFLAGS = $(LIBDL)

#
# Executables
#
CRKEY = vpkcs11_sample_create_key
ENCDEC = vpkcs11_sample_encrypt_decrypt
DELKEY = vpkcs11_sample_find_delete_key
EXPKEY = vpkcs11_sample_find_export_key
CRSIGN = vpkcs11_sample_keypair_create_sign
CROBJ = vpkcs11_sample_create_object
ATTRS = vpkcs11_sample_attributes
DIGEST = vpkcs11_sample_digest
SIGNVERIFY = vpkcs11_sample_sign_verify
RANDFPE = vpkcs11_sample_random_fpe
GENRANDOM = vpkcs11_sample_gen_random
RENEWCERT = vpkcs11_sample_renew_cert
CLI = vpkcs11_sample_cli$
KEYSTATES = vpkcs11_sample_key_states
KEYIMPORT = vpkcs11_sample_import_key
VERSIONFIND = vpkcs11_test_version_find

HELPEROBJ = vpkcs11_sample_helper.o
#
# .c files to build
#
SRCS = $(shell find . -name 'vpkcs11_sample_*.c')

OBJS = $(SRCS:.c=.o)
OBJ_EXT = o


all: $(OBJS) $(CRKEY) $(ENCDEC) $(DELKEY) $(EXPKEY) $(CRSIGN) $(CROBJ) $(KEYIMPORT) $(ENCDEC_MULTI) $(META_LOGGING) $(ATTRS) $(DIGEST) $(KEYSTATES) $(GENRANDOM) $(RENEWCERT) $(SIGNVERIFY) $(VERSIONFIND)


$(ENCDEC_MULTI): vpkcs11_sample_en_decrypt_multipart.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $@ $@.o $(HELPEROBJ) $(LDFLAGS)

$(CRKEY): vpkcs11_sample_create_key.o $(HELPEROBJ) 
	$(LD) $@ $@.o $(HELPEROBJ) $(LDFLAGS)

$(ENCDEC): vpkcs11_sample_encrypt_decrypt.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $@ $@.o $(HELPEROBJ) $(LDFLAGS)

$(DELKEY): vpkcs11_sample_find_delete_key.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $@ $@.o $(HELPEROBJ) $(LDFLAGS)

$(EXPKEY): vpkcs11_sample_find_export_key.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $@ $@.o $(HELPEROBJ) $(LDFLAGS)

$(CRSIGN): vpkcs11_sample_keypair_create_sign.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $@ $@.o $(HELPEROBJ) $(LDFLAGS)

$(CROBJ): vpkcs11_sample_create_object.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $@ $@.o $(HELPEROBJ) $(LDFLAGS)

$(KEYIMPORT): vpkcs11_sample_import_key.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $@ $@.o $(HELPEROBJ) $(LDFLAGS)

$(META_LOGGING): vpkcs11_sample_metadata_logging.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $@ $@.o $(HELPEROBJ) $(LDFLAGS)

$(KEYSTATES): vpkcs11_sample_key_states.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $@ $@.o $(HELPEROBJ) $(LDFLAGS)

$(GENRAND): vpkcs11_sample_gen_random.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $@ $@.o $(HELPEROBJ) $(LDFLAGS)

$(RANDFPE): vpkcs11_sample_random_fpe.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $@ $@.o $(HELPEROBJ) $(LDFLAGS)

$(ATTRS): vpkcs11_sample_attributes.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $@ $@.o $(HELPEROBJ) $(LDFLAGS)

$(DIGEST): vpkcs11_sample_digest.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $@ $@.o $(HELPEROBJ) $(LDFLAGS)

$(SIGNVERIFY): vpkcs11_sample_sign_verify.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $@ $@.o $(HELPEROBJ) $(LDFLAGS)

$(GENRANDOM): vpkcs11_sample_gen_random.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $@ $@.o $(HELPEROBJ) $(LDFLAGS)

$(RENEWCERT): vpkcs11_sample_renew_cert.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $@ $@.o $(HELPEROBJ) $(LDFLAGS)

$(VERSIONFIND): vpkcs11_test_version_find.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $@ $@.o $(HELPEROBJ) $(LDFLAGS)


clean:
	$(RM) $(OBJS) $(CRKEY) $(ENCDEC) $(DELKEY) $(EXPKEY) $(CRSIGN) $(CROBJ) $(KEYIMPORT) $(ENCDEC_MULTI) $(META_LOGGING) $(ATTRS) $(DIGEST) $(KEYSTATES) $(GENRANDOM) $(RENEWCERT) $(SIGNVERIFY) $(VERSIONFIND)

run:
	./vpkcs11_sample_find_delete_key -p ${PASSWORD} -k testkey
	./vpkcs11_sample_create_key -p ${PASSWORD} -k testkey
	./vpkcs11_sample_find_delete_key -p ${PASSWORD} -k testkey2
	./vpkcs11_sample_create_object -p ${PASSWORD} -k testkey2
	./vpkcs11_sample_find_delete_key -p ${PASSWORD} -k testkey2
	./vpkcs11_sample_keypair_create_sign -p ${PASSWORD} -k testRSAkey
	./vpkcs11_sample_encrypt_decrypt -p ${PASSWORD} -k testkey3
	./vpkcs11_sample_en_decrypt_multipart -p ${PASSWORD} -k testkey4 -f ./vpkcs11_sample_create_key
	./vpkcs11_sample_create_object -p ${PASSWORD} -k wrappingKey
	./vpkcs11_sample_find_export_key -p ${PASSWORD} -k testkey -w wrappingKey
	./vpkcs11_sample_attributes -p ${PASSWORD} -k testRSAkey
	./vpkcs11_sample_digest -p ${PASSWORD} -k testkey3
