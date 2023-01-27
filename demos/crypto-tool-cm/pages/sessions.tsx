import { useRouter } from "next/router";
import axios from 'axios';
import React, {useEffect, useState} from "react";

export default function Sessions() {
    const [sessions, setSessions] = useState([]);
    const router = useRouter();

    const redirect = () =>{
            router.push('/sessionCreate');
    }

    const renewSession = (index) => {
        let pointer=0;
        console.log(index);
        var sessionsArr = JSON.parse(localStorage.getItem('sessions'));
        for(let i = 0; i < sessionsArr.length; i++) {
            if(sessionsArr[i].name === index) {
                pointer=i;    
            }
        }
        let payload = {
            name: sessionsArr[pointer].name,
            ip: sessionsArr[pointer].ip,
            refresh_token: sessionsArr[pointer].refresh_token
        }
        axios.post('/api/sessions/refresh', payload).then(response => {
            console.log(response)
            var newSessionsList = []
            newSessionsList.push(response.data)
            localStorage.removeItem('sessions');
            localStorage.setItem('sessions', JSON.stringify(newSessionsList));
        });
    }

    const deleteSession = (index) => {
        console.log(index);
        var sessionsArr = JSON.parse(localStorage.getItem('sessions'));
        for(let i = 0; i < sessionsArr.length; i++) {
            if(sessionsArr[i].name === index) {
                sessionsArr.splice(i, 1);
            }
        }
        localStorage.setItem('sessions', JSON.stringify(sessionsArr));
        router.reload();
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

    var i=0;

    return (
    <div className="flex flex-col">
        <div className="overflow-x-auto">
            <div className="p-1.5 w-full inline-block align-middle">
                <button className="bg-gray-700 rounded p-2 text-white" onClick={redirect}>
                    Add Session
                </button>
            </div>
            <div className="p-1.5 w-full inline-block align-middle">
                <div className="overflow-hidden border rounded-lg">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th
                                    scope="col"
                                    className="px-6 py-3 text-xs font-bold text-left text-gray-500 uppercase "
                                >
                                    Name
                                </th>
                                <th
                                    scope="col"
                                    className="px-6 py-3 text-xs font-bold text-right text-gray-500 uppercase "
                                >
                                    Renew
                                </th>
                                <th
                                    scope="col"
                                    className="px-6 py-3 text-xs font-bold text-right text-gray-500 uppercase "
                                >
                                    Delete
                                </th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                        {Object.entries(rows).map((entry) => {
                            const row = entry[0];
                            const details = entry[1];
                            return(
                                <tr>
                                    <td className="px-6 py-4 text-sm text-gray-800 whitespace-nowrap">
                                        {row}
                                    </td>
                                    <td className="px-6 py-4 text-sm font-medium text-right whitespace-nowrap">
                                        <button className="bg-gray-700 rounded p-2 text-white" onClick={() => renewSession(row)}>
                                            Refresh Token
                                        </button>
                                    </td>
                                    <td className="px-6 py-4 text-sm font-medium text-right whitespace-nowrap">
                                        <button className="bg-red-700 rounded p-2 text-white" onClick={() => deleteSession(row)}>
                                            Delete Session
                                        </button>
                                    </td>
                                </tr>
                            )
                            i=i+1;
                        })}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    );
  }