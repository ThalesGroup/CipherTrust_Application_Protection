import React, { useEffect, useState } from "react";
import Footer from '../../components/Footer';
import { useNavigate } from 'react-router-dom';
import jwt_decode from "jwt-decode";
import axios from 'axios';

async function createOrder(data) {
    console.log(data);
    return fetch('http://'+process.env.REACT_APP_BACKEND_IP_ADDRESS+':8081/proxy/order-mgmt/order/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
      .then(data => data.json())
   }

const Checkout = () => {
    const navigate = useNavigate();
    const [username, setUsername] = useState('');
    const [unit, setUnit] = useState('');
    const [street, setStreet] = useState('');
    const [city, setCity] = useState('');
    const [state, setState] = useState('');
    const [zipCode, setZipCode] = useState('');
    const [country, setCountry] = useState('');
    const [email, setEmail] = useState('');
    const [fullName, setFullName] = useState('');
    const [cardNumber, setCardNumber] = useState('');
    const [cvv, setCvv] = useState('');
    const [expiry, setExpiry] = useState('');

    const handleSubmit = async e => {
        e.preventDefault();
        const productId='RF293';
        const productName='North wolf bag';
        const price=900;
        const qty=1;
    
        const shippingAddress = {
            unit,
            street,
            city,
            state,
            zipCode,
            country
        }
        const billingAddress = {
            unit,
            street,
            city,
            state,
            zipCode,
            country
        }

        const card = {
            cardNumber,
            cvv,
            shippingAddress,
            billingAddress
        }

        const product={
            productId,
            productName,
            price
        }
        
        const products=[{product, qty}]

        const response = await createOrder({
          products,
          username,
          card
        });
        navigate('/');
        
      }

    useEffect(() => {
        //Get User Details
        const userId = sessionStorage.getItem('user');
        axios
        .get('http://'+process.env.REACT_APP_BACKEND_IP_ADDRESS+':8080/api/user-mgmt/user/'+userId)
        .then((res) => {
            console.log(res.data.user);
            setFullName(res.data.user.fullName);
            setUsername(userId);
            setEmail(res.data.user.email);
            setUnit(res.data.user.address.unit);
            setStreet(res.data.user.address.street);
            setCity(res.data.user.address.city);
            setState(res.data.user.address.state);
            setZipCode(res.data.user.address.zipCode);
            setCountry(res.data.user.address.country);
        })
        .catch((err) => console.log(err));

        let token = sessionStorage.getItem('token');
        if(token === null || token==="") {
            navigate('/login');
        } else {
            var decodedToken = jwt_decode(token);
            var dateNow = new Date();
            if(decodedToken.exp * 1000 > dateNow.getTime()) {
                //do nothing
            } else {
                sessionStorage.removeItem('token');
                navigate('/login');
            }
        }
    }, [navigate]);

    return (
      <>
        <div className="flex justify-center items-center">
            <div className="py-16 px-4 md:px-6 2xl:px-0 flex justify-center items-center 2xl:mx-auto 2xl:container">
                <div className="flex flex-col justify-start items-start w-full space-y-9">
                    <div className="flex justify-start flex-col items-start space-y-2">
                        <p className="text-3xl lg:text-4xl font-semibold leading-7 lg:leading-9 text-gray-800">Checkout</p>
                        <p className="text-base leading-normal sm:leading-4 text-gray-600">
                            Home {">"} Cart {">"} Checkout
                        </p>
                    </div>

                    <div className="flex flex-col xl:flex-row justify-center xl:justify-between space-y-6 xl:space-y-0 xl:space-x-6 w-full">
                        <div className="xl:w-3/5 flex flex-col sm:flex-row xl:flex-col justify-center items-center bg-gray-100 py-7 sm:py-0 xl:py-10 px-10 xl:w-full">
                            <div className="md:flex items-center mt-14 py-8 border-t border-gray-200">
                                <div className="w-1/4">
                                    <img src="https://cdn.tuk.dev/assets/templates/e-commerce-kit/bestSeller3.png" alt="#" className="w-full h-full object-center object-cover" />
                                </div>
                                <div className="md:pl-3 md:w-3/4">
                                    <p className="text-xs leading-3 text-gray-800 md:pt-0 pt-4">RF293</p>
                                    <div className="flex items-center justify-between w-full pt-1">
                                        <p className="text-base font-black leading-none text-gray-800">North wolf bag</p>
                                    </div>
                                    <p className="text-xs leading-3 text-gray-600 pt-2">Height: 10 inches</p>
                                    <p className="text-xs leading-3 text-gray-600 py-4">Color: Black</p>
                                    <p className="w-96 text-xs leading-3 text-gray-600">Composition: 100% calf leather</p>
                                    <div className="flex items-center justify-between pt-5 pr-6">
                                        <p className="text-base font-black leading-none text-gray-800">$900</p>
                                    </div>
                                </div>
                            </div>
                            <div className="md:flex items-center py-8 border-t border-gray-200">
                                <div className="w-1/4">
                                    <img src="https://cdn.tuk.dev/assets/templates/e-commerce-kit/bestSeller2.png" alt="#" className="w-full h-full object-center object-cover" />
                                </div>
                                <div className="md:pl-3 md:w-3/4 w-full">
                                    <p className="text-xs leading-3 text-gray-800 md:pt-0 pt-4">RF293</p>
                                    <div className="flex items-center justify-between w-full pt-1">
                                        <p className="text-base font-black leading-none text-gray-800">Luxe Signature Ring</p>
                                    </div>
                                    <p className="text-xs leading-3 text-gray-600 pt-2">Height: 10 inches</p>
                                    <p className="text-xs leading-3 text-gray-600 py-4">Color: Black</p>
                                    <p className="w-96 text-xs leading-3 text-gray-600">Composition: 100% calf leather</p>
                                    <div className="flex items-center justify-between pt-5 pr-6">
                                        <p className="text-base font-black leading-none text-gray-800">$1,500</p>
                                    </div>
                                </div>
                            </div>
                            <div className="md:flex items-center py-8 border-t border-b border-gray-200">
                                <div className="w-1/4">
                                    <img src="https://cdn.tuk.dev/assets/templates/e-commerce-kit/bestSeller1.png" alt="#" className="w-full h-full object-center object-cover" />
                                </div>
                                <div className="md:pl-3 md:w-3/4 w-full">
                                    <p className="text-xs leading-3 text-gray-800 md:pt-0 pt-4">RF293</p>
                                    <div className="flex items-center justify-between w-full pt-1">
                                        <p className="text-base font-black leading-none text-gray-800">Luxe Signature Shoes</p>
                                    </div>
                                    <p className="text-xs leading-3 text-gray-600 pt-2">Height: 10 inches</p>
                                    <p className="text-xs leading-3 text-gray-600 py-4">Color: Black</p>
                                    <p className="w-96 text-xs leading-3 text-gray-600">Composition: 100% calf leather</p>
                                    <div className="flex items-center justify-between pt-5 pr-6">
                                        <p className="text-base font-black leading-none text-gray-800">$450</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="p-8 bg-gray-100 flex flex-col lg:w-full xl:w-3/5">
                            
                            <div className="mt-8">
                                <input className="border border-gray-300 p-4 rounded w-full text-base leading-4 placeholder-gray-600 text-gray-600" type="email" value={email} disabled />
                            </div>

                            <label className="mt-8 text-base leading-4 text-gray-800">Card details</label>
                            <div className="mt-2 flex-col">
                                <div>
                                    <input className="border rounded-tl rounded-tr border-gray-300 p-4 w-full text-base leading-4 placeholder-gray-600 text-gray-600" type="text" placeholder="0000-1234-6549-15151"  onChange={e => setCardNumber(e.target.value)} />
                                </div>
                                <div className="flex-row flex">
                                    <input className="border rounded-bl border-gray-300 p-4 w-full text-base leading-4 placeholder-gray-600 text-gray-600" type="text" placeholder="MM/YY" onChange={e => setExpiry(e.target.value)} />
                                    <input className="border rounded-br border-gray-300 p-4 w-full text-base leading-4 placeholder-gray-600 text-gray-600" type="text" placeholder="CVC" onChange={e => setCvv(e.target.value)} />
                                </div>
                            </div>

                            <label className="mt-8 text-base leading-4 text-gray-800">Name on card</label>
                            <div className="mt-2 flex-col">
                                <div>
                                    <input className="border rounded border-gray-300 p-4 w-full text-base leading-4 placeholder-gray-600 text-gray-600" type="email"  value={fullName} disabled />
                                </div>
                            </div>

                            <label className="mt-8 text-base leading-4 text-gray-800">Address</label>
                            <div className="mt-2 flex-col">
                                <div className="flex-row flex">
                                    <input className="border rounded-bl border-gray-300 p-4 w-full text-base leading-4 placeholder-gray-600 text-gray-600" type="text"  value={unit} disabled />
                                    <input className="border rounded-br border-gray-300 p-4 w-full text-base leading-4 placeholder-gray-600 text-gray-600" type="text"  value={street} disabled />
                                </div>
                            </div>
                            <div className="mt-2 flex-col">
                                <div className="flex-row flex">
                                    <input className="border rounded-bl border-gray-300 p-4 w-full text-base leading-4 placeholder-gray-600 text-gray-600" type="text"  value={city} disabled />
                                    <input className="border rounded-br border-gray-300 p-4 w-full text-base leading-4 placeholder-gray-600 text-gray-600" type="text"  value={state} disabled />
                                </div>
                            </div>
                            <div className="mt-2 flex-col">
                                <div className="flex-row flex">
                                    <input className="border rounded-bl border-gray-300 p-4 w-full text-base leading-4 placeholder-gray-600 text-gray-600" type="text"  value={zipCode} disabled />
                                    <input className="border rounded-br border-gray-300 p-4 w-full text-base leading-4 placeholder-gray-600 text-gray-600" type="text"  value={country} disabled />
                                </div>
                            </div>

                            <button className="mt-8 border border-transparent hover:border-gray-300 bg-gray-900 hover:bg-white text-white hover:text-gray-900 flex justify-center items-center py-4 rounded w-full" onClick={handleSubmit}>
                                <div>
                                    <p className="text-base leading-4">Pay $2850</p>
                                </div>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <Footer />
      </>
    );
};

export default Checkout;