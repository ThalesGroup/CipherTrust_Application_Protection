/*

   fpe.h

*/

#ifndef _FPE_H_
#define _FPE_H_

#define CS_ASCII   0
#define CS_UTF8    1
#define CS_UTF16LE 2
#define CS_UTF16BE 3
#define CS_UTF32LE 4
#define CS_UTF32BE 5

#define MAX_CHARSET_LEN_UTF 65535
#define MAX_CHARSET_LEN_ASCII 255


#ifndef CK_PTR
#define CK_PTR *
#endif
#include "pkcs11t.h"

#define CKM_VORMETRIC_FPE              0x80004001
#define CKM_THALES_FPE                 0x80004001
#define CKM_THALES_FF1                 0x80004002
#define CKM_THALES_FF3_1               0x80004003
#define CKR_RADIX_TOO_LARGE            0x00000300

typedef struct FPE_PARAMETER {
  CK_BYTE     tweak[8];
  CK_BYTE     radix;         /* 2..255. If this byte is set to 1, this is actually the FPE_PARAMETER_UTF structure (see below) */
  CK_BYTE     charset[255];
} CK_FPE_PARAMETER;

typedef struct FPE_PARAMETER_UTF {
  CK_BYTE        tweak[8];
  CK_BYTE        mode;       /* 1 denotes UTF mode, 2..255 denotes the legacy ASCII mode radix, see above */
  CK_BYTE        utfmode;    /* 1...UTF8, 2...UTF16LE, 3...UTF16BE, 4...UTF32LE, 5...UTF32BE */
  unsigned short radix;      /* radix in network byte order, 2..65535 */
  unsigned       charsetlen; /* length of character set data in bytes, in network byte order */
  CK_BYTE        charset[4*65535];
} CK_FPE_PARAMETER_UTF;

typedef struct FF1_PARAMETER_UTF {
  unsigned       charsetlen; /* length of character set data in bytes, in network byte order */
  unsigned       tweaklen;   /* length of tweak data in bytes, in network byte order */
  unsigned short radix;      /* radix in network byte order, 2..65535 */
  CK_BYTE        utfmode;    /* 0...ASCII, 1...UTF8, 2...UTF16LE, 3...UTF16BE, 4...UTF32LE, 5...UTF32BE */
  CK_BYTE        charset[4*65536]; /* this is an open array with a minimum length of 2 bytes and a theoretical maximum length of 65535*4 bytes */
  /* tweak data is optional - if present, it immediately follows the charset data (within the charset array) */
} CK_FF1_PARAMETER_UTF;



#if defined(_AIX) || defined(__hpux) || defined(__sun) || defined(__s390x__)
#define _BIGENDIAN
#define myhtonl(x)  x
#define myhtons(x)  x
#else
#define _LITTLEENDIAN
#define myhtonl(x)  ((x>>24) + ((x>>8)&0xFF00) + ((x<<8)&0xFF0000) + ((x&0xFF)<<24))
#define myhtons(x)  ((x>>8) + ((x&0xFF)<<8))
#ifdef _MSC_VER
#define _LITTLEENDIAN_MSC
#else
#define _LITTLEENDIAN_GCC
#endif
#endif

#if defined(__sun) || defined(__hpux)
#include <sys/byteorder.h>
#endif
#include <string.h>
#include <memory.h>

#ifndef _MSC_VER
#define min(a,b) ((a<b) ? a : b)
#endif

#ifdef _LITTLEENDIAN_GCC
#include <netinet/in.h>
#include <signal.h>
#endif

#ifndef _MSC_VER
#include <dlfcn.h>
#endif

#define __PASTE(x,y)      x##y

#endif
