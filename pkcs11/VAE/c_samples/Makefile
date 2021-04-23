
# How far from the bottom are we in the directory structure?
#
TOP_DIR = ../../../..

# ----- Begin Boilerplate

#
# Set up Vormetric environment
#
include $(TOP_DIR)/mk/Make.rules

ifeq (,$(findstring _obj_,$(CURDIR)))
include $(TOP_DIR)/mk/target.mk
else
include $(TOP_DIR)/mk/build.rules

VPATH = $(SRCDIR)

# ----- End Boilerplate

#
# Executables
#
CRKEY = vpkcs11_sample_create_key$(EXE_EXT)
ENCDEC = vpkcs11_sample_encrypt_decrypt$(EXE_EXT)
DELKEY = vpkcs11_sample_find_delete_key$(EXE_EXT)
EXPKEY = vpkcs11_sample_find_export_key$(EXE_EXT)
CRSIGN = vpkcs11_sample_keypair_create_sign$(EXE_EXT)
CROBJ = vpkcs11_sample_create_object$(EXE_EXT)
ATTRS = vpkcs11_sample_attributes$(EXE_EXT)
DIGEST = vpkcs11_sample_digest$(EXE_EXT)
SIGNVERIFY = vpkcs11_sample_sign_verify$(EXE_EXT)
RANDFPE = vpkcs11_sample_random_fpe$(EXE_EXT)
GENRANDOM = vpkcs11_sample_gen_random$(EXE_EXE)
RENEWCERT = vpkcs11_sample_renew_cert$(EXE_EXE)
CLI = vpkcs11_sample_cli$(EXE_EXE)
KEYSTATES = vpkcs11_sample_key_states$(EXE_EXT)
KEYIMPORT = vpkcs11_sample_import_key$(EXE_EXT)
VERSIONFIND = vpkcs11_test_version_find$(EXE_EXT)

#IMEXPORTOBJ = vpkcs11_sample_key_import_export$(EXE_EXT)
#PERFTESTOBJ = vpkcs11_sample_perf_test$(EXE_EXT)
ENCDEC_MULTI = vpkcs11_sample_en_decrypt_multipart$(EXE_EXT)
META_LOGGING = vpkcs11_sample_metadata_logging$(EXE_EXT)

HELPEROBJ = vpkcs11_sample_helper.$(OBJ_EXT)

#
# .c files to build
# Executables
SRCS = vpkcs11_sample_create_key.c vpkcs11_sample_create_object.c vpkcs11_sample_encrypt_decrypt.c vpkcs11_sample_find_delete_key.c vpkcs11_sample_find_export_key.c vpkcs11_sample_keypair_create_sign.c vpkcs11_sample_en_decrypt_multipart.c vpkcs11_sample_metadata_logging.c vpkcs11_sample_digest.c vpkcs11_sample_sign_verify.c vpkcs11_sample_renew_cert.c vpkcs11_sample_attributes.c vpkcs11_sample_key_states.c vpkcs11_sample_import_key.c vpkcs11_test_version_find.c vpkcs11_sample_helper.c

SRCS+= vpkcs11_sample_cli.c

SRCS2 = $(SRCS:%.c=$(SRCDIR)/%.c)

OBJS = $(SRCS:.c=.$(OBJ_EXT))
LDFLAGS += -g -I$(SRCDIR)/../../src
PROD = pkcs11

all: $(OBJS) $(CRKEY) $(ENCDEC) $(DELKEY) $(EXPKEY) $(CRSIGN) $(CROBJ) $(KEYIMPORT) $(ENCDEC_MULTI) $(META_LOGGING) $(ATTRS) $(DIGEST) $(KEYSTATES) $(GENRANDOM) $(RENEWCERT) $(SIGNVERIFY) $(VERSIONFIND)


$(ENCDEC_MULTI): vpkcs11_sample_en_decrypt_multipart.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $(OUTE)$@ $<  $(HELPEROBJ) $(LDFLAGS) $(LIBDL)

$(CRKEY): vpkcs11_sample_create_key.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $(OUTE)$@ $< $(HELPEROBJ) $(LDFLAGS) $(LIBDL)

$(ENCDEC): vpkcs11_sample_encrypt_decrypt.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $(OUTE)$@ $< $(HELPEROBJ) $(LDFLAGS) $(LIBDL)

$(DELKEY): vpkcs11_sample_find_delete_key.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $(OUTE)$@ $<  $(HELPEROBJ)  $(LDFLAGS) $(LIBDL)

$(EXPKEY): vpkcs11_sample_find_export_key.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $(OUTE)$@ $<  $(HELPEROBJ) $(LDFLAGS) $(LIBDL)

$(CRSIGN): vpkcs11_sample_keypair_create_sign.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $(OUTE)$@ $<  $(HELPEROBJ) $(LDFLAGS) $(LIBDL)

$(CROBJ): vpkcs11_sample_create_object.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $(OUTE)$@ $<  $(HELPEROBJ) $(LDFLAGS) $(LIBDL)

$(KEYIMPORT): vpkcs11_sample_import_key.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $(OUTE)$@ $<  $(HELPEROBJ) $(LDFLAGS) $(LIBDL)

$(META_LOGGING): vpkcs11_sample_metadata_logging.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $(OUTE)$@ $<  $(HELPEROBJ) $(LDFLAGS) $(LIBDL)

$(KEYSTATES): vpkcs11_sample_key_states.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $(OUTE)$@ $<  $(HELPEROBJ) $(LDFLAGS) $(LIBDL)

$(GENRAND): vpkcs11_sample_gen_random.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $(OUTE)$@ $<  $(HELPEROBJ) $(LDFLAGS) $(LIBDL)

$(RANDFPE): vpkcs11_sample_random_fpe.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $(OUTE)$@ $<  $(HELPEROBJ) $(LDFLAGS) $(LIBDL)

$(ATTRS): vpkcs11_sample_attributes.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $(OUTE)$@ $<  $(HELPEROBJ) $(LDFLAGS) $(LIBDL)

$(DIGEST): vpkcs11_sample_digest.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $(OUTE)$@ $<  $(HELPEROBJ) $(LDFLAGS) $(LIBDL)

$(SIGNVERIFY): vpkcs11_sample_sign_verify.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $(OUTE)$@ $<  $(HELPEROBJ) $(LDFLAGS) $(LIBDL)

$(GENRANDOM): vpkcs11_sample_gen_random.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $(OUTE)$@ $<  $(HELPEROBJ) $(LDFLAGS) $(LIBDL)

$(RENEWCERT): vpkcs11_sample_renew_cert.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $(OUTE)$@ $<  $(HELPEROBJ) $(LDFLAGS) $(LIBDL)

$(VERSIONFIND): vpkcs11_test_version_find.$(OBJ_EXT) $(HELPEROBJ)
	$(LD) $(OUTE)$@ $< $(HELPEROBJ) $(LDFLAGS) $(LIBDL)

$(CLI):
	echo	$(LD) $(OUTE)$@ -DTHALES_CLI_MODE $(SRCS2) $(LDFLAGS) $(LIBDL)
	$(LD) $(OUTE)$@ -DTHALES_CLI_MODE $(SRCS2) $(LDFLAGS) $(LIBDL)

#$(PERFTESTOBJ): vpkcs11_sample_perf_test.$(OBJ_EXT)
#	$(LD) $(OUTE)$@ $< $(LDFLAGS) $(LIBDL)

#----- Begin Boilerplate
include $(TOP_DIR)/mk/build.suffix.rules
endif
# ----- End Boilerplate
