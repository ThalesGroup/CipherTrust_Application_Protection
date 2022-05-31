/*
 * thread.cc
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 */

#include <stdlib.h>
#include <string.h>
#include "thread.h"
#ifdef UNIX
#include <unistd.h>
#endif

BaseThread::BaseThread(ThreadRoutine routine, ThreadRoutineParam param1,
		       ThreadRoutineParam param2)
    : _state(THREAD_NONE), _routine(routine), _param1(param1), _param2(param2)
{
    _detached = false;
}

BaseThread::~BaseThread()
{
#ifndef UNIX
	CloseHandle(_handle);
#endif
}

bool
BaseThread::init(bool detached)
{
    bool retval = true;
#ifdef UNIX
    pthread_attr_t pthattr0;
    _mutex.lock();
    pthread_attr_init(&pthattr0);

    int r = pthread_create( &_handle, &pthattr0, startup, this );
    if ( r != 0 )
    {
	_state = THREAD_NONE;
	retval = false;
    }
#else // UNIX
    _handle = (ThreadHandle)_beginthreadex(NULL, 0, startup, this,
                                                                  CREATE_SUSPENDED, &_threadID);
    if ( !_handle )
    {
	_state = THREAD_NONE;
	retval = false;
    }
#endif // UNIX
    if ( retval)
        _state = THREAD_INITIALIZED;
        
    return retval;
}

#if defined(UNIX)
void *
#else 
unsigned _stdcall
#endif
BaseThread::startup(void *arg)
{
	BaseThread *bt = (BaseThread*)arg;
#ifdef UNIX
	bt->_mutex.lock();
	bt->_mutex.unLock();
#endif
	bt->_routine(bt->_param1, bt->_param2);
	return 0;
}

void
BaseThread::run()
{
#ifdef UNIX
	_mutex.unLock();
#else
	ResumeThread(_handle);
#endif
	_state = THREAD_RUNNING;
}

unsigned int
BaseThread::join()
{
#ifdef UNIX
    if ( _detached )
	return 0;
    int retval = pthread_join(_handle, NULL);
	return retval;
#else
    WaitForSingleObject(_handle, INFINITE);

    DWORD result;
    GetExitCodeThread(_handle, &result);

    return result;
#endif
}

int BaseThread::threadid()
{
#if defined(UNIX)
    #if defined(OS_Darwin)
	return sysconf(_SC_PAGE_SIZE);
    #else
	return (int) pthread_self();
    #endif
#else
    return (int) GetCurrentThreadId();
#endif
}
