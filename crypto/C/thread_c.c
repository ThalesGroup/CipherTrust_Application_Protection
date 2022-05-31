/*
 * thread_c.c    
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 */

#include "thread_c.h"


void
Thread_CreateThread(ThreadHandle *handle, THREADFUNCTION threadFunction, void *arg )
{
#ifndef UNIX
    unsigned threadID;
    *handle = (ThreadHandle)_beginthreadex(NULL, 0, threadFunction, arg,
                                  CREATE_SUSPENDED, &threadID);
#else
    pthread_attr_t pthattr0;
    pthread_attr_init(&pthattr0);

    pthread_attr_setdetachstate(&pthattr0, PTHREAD_CREATE_JOINABLE);

    int r = pthread_create( handle, &pthattr0, threadFunction, arg );
    if ( r != 0 )
    {
        handle = 0;
    }
#endif
}

void
Thread_Run(ThreadHandle threadHandle)
{
#ifndef UNIX
    ResumeThread(threadHandle);
#endif
}

unsigned int
Thread_Join(ThreadHandle threadHandle)
{
#ifndef UNIX
    DWORD result = 0;

    WaitForSingleObject(threadHandle, INFINITE);     

    GetExitCodeThread(threadHandle, &result);

    return result;
#else
    return pthread_join(threadHandle, NULL);
#endif
}

void Thread_CloseHandles(ThreadHandle threadHandle)
{
#ifndef UNIX
    CloseHandle(threadHandle);
#endif
}

int Thread_ThreadId()
{
#ifndef UNIX
    return (int) GetCurrentThreadId();
#else
    return (int) pthread_self();
#endif
}
