import React, { useState, useEffect } from 'react';
import jwt_decode from "jwt-decode";

async function createAccount(AccDetails) {
    console.log(JSON.stringify(AccDetails))
    return fetch('http://localhost:8081/api/proxy/account', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(AccDetails)
    }).then(data => data.json())
}

export default function CreateAccount() {
    let token = sessionStorage.getItem('token');
    var decodedToken = jwt_decode(token);
    
    const [fullName, setFullName] = useState();
    const [mobileNumber, setMobileNumber] = useState();
    const [dob, setDob] = useState();
    const [ssn, setSsn] = useState();
    const [accFriendlyName, setAccFriendlyName] = useState();
    const cmID = decodedToken.sub;
    const userName = decodedToken.preferred_username;

    useEffect(() => {});

    const handleSubmit = async event => {
        event.preventDefault();
        const Account_details = await createAccount({
            ssn,
            dob,
            fullName,
            userName,
            mobileNumber,
            cmID,
            accFriendlyName
        });
        console.log(Account_details);
      };
    return(
        <div className="container px-6 mx-auto">
        <div className="rounded shadow relative bg-white z-10 -mt-8 mb-8 w-full">

            <div>
            <div className="flex flex-no-wrap items-start">
            <div className="w-full ">
                <div className="py-4 px-2">
                <div>
                    <div className="mt-10 px-7">
                    <p className="text-xl font-semibold leading-tight text-gray-800">
                        Account Details
                    </p>
                    <div className="grid w-full grid-cols-1 lg:grid-cols-2 md:grid-cols-1 gap-7 mt-7 ">                        
                        <div>
                            <p className="text-base font-medium leading-none text-gray-800">
                                Username
                            </p>
                            <input 
                            className="w-full p-3 mt-4 border border-gray-300 rounded outline-none focus:bg-gray-50"
                            value={decodedToken.preferred_username}
                            disabled={true}
                            />
                            <p className="mt-3 text-xs leading-3 text-gray-600">
                                Your Ciphertrust Manager Username
                            </p>
                        </div>
                        <div>
                            <p className="text-base font-medium leading-none text-gray-800">
                                SSN
                            </p>
                            <input 
                            className="w-full p-3 mt-4 border border-gray-300 rounded outline-none focus:bg-gray-50"
                            type="password"
                            onChange={e => setSsn(e.target.value)}
                            />
                            <p className="mt-3 text-xs leading-3 text-gray-600">
                                Your data will remain secure as per PCC compliance requirements
                            </p>
                        </div>

                        <div>
                            <p className="text-base font-medium leading-none text-gray-800">
                                Full Name
                            </p>
                            <input 
                            className="w-full p-3 mt-4 border border-gray-300 rounded outline-none focus:bg-gray-50"
                            onChange={e => setFullName(e.target.value)}
                            />
                        </div>
                        <div>
                            <p className="text-base font-medium leading-none text-gray-800">
                                Contact Number
                            </p>
                            <input 
                            className="w-full p-3 mt-4 border border-gray-300 rounded outline-none focus:bg-gray-50"
                            onChange={e => setMobileNumber(e.target.value)}
                            />
                            <p className="mt-3 text-xs leading-3 text-gray-600">
                                Your data will remain secure as per PCC compliance requirements
                            </p>
                        </div>

                        <div>
                            <p className="text-base font-medium leading-none text-gray-800">
                                Date Of Birth
                            </p>
                            <input 
                            className="w-full p-3 mt-4 border border-gray-300 rounded outline-none focus:bg-gray-50"
                            type="Date"
                            onChange={e => setDob(e.target.value)}
                            />
                            <p className="mt-3 text-xs leading-3 text-gray-600">
                                Your data will remain secure as per PCC compliance requirements
                            </p>
                        </div>
                        <div>
                            <p className="text-base font-medium leading-none text-gray-800">
                                Friendly Name for the Account
                            </p>
                            <input 
                            className="w-full p-3 mt-4 border border-gray-300 rounded outline-none focus:bg-gray-50"
                            onChange={e => setAccFriendlyName(e.target.value)}
                            />
                        </div>
                    </div>
                    </div>
                    
                    <hr className="h-[1px] bg-gray-100 my-14" />
                    <div className="flex flex-col flex-wrap items-center justify-center w-full px-7 lg:flex-row lg:justify-end md:justify-end gap-x-4 gap-y-4">
                    <button className="bg-white border-indigo-700 rounded hover:bg-gray-50 transform duration-300 ease-in-out text-sm font-medium px-6 py-4 text-indigo-700 border lg:max-w-[95px]  w-full ">
                        Cancel
                    </button>
                    <button 
                        className="bg-indigo-700 rounded hover:bg-indigo-600 transform duration-300 ease-in-out text-sm font-medium px-6 py-4 text-white lg:max-w-[144px] w-full "
                        onClick={handleSubmit}
                    >
                        Create
                    </button>
                    </div>
                </div>
                </div>
            </div>
            </div>
        </div>
        </div>
        </div>
    );
}