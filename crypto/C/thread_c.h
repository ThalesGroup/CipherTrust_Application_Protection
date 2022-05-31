/*
 * thread_c.h 
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 */

#ifndef THREAD_C_H
#define THREAD_C_H

#ifndef UNIX
#include <windows.h>
#include <process.h>
#else
#include <pthread.h>
#endif

#ifndef UNIX
    typedef HANDLE ThreadHandle;
    typedef unsigned (__stdcall *THREADFUNCTION)(void *arg1);
#else
    typedef pthread_t ThreadHandle;
    typedef void* (*THREADFUNCTION)(void *arg1);
#endif


void Thread_CreateThread(ThreadHandle *handle, THREADFUNCTION threadFunction, void *arg);
void Thread_Run(ThreadHandle threadHandle);
unsigned int Thread_Join(ThreadHandle threadHandle);
void Thread_CloseHandles(ThreadHandle threadHandle);
int Thread_ThreadId();

#endif
