######################################################################
#
# @(#)Makefile.sample	
#
# Makefile for CADP CAPI sample code.
#
# No warranty of any kind, either expressed or implied by fact or law
# Use of this item is not restricted by copyright or license terms		
#
######################################################################

# Set CAPILIBPATH to the path of the directory that contains libcadp_capi library.
CAPILIBPATH := /opt/CipherTrust/CADP_for_C/

CAPILDIR := $(CAPILIBPATH)
CAPIINDIR := $(subst /lib,/include,$(CAPILDIR))

## libname might be different for different OS
## enter the path of openssl library libcrypto.a in CAPILIBNAME
LIBS += -L$(CAPILDIR)
LIBS += -lcrypto
CAPIINCLUDEDIR=$(CAPILIBPATH)/include
# set CC to point to your C compiler.
ifeq ($(OS_NAME),OS400)
CC=icc
else
CC=gcc
endif

# you can compile this with a C++ or C compiler such as gcc 
# (3.2.x or greater).
# if you have an older gcc or another C compiler, you may need to obtain 
# libstdc++.so.5 and possibly libgcc_s.so.1 from a newer gcc/g++.
# For Bluecat, the path to the location of the library and the 
# 
# LIBS = -L/usr/share/bluecat/cdt/lib -lstdc++

# on NCR MP-RAS
# LIBS = -lstdc++ -lpthread -ldl

# For 64-bit builds (Ex: HPUX 11.11) use the 64-bit gcc and the path to the
# 64-bit libgcc.
# LIBSTDC++ = -lstdc++
# LIBGCC = -lgcc_s
# LIBS += -lpthread $(LIBSTDC++)

# HPUX1123-32 requires this LIBS line
# LIBS = -lstdc++



CFLAGS=-g -I$(CAPIINCLUDEDIR)
#     FLAG Tag  for c++
CXXFLAGS=-g -I$(CAPIINCLUDEDIR)
# uncoment this flag to set your platform: 
CFLAGS += -DUNIX
CXXFLAGS += -DUNIX

# depending on the processor architecture (i.e. 32 or 64 bit), the 
# following flag needs to be set.
#     uncomment for 32 bit architectures
# CFLAGS += -DARCH=32
# CXXFLAGS += -DARCH=32
#     uncomment for 64 bit architectures
 CFLAGS += -DARCH=64
 CXXFLAGS += -DARCH=64

# on Linux, uncomment this:
LIBS += -ldl

# on Solaris, uncomment these:
# CFLAGS +=  -DOS_SUNOS5
# CXXFLAGS +=  -DOS_SUNOS5
# LIBS +=  -lsocket -lrt -lnsl
# CPP=g++

# on HP-UX, uncomment this:
# CFLAGS += -DOS_HPUX
# CXXFLAGS += -DOS_HPUX

# on 64-bit Solaris 5.9 uncomment these:
# CFLAGS += -m64
# CXXFLAGS += -m64
# LIBS +=  -m64

# on Itanium 64-bit HP-UX 11.23 uncomment these:
# CFLAGS += -mlp64
# CXXFLAGS += -mlp64
# LIBS += -mlp64

# on 64-bit AIX uncomment these:
# CFLAGS += -maix64
# CXXFLAGS += -maix64
# LIBS += -maix64

# on 64-bit Linux using 32-bit CAPI libraries, uncomment these:
# CFLAGS += -m32 
# CXXFLAGS += -m32
# LIBS += -m32 

# on OS/400 uncomment this
# CFLAGS += -DOS400 -v
# CXXFLAGS += -DOS400 -v

# on 64-bit MAC uncomment these:
# CFLAGS += -DOS_Darwin
# CXXFLAGS += -DOS_Darwin
# CFLAGS += -arch x86_64
# CXXFLAGS += -arch x86_64
# LIBS +=  -m64

ifeq ($(OS_NAME),Darwin)
CAPILIBNAME = $(CAPILIBPATH)/libcadp_capi.dylib
CryptoDataUtilityLIBNAME = $(CAPILIBPATH)/libCryptoDataUtility.dylib
CPP=g++
else
CAPILIBNAME = $(CAPILIBPATH)/libcadp_capi.so
CryptoDataUtilityLIBNAME = $(CAPILIBPATH)/libCryptoDataUtility.so
endif


