/*
 * criticalMutex.cc
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 */


#ifdef UNIX 
#include "criticalMutex.h"
#include <sys/time.h>
#include <unistd.h>
#include <pthread.h>
#else // Windows
#include <windows.h>
#include "criticalMutex.h"
#endif

CriticalMutex::CriticalMutex()
{
#ifdef UNIX
    pthread_mutex_init( &_mutex, NULL ) ;
#else
    InitializeCriticalSection(&_mutex);
#endif
}

CriticalMutex::~CriticalMutex()
{
#ifdef UNIX
    if ( pthread_mutex_destroy( &_mutex ) != 0 )
    {
	// Log the error.
	// errno is EBUSY of this CriticalMutex is used by another thread and
	// is LOCKED.
    }
#else
    DeleteCriticalSection(&_mutex);
#endif

}

int
CriticalMutex::lock ()
{
#ifdef UNIX
    return ( pthread_mutex_lock( &_mutex ) ) ;
#else
    EnterCriticalSection(&_mutex);
    return 0;
#endif
    
}

int
CriticalMutex::unLock ()
{
#ifdef UNIX
    return ( pthread_mutex_unlock( &_mutex ) ) ;
#else
    LeaveCriticalSection(&_mutex);
    return 0;
#endif
}
#ifndef UNIX
#if(_WIN32_WINNT >= 0x0400)
bool
CriticalMutex::tryLock ()
{
    return TryEnterCriticalSection(&_mutex);
}
#endif
#elif UNIX
bool
CriticalMutex::tryLock ()
{
    return ( pthread_mutex_trylock( &_mutex ) == 0 ? true : false ) ;
}
#endif

#ifdef UNIX
int CriticalMutex::condWait( pthread_cond_t *condVar, int timeToWait )
{
    struct timeval 	currTime ;
    struct timespec	timeSpec ;

    gettimeofday( &currTime, NULL) ;

    // Default value of method is -1 -> Means infinite wait.
    timeSpec.tv_sec = currTime.tv_sec + timeToWait ;
    timeSpec.tv_nsec = currTime.tv_usec * 1000 ;

    int retCode = 0 ;
    if ( timeToWait < 0 )
	retCode = pthread_cond_wait( condVar, &_mutex ) ;
    else
	retCode = pthread_cond_timedwait( condVar, &_mutex, &timeSpec ) ;

    return retCode ;
}
#endif


SmartMutex::SmartMutex( CriticalMutex& mutex )
    : _mutex(  mutex )
{
    (void)_mutex.lock();
}


SmartMutex::~SmartMutex()
{
    (void)_mutex.unLock() ;
}
