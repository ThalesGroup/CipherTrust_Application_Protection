import React, {useEffect, useState} from "react";
import axios from 'axios';

export default function Encrypt() {
    const [sessions, setSessions] = useState([]);
    const [selected, setSelected] = useState("");
    const [data, setData] = useState([]);
    const [signedText, setSignedText] = useState("");

    let options=[];
    const submitContact = async (event) => {
        event.preventDefault();
        const params = event.target.session.value.split("___");
        let payload = {
            keyName: event.target.key2.value,
            signAlgo: event.target.signAlgo.value,
            hashAlgo: event.target.hashAlgo.value,
            unsignedData: event.target.unsigned_data.value,
            ip: params[0],
            jwt: params[1]
        }
        console.log(payload);
        axios.post('/api/crypto/sign', payload).then(response => {
            setSignedText(response.data.data.data);
        });
    }
    const changeSelectOptionHandler = (event) => {
        const params = event.target.value.split("___");

        let payload = {            
            ip: params[0],
            jwt: params[1]
        }
        axios.post('/api/crypto/keys', payload).then(response => {
            for (const resource of response.data.data.resources) {
                options.push(<option value={resource.name}>{resource.name}</option>);
            }
            setData(options);
        });
    };

    if (selected !== "") {
        const params = selected.split("___");

        let payload = {            
            ip: params[0],
            jwt: params[1]
        }
        axios.post('/api/crypto/keys', payload).then(response => {
            //console.log(response.data)
            for (const resource of response.data.data.resources) {
                options.push(<option value={resource.name}>{resource.name}</option>);
            }
            setData(options);
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
            Sign Data
        </h1>
        <form onSubmit={submitContact}>
        <div className="mt-8 flex">
            <div className="flex flex-col xl:w-1/2 lg:w-1/2 md:w-1/2 w-1/2">
                <label htmlFor="unsigned_data" className="pb-2 text-sm font-bold text-gray-800 dark:text-gray-100">
                    Unsigned Data
                </label>
                <textarea id="unsigned_data" name="unsigned_data" required 
                className="bg-gray-700 border border-gray-300 dark:border-gray-700 pl-3 py-3 shadow-sm rounded text-sm focus:outline-none focus:border-indigo-700 resize-none placeholder-gray-500 text-gray-500 dark:text-gray-400 w-full" 
                placeholder="Data to be signed" 
                rows={5} 
                defaultValue={""} />
            </div>
            <div className="flex flex-col xl:w-1/2 lg:w-1/2 md:w-1/2 w-1/2 ml-3">
                <label className="pl-3 py-1 text-sm font-bold text-gray-800 dark:text-gray-100">
                    Signed Data
                </label>
                <div className="bg-orange-100 h-full rounded p-2 font-sans text-sm font-semibold">
                    result: {signedText}
                </div>
            </div>
        </div>
        <div className="mt-8 flex flex-col xl:w-3/5 lg:w-1/2 md:w-1/2 w-full">
            <label htmlFor="session" className="pb-2 text-sm font-bold text-gray-800 dark:text-gray-100">
                Select CM Session
            </label>
            <select  id="session" name="session" onChange={changeSelectOptionHandler}
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
        <div className="mt-8 flex flex-col xl:w-3/5 lg:w-1/2 md:w-1/2 w-full">
            <label htmlFor="key2" className="pb-2 text-sm font-bold text-gray-800 dark:text-gray-100">
                Select Key
            </label>
            <select  id="key2" name="key2"
            className="block appearance-none w-full bg-gray-700 border border-gray-300 text-white py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-gray-700 focus:border-gray-300">
                <option value="">--Select Key for Encryption--</option>
                {data}
            </select>
        </div>
        <div className="mt-8 flex flex-col xl:w-3/5 lg:w-1/2 md:w-1/2 w-full">
            <label htmlFor="signAlgo" className="pb-2 text-sm font-bold text-gray-800 dark:text-gray-100">
                Select Signing Algo
            </label>
            <select  id="signAlgo" name="signAlgo"
            className="block appearance-none w-full bg-gray-700 border border-gray-300 text-white py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-gray-700 focus:border-gray-300">
                <option value="">--Select Key Algorithm--</option>
                <option value="ECDSA">ECDSA</option>
                <option value="RSA">RSA</option>
            </select>
        </div>
        <div className="mt-8 flex flex-col xl:w-3/5 lg:w-1/2 md:w-1/2 w-full">
            <label htmlFor="hashAlgo" className="pb-2 text-sm font-bold text-gray-800 dark:text-gray-100">
                Select Hash Algo
            </label>
            <select  id="hashAlgo" name="hashAlgo"
            className="block appearance-none w-full bg-gray-700 border border-gray-300 text-white py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-gray-700 focus:border-gray-300">
                <option value="">--Select Hash Algorithm--</option>
                <option value="SHA1">SHA1</option>
                <option value="SHA-256">SHA-256</option>
                <option value="SHA-384">SHA-384</option>
                <option value="SHA-512">SHA-512</option>
                <option value="SHA3-224">SHA3-224</option>
                <option value="SHA3-256">SHA3-256</option>
                <option value="SHA3-384">SHA3-384</option>
                <option value="SHA3-512">SHA3-512</option>
                <option value="none">None</option>
            </select>
        </div>
        <div className="mt-8 flex flex-col w-40">
            <button className="bg-gray-700 rounded p-2 text-white">
                Sign
            </button>
        </div>
        </form>
      </>
    )
  }