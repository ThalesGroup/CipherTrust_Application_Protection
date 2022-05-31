/*
 * criticalMutex.h
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 */

#ifndef SYSDEP_MUTEX_H
#define SYSDEP_MUTEX_H

#ifdef UNIX
#include <pthread.h>
#else // Windows
#include <windows.h>
#endif

#ifdef UNIX
typedef pthread_mutex_t *MutexHandle;
typedef pthread_mutex_t MutexType;
#else
typedef LPCRITICAL_SECTION MutexHandle;
typedef CRITICAL_SECTION MutexType;
#endif

class CriticalMutex
{
    private:
	CriticalMutex( const CriticalMutex& ) ;
	CriticalMutex& operator=( const CriticalMutex& ) ;

    public:
	CriticalMutex () ;
	~CriticalMutex () ;

	int	lock () ;
	int	unLock () ;
#ifndef UNIX
#if(_WIN32_WINNT >= 0x0400)
	bool	tryLock () ;
#endif
#elif UNIX
	bool tryLock();
#endif

	MutexHandle	getCriticalMutex()
	{
	    return &_mutex ;
	}

#ifdef UNIX
	int	condWait( pthread_cond_t *cond, int timeToWait = -1 ) ;
#endif

    private:
	MutexType		_mutex ;

} ;


class SmartMutex
{
    private:
	SmartMutex() ;
	SmartMutex( const SmartMutex& ) ;
	SmartMutex& operator=( const SmartMutex& ) ;

	CriticalMutex	&_mutex ;

    public:

	SmartMutex( CriticalMutex& mutex ) ;
	virtual ~SmartMutex () ;
} ;

#endif

