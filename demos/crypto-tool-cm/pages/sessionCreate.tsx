import React from "react";
import axios from 'axios';
import { ToastContainer, toast } from "react-toastify";
import { useRouter } from "next/router";
import 'react-toastify/dist/ReactToastify.css';

export default function SessionCreate() {
    const router = useRouter();

    const submitContact = async (event) => {
        event.preventDefault();
        let payload = {
            name: event.target.sessionName.value,
            ip: event.target.cmIP.value,
            username: event.target.username.value,
            password: event.target.password.value
        }
        console.log(payload)
        axios.post('/api/sessions/add', payload).then(response => {
            console.log(response.data)
            let sessions = localStorage.getItem('sessions');
            if (sessions !== null) {
                var obj = JSON.parse(sessions);
                let keyExists = false
                obj.forEach(function(session) {
                    if(session['name'] === event.target.sessionName.value) {
                        keyExists = true;
                    } else {
                        keyExists = false;
                    }
                });
                console.log(keyExists);
                
                if(keyExists){
                    console.log("session name already exists");
                    toast('Session "' + event.target.sessionName.value + '" already exists', { hideProgressBar: true, autoClose: 2000, type: 'error', position:'top-right' })
                } else {
                    obj.push(response.data)
                    localStorage.setItem('sessions', JSON.stringify(obj))
                    toast('Session added succesfully...redirecting now!', { hideProgressBar: true, autoClose: 2000, type: 'success', position:'top-right' })
                    setTimeout(() => {
                        router.push('/sessions');
                    }, 2000);
                }
            } else {
                var session = [response.data]
                localStorage.setItem('sessions', JSON.stringify(session))
                toast('Session added succesfully...redirecting now!', { hideProgressBar: true, autoClose: 2000, type: 'success', position:'top-right' })
                setTimeout(() => {
                    router.push('/sessions');
                }, 2000);
            }
        })
      };
    return (
      <>
        <h1 className="text-l">
            Create Session
        </h1>
        <ToastContainer />
        <form onSubmit={submitContact}>
        <div className="mt-8 flex flex-col xl:w-3/5 lg:w-1/2 md:w-1/2 w-full">
            <label htmlFor="sessionName" className="pb-2 text-sm font-bold text-gray-800 dark:text-gray-100">
                Session Name
            </label>
            <input type={"text"} id="sessionName" name="sessionName" required 
                className="bg-gray-700 border border-gray-300 dark:border-gray-700 pl-3 py-3 shadow-sm rounded text-sm focus:outline-none focus:border-indigo-700 resize-none placeholder-gray-500 text-gray-500 dark:text-gray-400 w-full" 
                defaultValue={""} />
        </div>
        <div className="mt-8 flex flex-col xl:w-3/5 lg:w-1/2 md:w-1/2 w-full">
            <label htmlFor="cmIP" className="pb-2 text-sm font-bold text-gray-800 dark:text-gray-100">
                CipherTrust Manager IP/FQDN
            </label>
            <input type={"text"} id="cmIP" name="cmIP" required 
                className="bg-gray-700 border border-gray-300 dark:border-gray-700 pl-3 py-3 shadow-sm rounded text-sm focus:outline-none focus:border-indigo-700 resize-none placeholder-gray-500 text-gray-500 dark:text-gray-400 w-full" 
                placeholder="https://10.10.10.10"
                defaultValue={""} />
        </div>
        <div className="mt-8 flex flex-col xl:w-3/5 lg:w-1/2 md:w-1/2 w-full">
            <label htmlFor="username" className="pb-2 text-sm font-bold text-gray-800 dark:text-gray-100">
                Username
            </label>
            <input type={"text"} id="username" name="username" required 
                className="bg-gray-700 border border-gray-300 dark:border-gray-700 pl-3 py-3 shadow-sm rounded text-sm focus:outline-none focus:border-indigo-700 resize-none placeholder-gray-500 text-gray-500 dark:text-gray-400 w-full" 
                defaultValue={""} />
        </div>
        <div className="mt-8 flex flex-col xl:w-3/5 lg:w-1/2 md:w-1/2 w-full">
            <label htmlFor="password" className="pb-2 text-sm font-bold text-gray-800 dark:text-gray-100">
                Username
            </label>
            <input type={"password"} id="password" name="password" required 
                className="bg-gray-700 border border-gray-300 dark:border-gray-700 pl-3 py-3 shadow-sm rounded text-sm focus:outline-none focus:border-indigo-700 resize-none placeholder-gray-500 text-gray-500 dark:text-gray-400 w-full" 
                defaultValue={""} />
        </div>
        <div className="mt-8 flex flex-col w-40">
            <button type="submit" className="bg-gray-700 rounded p-2 text-white">
                Add Session
            </button>
        </div>
        
        </form>
      </>
    )
  }