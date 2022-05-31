/*
 * thread.h 
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 */

#ifndef SYSDEP_BASETHREAD_H
#define SYSDEP_BASETHREAD_H

#include "criticalMutex.h"

#ifdef UNIX
#include <pthread.h>
#else
#include <windows.h>
#include <process.h>
#endif

extern "C" void * BaseThread_startup(void *arg);

class BaseThread {
public:
	typedef void *(*ThreadRoutine)(void *, void *);
#ifdef UNIX
	typedef pthread_t ThreadHandle;
	typedef void *ThreadRoutineParam;
#else
	typedef HANDLE ThreadHandle;
	typedef LPVOID ThreadRoutineParam;
#endif

	typedef enum 
	    { THREAD_NONE, THREAD_INITIALIZED, THREAD_RUNNING, THREAD_COMPLETE, 
		THREAD_EXIT, THREAD_FATAL, THREAD_SHUTDOWN } ThreadState;
            
        friend void * BaseThread_startup(void *arg);

private:
	CriticalMutex _mutex;
	BaseThread();
	BaseThread(const BaseThread &);
	BaseThread &operator=(BaseThread &);
#ifndef UNIX
	unsigned _threadID;
#endif

	ThreadState _state;
	bool _detached;


protected:
	ThreadRoutine _routine;
	ThreadRoutineParam _param1;
	ThreadRoutineParam _param2;
	ThreadHandle _handle;

#if defined(UNIX)
	static void *startup(void *);
#else 
	static unsigned __stdcall startup(void *);
#endif

public:
	BaseThread(ThreadRoutine routine, 
		ThreadRoutineParam param1 = NULL,
		ThreadRoutineParam param2 = NULL);

	virtual ~BaseThread();

	virtual bool init(bool detached = false);
	void run();
	unsigned int join();

	ThreadState getState() const { return _state; }
	void setState(ThreadState state) { _state = state;}

	static int threadid();
	bool isDetached() const { return _detached; }

};

#endif
