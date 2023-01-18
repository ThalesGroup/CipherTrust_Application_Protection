import React, {useEffect, useState} from "react";
import axios from 'axios';

export default function Encrypt() {
    const [sessions, setSessions] = useState([]);
    const [random, setRandom] = useState("");

    const submitContact = async (event) => {
        event.preventDefault();
        const params = event.target.session.value.split("___");
        let payload = {
            ip: params[0],
            jwt: params[1]
        }
        axios.post('/api/crypto/rand', payload).then(response => {
            console.log(response.data)
            setRandom(response.data.data.bytes);
        });
    }

    useEffect(() => {
        if(localStorage.getItem('sessions') !== null) {
            setSessions(JSON.parse(localStorage.getItem('sessions')));
        }
    },[]);

    const rows = {};
    for (const session of sessions) {
        if (session.name in rows) {
          rows[session.name].push(session);
        } else {
          rows[session.name] = [session];
        }
    }
    return (
      <>
        <h1 className="text-l">
            Randomly Generated Data
        </h1>
        <form onSubmit={submitContact}>
        <div className="mt-8 flex">
            <div className="flex flex-col xl:w-1 lg:w-1 md:w-1 w-1 ml-3">
                <div className="bg-orange-100 h-full rounded p-2 font-sans text-sm font-semibold">
                    output: {random}
                </div>
            </div>
        </div>
        <div className="mt-8 flex flex-col xl:w-3/5 lg:w-1/2 md:w-1/2 w-full">
            <label htmlFor="session" className="pb-2 text-sm font-bold text-gray-800 dark:text-gray-100">
                Select CM Session
            </label>
            <select  id="session" name="session"
            className="block appearance-none w-full bg-gray-700 border border-gray-300 text-white py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-gray-700 focus:border-gray-300">
                <option value="">--Select CipherTrust Manager Session--</option>
                {Object.entries(rows).map((entry) => {
                    const row = entry[0];
                    const details = entry[1];
                    return(
                        <option key={row} value={details[0].ip + '___' + details[0].jwt}>{row}</option>
                    )
                })}
            </select>
        </div>
        <div className="mt-8 flex flex-col w-40">
            <button className="bg-gray-700 rounded p-2 text-white">
                Generate
            </button>
        </div>
        </form>
      </>
    )
  }