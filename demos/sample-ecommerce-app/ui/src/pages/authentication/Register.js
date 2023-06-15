import React, { useState } from 'react';
import './Login.css';
import { useNavigate } from 'react-router-dom';

async function createUser(data) {
 console.log(data);
 return fetch('http://'+process.env.REACT_APP_BACKEND_IP_ADDRESS+':8080/api/user-mgmt/user/create', {
   method: 'POST',
   headers: {
     'Content-Type': 'application/json'
   },
   body: JSON.stringify(data)
 })
   .then(data => data.json())
}

export default function Register() {
  const navigate = useNavigate();
  const countries = ["Canada", "United States", "India"];
  const [menu, setMenu] = useState(false);
  const [username, setUserName] = useState();
  const [password, setPassword] = useState();
  const [mobileNum, setMobileNum] = useState();
  const [email, setEmail] = useState();
  const [fullName, setFullName] = useState();
  const [street, setStreet] = useState();
  const [unit, setUnit] = useState();
  const [city, setCity] = useState();
  const [state, setState] = useState();
  const [zipCode, setZipCode] = useState();
  const [country, setCountry] = useState();

  const changeText = (e) => {
    setMenu(false);
    setCountry(e.target.textContent);
  };

  const handleSubmit = async e => {
    e.preventDefault();

    const address = {
        unit,
        street,
        city,
        state,
        zipCode,
        country
    }
    
    const auth_response = await createUser({
      username,
      password,
      mobileNum,
      email,
      fullName,
      address
    });
    sessionStorage.removeItem('token');
    sessionStorage.removeItem('user');
    navigate('/checkout');
    
  }

  return(
    <div class="flex mb-4">
      <div class="w-1/4 h-full bg-gray-100"></div>
      <div class="w-1/2 h-full bg-gray-100">

        <div className="p-8 bg-gray-100 flex flex-col lg:w-full xl:w-full">           
            <label className="mt-8 text-base leading-4 text-gray-800">User details</label>
            <div className="mt-2 flex-col">
                <div className="flex-row flex">
                    <input className="border border-gray-300 p-4 rounded w-full text-base leading-4 placeholder-gray-600 text-gray-600" type="text" placeholder="Username" onChange={e => setUserName(e.target.value)} />
                    <input className="border border-gray-300 p-4 rounded w-full text-base leading-4 placeholder-gray-600 text-gray-600" type="password" placeholder="Password" onChange={e => setPassword(e.target.value)} />
                </div>
            </div>
            <div className="mt-2 flex-col">
                <div className="flex-row flex">
                    <input className="border border-gray-300 p-4 rounded w-full text-base leading-4 placeholder-gray-600 text-gray-600" type="email" placeholder="Email" onChange={e => setEmail(e.target.value)} />
                    <input className="border border-gray-300 p-4 rounded w-full text-base leading-4 placeholder-gray-600 text-gray-600" type="text" placeholder="Contact Number" onChange={e => setMobileNum(e.target.value)} />
                </div>
            </div>
            <div className="mt-2 flex-col">
                <div>
                    <input className="border rounded border-gray-300 p-4 w-full text-base leading-4 placeholder-gray-600 text-gray-600" type="text" placeholder="Full Name" onChange={e => setFullName(e.target.value)} />
                </div>
            </div>

            <label className="mt-8 text-base leading-4 text-gray-800">Address Details</label>
            <div className="mt-2 flex-col">
                <div className="flex-row flex">
                    <input className="border border-gray-300 p-4 rounded w-full text-base leading-4 placeholder-gray-600 text-gray-600" type="text" placeholder="Unit#" onChange={e => setUnit(e.target.value)} />
                    <input className="border border-gray-300 p-4 rounded w-full text-base leading-4 placeholder-gray-600 text-gray-600" type="text" placeholder="Street Name" onChange={e => setStreet(e.target.value)} />
                </div>
            </div>
            <div className="mt-2 flex-col">
                <div className="flex-row flex">
                    <input className="border border-gray-300 p-4 rounded w-full text-base leading-4 placeholder-gray-600 text-gray-600" type="text" placeholder="City" onChange={e => setCity(e.target.value)} />
                    <input className="border border-gray-300 p-4 rounded w-full text-base leading-4 placeholder-gray-600 text-gray-600" type="text" placeholder="State Name" onChange={e => setState(e.target.value)} />
                </div>
            </div>
            <div className="mt-2 flex-col">
                <div className="relative">
                    <button className="text-left border rounded-tr rounded-tl border-gray-300 p-4 w-full text-base leading-4 placeholder-gray-600 text-gray-600 bg-white" type="text">
                        {country}
                    </button>
                    <svg onClick={() => setMenu(!menu)} className={"transform  cursor-pointer absolute top-4 right-4 " + (menu ? "rotate-180" : "")} width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M3.5 5.75L8 10.25L12.5 5.75" stroke="#27272A" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    <div className={"mt-1 absolute z-10 w-full flex bg-gray-50 justify-start flex-col text-gray-600 " + (menu ? "block" : "hidden")}>
                        {countries.map((country) => (
                            <div key={country} className="cursor-pointer hover:bg-gray-800 hover:text-white px-4 py-2" onClick={changeText}>
                                {country}
                            </div>
                        ))}
                    </div>
                </div>
                <input className="border rounded-bl rounded-br border-gray-300 p-4 w-full text-base leading-4 placeholder-gray-600 text-gray-600" type="text" placeholder="ZIP" onChange={e => setZipCode(e.target.value)} />
            </div>

            <button className="mt-8 border border-transparent hover:border-gray-300 bg-gray-900 hover:bg-white text-white hover:text-gray-900 flex justify-center items-center py-4 rounded w-full" onClick={handleSubmit}>
                <div>
                    <p className="text-base leading-4">Register</p>
                </div>
            </button>
            <label className="mt-8 text-base leading-4 text-gray-800">Already Registered? <a href="/login">Login</a>.</label>
        </div>
      </div>
      <div class="w-1/4 h-full bg-gray-100"></div>
    </div>
  )
}