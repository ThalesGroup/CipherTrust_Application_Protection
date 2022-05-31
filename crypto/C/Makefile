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

CAPILDIR := ..
CAPIINDIR := $(subst /lib,/include,$(CAPILDIR))

## libname might be different for different OS
## enter the path of openssl library libcrypto.a in CAPILIBNAME
LIBS += -L$(CAPILDIR)
LIBS += -lcrypto
CAPIINCLUDEDIR=../include
# set CC to point to your C compiler.
ifeq ($(OS_NAME),OS400)
CC=icc
else
CC=gcc
endif

# you can compile this with a C++ or C compiler such as gcc 
# (3.2.x or greater).
# if you have an older gcc or another C compiler, you may need to obtain 
# libstdc++.so.5 and possibly libgcc_s.so.1 from a newer gcc/g++ or 
# the ../samplelibs directory, and use the variable below point to them.
# For Bluecat, the path to the location of the library and the 
# 
# LIBS = -L/usr/share/bluecat/cdt/lib -lstdc++

# on NCR MP-RAS
# LIBS = -L../samplelibs -lstdc++ -lpthread -ldl

# For 64-bit builds (Ex: HPUX 11.11) use the 64-bit gcc and the path to the
# 64-bit libgcc.
LIBSTDC++ = -lstdc++
LIBGCC = -lgcc_s
LIBS += -lpthread -L../samplelibs $(LIBSTDC++)

# HPUX1123-32 requires this LIBS line
# LIBS = -L../samplelibs -lstdc++



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
CAPILIBNAME = ../libcadp_capi.dylib
CryptoDataUtilityLIBNAME = ../libCryptoDataUtility.dylib
CPP=g++
else
CAPILIBNAME = ../libcadp_capi.so
CryptoDataUtilityLIBNAME = ../libCryptoDataUtility.so
endif


all: crypto CryptoDataUtility


crypto: CryptoSinglePart CryptoSinglePartMultiThreadedCPP CryptoSinglePartMultiThreadedC CryptoSinglePart_Fast CryptoSinglePart_AES_GCM CryptoSinglePart_EC CryptoSinglePartBulk_Enhanced CryptoSinglePart_multitenency CryptoSinglePart_CMS

CryptoDataUtility: CryptoDataUtility.o $(CAPILIBNAME)  $(CryptoDataUtilityLIBNAME)
	$(CC) -o CryptoDataUtility CryptoDataUtility.o  $(CAPILIBNAME) $(CryptoDataUtilityLIBNAME)  $(LIBS) -lpthread

CryptoSinglePart: CryptoSinglePart.o $(CAPILIBNAME)
	$(CC) -o CryptoSinglePart CryptoSinglePart.o $(CAPILIBNAME) $(LIBS)
CryptoSinglePartBulk_Enhanced: CryptoSinglePartBulk_Enhanced.o $(CAPILIBNAME)
	$(CC) -o CryptoSinglePartBulk_Enhanced CryptoSinglePartBulk_Enhanced.o $(CAPILIBNAME) $(LIBS)

CryptoSinglePartMultiThreadedCPP: CryptoSinglePartMultiThreadedCPP.o criticalMutex.o thread.o $(CAPILIBNAME)
ifeq ($(OS_NAME),Darwin)
	$(CPP) -o CryptoSinglePartMultiThreadedCPP CryptoSinglePartMultiThreadedCPP.o criticalMutex.o thread.o  $(CAPILIBNAME) -L../lib -lcrypto -ldl
else ifeq ($(OS_NAME),SunOS)
	$(CPP) -o CryptoSinglePartMultiThreadedCPP CryptoSinglePartMultiThreadedCPP.o criticalMutex.o thread.o  $(CAPILIBNAME) $(LIBS)
else
	$(CC) -o CryptoSinglePartMultiThreadedCPP CryptoSinglePartMultiThreadedCPP.o criticalMutex.o thread.o  $(CAPILIBNAME) $(LIBS)
endif

CryptoSinglePartMultiThreadedC: CryptoSinglePartMultiThreadedC.o thread_c.o $(CAPILIBNAME)
	$(CC) -o CryptoSinglePartMultiThreadedC CryptoSinglePartMultiThreadedC.o thread_c.o  $(CAPILIBNAME) $(LIBS)

CryptoSinglePart_Fast: CryptoSinglePart_Fast.o thread_c.o $(CAPILIBNAME)
	$(CC) -o CryptoSinglePart_Fast CryptoSinglePart_Fast.o thread_c.o $(CAPILIBNAME) $(LIBS)

CryptoSinglePart_multitenency: CryptoSinglePart_multitenency.o $(CAPILIBNAME)
	$(CC) -o CryptoSinglePart_multitenency CryptoSinglePart_multitenency.o $(CAPILIBNAME) $(LIBS)

CryptoSinglePart_AES_GCM: CryptoSinglePart_AES_GCM.o $(CAPILIBNAME)
	$(CC) -o CryptoSinglePart_AES_GCM CryptoSinglePart_AES_GCM.o $(CAPILIBNAME) $(LIBS)

CryptoSinglePart_CMS: CryptoSinglePart_CMS.o $(CAPILIBNAME)
	$(CC) -o CryptoSinglePart_CMS CryptoSinglePart_CMS.o $(CAPILIBNAME) $(LIBS)

CryptoSinglePart_EC: CryptoSinglePart_EC.o $(CAPILIBNAME)
	$(CC) -o CryptoSinglePart_EC CryptoSinglePart_EC.o $(CAPILIBNAME) $(LIBS)

binaries = CryptoSinglePart CryptoSinglePartMultiThreadedCPP CryptoSinglePartMultiThreadedC CryptoSinglePart_Fast CryptoSinglePart_AES_GCM CryptoSinglePart_EC CryptoSinglePart_CMS CryptoSinglePartBulk_Enhanced CryptoSinglePart_multitenency CryptoDataUtility

clean:
	rm -f $(binaries) *.o