all: init kmip

init:
ifeq (,$(wildcard $(CAPILIBNAME)))
	$(info $(CAPILIBNAME) library not found on the provided path. Please provide the correct path.)
	@exit 101
endif

kmip: KMIPCreate KMIPRegisterSymmetricKey KMIPRegisterAsymmetricKey KMIPRegisterCertificate KMIPRegisterTemplate KMIPRegisterSecretData KMIPRegisterPrivateKey KMIPRegisterPublicKey KMIPRegisterCustomBigInt KMIPQuery KMIPLocate KMIPCrypto KMIPCrypto_RSA KMIPCrypto_AES_GCM KMIPGet KMIPGetAttributes KMIPDestroy KMIPModifyAttribute KMIPAddAttribute KMIPCryptoSinglePart KMIPGetAttributeList KMIPDeleteAttribute KMIPBatching KMIPGetCustomAttribute KMIPSetDate KMIPRevoke KMIPCreateKeyPair KMIPGetWrappedKey KMIPDiscoverVersion KMIPReKey KMIPReKeyPair

KMIPCreate: KMIPCreate.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPCreate KMIPCreate.o KMIPMisc.o $(CAPILIBNAME) $(LIBS)
KMIPModifyAttribute: KMIPModifyAttribute.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPModifyAttribute KMIPModifyAttribute.o KMIPMisc.o $(CAPILIBNAME) $(LIBS)
KMIPAddAttribute: KMIPAddAttribute.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPAddAttribute KMIPAddAttribute.o KMIPMisc.o $(CAPILIBNAME) $(LIBS)
KMIPRegisterSymmetricKey: KMIPRegisterSymmetricKey.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPRegisterSymmetricKey KMIPRegisterSymmetricKey.o KMIPMisc.o $(CAPILIBNAME) $(LIBS)
KMIPRegisterTemplate: KMIPRegisterTemplate.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPRegisterTemplate KMIPRegisterTemplate.o KMIPMisc.o $(CAPILIBNAME) $(LIBS)
KMIPRegisterSecretData: KMIPRegisterSecretData.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPRegisterSecretData KMIPRegisterSecretData.o KMIPMisc.o  $(CAPILIBNAME) $(LIBS)
KMIPRegisterPrivateKey: KMIPRegisterPrivateKey.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPRegisterPrivateKey KMIPRegisterPrivateKey.o KMIPMisc.o  $(CAPILIBNAME) $(LIBS)
KMIPRegisterPublicKey: KMIPRegisterPublicKey.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPRegisterPublicKey KMIPRegisterPublicKey.o KMIPMisc.o  $(CAPILIBNAME) $(LIBS)
KMIPQuery: KMIPQuery.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPQuery KMIPQuery.o KMIPMisc.o $(CAPILIBNAME) $(LIBS)
KMIPLocate: KMIPLocate.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPLocate KMIPLocate.o KMIPMisc.o  $(CAPILIBNAME) $(LIBS)
KMIPCrypto: KMIPCrypto.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPCrypto KMIPCrypto.o KMIPMisc.o  $(CAPILIBNAME) $(LIBS)
KMIPCrypto_RSA: KMIPCrypto_RSA.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPCrypto_RSA KMIPCrypto_RSA.o KMIPMisc.o  $(CAPILIBNAME) $(LIBS)
KMIPCrypto_AES_GCM: KMIPCrypto_AES_GCM.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPCrypto_AES_GCM KMIPCrypto_AES_GCM.o KMIPMisc.o  $(CAPILIBNAME) $(LIBS)
KMIPGet: KMIPGet.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPGet KMIPGet.o KMIPMisc.o  $(CAPILIBNAME) $(LIBS)
KMIPGetAttributes: KMIPGetAttributes.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPGetAttributes KMIPGetAttributes.o KMIPMisc.o $(CAPILIBNAME) $(LIBS)
KMIPGetAttributeList: KMIPGetAttributeList.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPGetAttributeList KMIPGetAttributeList.o KMIPMisc.o $(CAPILIBNAME) $(LIBS)
KMIPDestroy: KMIPDestroy.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPDestroy KMIPDestroy.o KMIPMisc.o $(CAPILIBNAME) $(LIBS)
KMIPDeleteAttribute: KMIPDeleteAttribute.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPDeleteAttribute KMIPDeleteAttribute.o KMIPMisc.o $(CAPILIBNAME) $(LIBS)
KMIPRegisterCustomBigInt: KMIPRegisterCustomBigInt.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPRegisterCustomBigInt KMIPRegisterCustomBigInt.o KMIPMisc.o $(CAPILIBNAME) $(LIBS)
KMIPCryptoSinglePart: KMIPCryptoSinglePart.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPCryptoSinglePart KMIPCryptoSinglePart.o KMIPMisc.o $(CAPILIBNAME) $(LIBS)
KMIPBatching: KMIPBatching.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPBatching KMIPBatching.o KMIPMisc.o $(CAPILIBNAME) $(LIBS)
KMIPRegisterAsymmetricKey: KMIPRegisterAsymmetricKey.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPRegisterAsymmetricKey KMIPRegisterAsymmetricKey.o KMIPMisc.o $(CAPILIBNAME) $(LIBS)
KMIPRegisterCertificate: KMIPRegisterCertificate.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPRegisterCertificate KMIPRegisterCertificate.o KMIPMisc.o $(CAPILIBNAME) $(LIBS)
KMIPGetCustomAttribute: KMIPGetCustomAttribute.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPGetCustomAttribute KMIPGetCustomAttribute.o KMIPMisc.o $(CAPILIBNAME) $(LIBS)
KMIPSetDate: KMIPSetDate.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPSetDate KMIPSetDate.o KMIPMisc.o  $(CAPILIBNAME) $(LIBS)
KMIPRevoke: KMIPRevoke.o  KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPRevoke KMIPRevoke.o KMIPMisc.o  $(CAPILIBNAME) $(LIBS)
KMIPCreateKeyPair: KMIPCreateKeyPair.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPCreateKeyPair KMIPCreateKeyPair.o KMIPMisc.o  $(CAPILIBNAME) $(LIBS)
KMIPGetWrappedKey: KMIPGetWrappedKey.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPGetWrappedKey KMIPGetWrappedKey.o KMIPMisc.o  $(CAPILIBNAME) $(LIBS)
KMIPDiscoverVersion: KMIPDiscoverVersion.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPDiscoverVersion KMIPDiscoverVersion.o KMIPMisc.o $(CAPILIBNAME) $(LIBS)
KMIPReKey: KMIPReKey.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPReKey KMIPReKey.o KMIPMisc.o $(CAPILIBNAME) $(LIBS)
KMIPReKeyPair: KMIPReKeyPair.o KMIPMisc.o $(CAPILIBNAME)
	$(CC) -o KMIPReKeyPair KMIPReKeyPair.o KMIPMisc.o $(CAPILIBNAME) $(LIBS)

binaries = KMIPCreate KMIPRegisterSymmetricKey KMIPRegisterAsymmetricKey KMIPRegisterCertificate KMIPRegisterTemplate KMIPRegisterSecretData KMIPRegisterPrivateKey KMIPRegisterPublicKey KMIPQuery KMIPLocate KMIPCrypto KMIPCrypto_RSA KMIPCrypto_AES_GCM KMIPGet KMIPGetAttributes KMIPDestroy KMIPRegisterCustomBigInt KMIPModifyAttribute KMIPAddAttribute KMIPCryptoSinglePart KMIPGetAttributeList KMIPDeleteAttribute KMIPBatching KMIPGetCustomAttribute KMIPSetDate KMIPRevoke KMIPCreateKeyPair KMIPGetWrappedKey KMIPDiscoverVersion KMIPReKey KMIPReKeyPair

clean:
	rm -f $(binaries) *.o
