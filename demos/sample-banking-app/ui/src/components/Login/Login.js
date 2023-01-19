import React, { useState, useEffect } from 'react';
import './Login.css';
import "bootstrap/dist/css/bootstrap.min.css"
import { useNavigate } from 'react-router-dom';
import jwt_decode from "jwt-decode";

async function loginUser(credentials) {
 console.log(credentials);
 return fetch('http://'+process.env.REACT_APP_BACKEND_IP_ADDRESS+':8080/api/fakebank/signin/', {
   method: 'POST',
   headers: {
     'Content-Type': 'application/json'
   },
   body: JSON.stringify(credentials)
 })
   .then(data => data.json())
}

export default function Login() {
  const navigate = useNavigate();
  const [username, setUserName] = useState();
  const [password, setPassword] = useState();
  const handleSubmit = async e => {
    e.preventDefault();
    
    const auth_response = await loginUser({
      username,
      password
    });
    sessionStorage.setItem('token', auth_response.jwt);
    sessionStorage.setItem('basic', btoa(username + ':' + password))
    let token = sessionStorage.getItem('token');
    var decodedToken = jwt_decode(token);
    if((decodedToken.preferred_username === 'cccustomersupport') || (decodedToken.preferred_username === 'everyoneelse'))
      navigate('/auth/admin/home');
    else
      navigate('/auth/user/home');
    
  }

  useEffect(() => {
    let token = sessionStorage.getItem('token');
    if(token !== null) {
      var decodedToken = jwt_decode(token);
      var dateNow = new Date();
      if(decodedToken.exp * 1000 > dateNow.getTime()) {
        if((decodedToken.preferred_username === 'cccustomersupport') || (decodedToken.preferred_username === 'everyoneelse'))
          navigate('/auth/admin/home');
        else
          navigate('/auth/user/home');
      } else {
        console.log('continue...');
      }
    } else {
      console.log('continue...');
    }
    
  }, [navigate]);

  return(
    <div className="bg-white dark:bg-gray-900">
        <div className="flex justify-center h-screen">
            <div className="hidden bg-cover lg:block lg:w-2/3 bg-[url('https://images.unsplash.com/photo-1606156822967-c44b9271f520?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170&q=80')]">
                <div className="flex items-center h-full px-20 bg-gray-900 bg-opacity-40">
                    <div>
                        <h2 className="text-4xl font-bold text-white">Secure Online Banking</h2>                        
                        <p className="max-w-xl mt-3 text-gray-300">Compliant online banking with Ciphertrust Manager data protection solution</p>
                    </div>
                </div>
            </div>
            
            <div class="flex items-center w-full max-w-md px-6 mx-auto lg:w-2/6">
                <div class="flex-1">
                    <div class="text-center">
                        <p class="mt-3 text-gray-500 dark:text-gray-300">Sign in to access your account</p>
                    </div>

                    <div class="mt-8">
                        <form onSubmit={handleSubmit}>
                            <div>
                                <label for="email" class="block mb-2 text-sm text-gray-600 dark:text-gray-200">Username</label>
                                <input type="text" name="email" id="email" placeholder="username" class="block w-full px-4 py-2 mt-2 text-gray-700 placeholder-gray-400 bg-white border border-gray-200 rounded-md dark:placeholder-gray-600 dark:bg-gray-900 dark:text-gray-300 dark:border-gray-700 focus:border-blue-400 dark:focus:border-blue-400 focus:ring-blue-400 focus:outline-none focus:ring focus:ring-opacity-40" onChange={e => setUserName(e.target.value)} />
                            </div>

                            <div class="mt-6">
                                <div class="flex justify-between mb-2">
                                    <label for="password" class="text-sm text-gray-600 dark:text-gray-200">Password</label>
                                    <a href="#" class="text-sm text-gray-400 focus:text-blue-500 hover:text-blue-500 hover:underline">Forgot password?</a>
                                </div>

                                <input type="password" name="password" id="password" placeholder="Your Password" class="block w-full px-4 py-2 mt-2 text-gray-700 placeholder-gray-400 bg-white border border-gray-200 rounded-md dark:placeholder-gray-600 dark:bg-gray-900 dark:text-gray-300 dark:border-gray-700 focus:border-blue-400 dark:focus:border-blue-400 focus:ring-blue-400 focus:outline-none focus:ring focus:ring-opacity-40" onChange={e => setPassword(e.target.value)} />
                            </div>

                            <div class="mt-6">
                                <button
                                    class="w-full px-4 py-2 tracking-wide text-white transition-colors duration-200 transform bg-blue-500 rounded-md hover:bg-blue-400 focus:outline-none focus:bg-blue-400 focus:ring focus:ring-blue-300 focus:ring-opacity-50">
                                    Sign in
                                </button>
                            </div>
                        </form>
                        <p class="mt-6 text-sm text-center text-gray-400">Don&#x27;t have an account yet? <a href="/userCreate" class="text-blue-500 focus:outline-none focus:underline hover:underline">Sign up</a>.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
  )
}