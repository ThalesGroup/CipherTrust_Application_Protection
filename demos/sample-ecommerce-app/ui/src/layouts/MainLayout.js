import React, { useState } from "react";
import { Outlet, Navigate } from "react-router-dom";
import { useNavigate } from "react-router-dom";

function MainLayout() {
    const CustomNavbar = ({ onSelect, activeKey, ...props }) => {
        const [searchInput, setSearchInput] = useState(true);
        const [mdOptionsToggle, setMdOptionsToggle] = useState(true);
        const [setShowMenu] = useState(false);
        const [show, setShow] = useState(false);
        const navigate = useNavigate();

        return (
            <div className="App" id="outer-container">
                <div id="page-wrap">

                    <div className="dark:bg-gray-900 bg-gray-50 px-6">
                        <div className="container mx-auto flex items-center justify-between">
                            <h1 className="md:w-2/12 cursor-pointer text-gray-800 dark:text-white" aria-label="Code.Run.Repeat.eShop">
                                Ciphertrust Ecommerce
                            </h1>
                            <div class="relative w-screen flex justify-start items-center">
                                <a href="/" class="px-5 py-4 hover:bg-gray-200 hover:text-black">Home</a>
                                <a href="/" class="px-5 py-4 hover:bg-gray-200 hover:text-black">Contact</a>

                                <div class="group">
                                    <button class="px-5 py-4 group-hover:bg-gray-200 group-hover:text-black">Products
                                        &darr;
                                    </button>
                                    <div
                                        class="hidden group-hover:flex flex-col absolute left-0 p-10 w-full z-30 bg-gray-100 text-black duration-300">
                                        <div class="grid grid-cols-2 md:grid-cols-4 gap-5">
                                            <div class="flex flex-col">
                                                <h3 class="mb-4 text-xl">Women</h3>
                                                <a href="/">Dresses</a>
                                                <a href="/">Tops</a>
                                                <a href="/">Tshirts</a>
                                                <a href="/">Jeans</a>
                                                <a href="/">Sweaters</a>
                                            </div>

                                            <div class="flex flex-col">
                                                <h3 class="mb-4 text-xl">Men</h3>
                                                <a href="/">Tshirts</a>
                                                <a href="/">Formals</a>
                                                <a href="/">Jeans</a>
                                                <a href="/">Shoes</a>
                                                <a href="/">Track Pants and Joggers</a>
                                            </div>

                                            <div class="flex flex-col">
                                                <h3 class="mb-4 text-xl">Accessories</h3>
                                                <a href="/">Body Lotion</a>
                                                <a href="/">Body Wash</a>
                                                <a href="/">Perfumes</a>
                                                <a href="/">Hair Accessories</a>
                                                <a href="/">Bracelets</a>
                                                <a href="/">Purses</a>
                                            </div>

                                            <div class="flex flex-col">
                                                <h3 class="mb-4 text-xl">Winter Clothing</h3>
                                                <a href="/">Jackets</a>
                                                <a href="/">Inners</a>
                                                <a href="/">Thermals</a>
                                                <a href="/">Snow Boots</a>
                                                <a href="/">Socks</a>
                                            </div>

                                            <div class="flex flex-col">
                                                <h3 class="mb-4 text-xl">Beauty</h3>
                                                <a href="/">Lipsticks</a>
                                                <a href="/">Eye Lines</a>
                                                <a href="/">Mascara</a>
                                                <a href="/">Face Wash</a>
                                                <a href="/">Face Moisturizers</a>
                                            </div>

                                            <div class="flex flex-col">
                                                <h3 class="mb-4 text-xl">Clearance</h3>
                                                <a href="/">Fall Collection</a>
                                                <a href="/">Summer Collection</a>
                                                <a href="/">Cool Stuff</a>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="md:w-2/12 justify-end flex items-center space-x-4 xl:space-x-8">
                                <div className="hidden lg:flex items-center">
                                    <button onClick={() => setSearchInput(!searchInput)} aria-label="search items" className="text-gray-800 dark:hover:text-gray-300 dark:text-white focus:outline-none focus:ring-2 focus:ring-gray-800">
                                        <svg className="fill-stroke" width={24} height={24} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <path d="M5 11C5 15.4183 8.58172 19 13 19C17.4183 19 21 15.4183 21 11C21 6.58172 17.4183 3 13 3C8.58172 3 5 6.58172 5 11Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                                            <path d="M2.99961 20.9999L7.34961 16.6499" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                                        </svg>
                                    </button>
                                    <input id="searchInput" type="text" placeholder="search" className={` ${searchInput ? "hidden" : ""} text-sm dark:bg-gray-900 dark:placeholder-gray-300 text-gray-600 rounded ml-1 border border-transparent focus:outline-none focus:border-gray-400 px-1`} />
                                </div>
                                <div className="hidden lg:flex items-center space-x-4 xl:space-x-8">
                                    <button aria-label="view favourites" className="text-gray-800 dark:hover:text-gray-300 dark:text-white focus:outline-none focus:ring-2 focus:ring-gray-800">
                                        <svg className="fill-stroke" width={24} height={24} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <path
                                                d="M20.8401 4.60987C20.3294 4.09888 19.7229 3.69352 19.0555 3.41696C18.388 3.14039 17.6726 2.99805 16.9501 2.99805C16.2276 2.99805 15.5122 3.14039 14.8448 3.41696C14.1773 3.69352 13.5709 4.09888 13.0601 4.60987L12.0001 5.66987L10.9401 4.60987C9.90843 3.57818 8.50915 2.99858 7.05012 2.99858C5.59109 2.99858 4.19181 3.57818 3.16012 4.60987C2.12843 5.64156 1.54883 7.04084 1.54883 8.49987C1.54883 9.95891 2.12843 11.3582 3.16012 12.3899L4.22012 13.4499L12.0001 21.2299L19.7801 13.4499L20.8401 12.3899C21.3511 11.8791 21.7565 11.2727 22.033 10.6052C22.3096 9.93777 22.4519 9.22236 22.4519 8.49987C22.4519 7.77738 22.3096 7.06198 22.033 6.39452C21.7565 5.72706 21.3511 5.12063 20.8401 4.60987V4.60987Z"
                                                stroke="currentColor"
                                                strokeWidth="1.5"
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                            />
                                        </svg>
                                    </button>
                                    <button onClick={() => setShow(!show)} aria-label="go to cart" className="text-gray-800 dark:hover:text-gray-300 dark:text-white focus:outline-none focus:ring-2 focus:ring-gray-800">
                                        <svg className="fill-stroke" width={26} height={26} viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <path d="M5 1L1 5.8V22.6C1 23.2365 1.28095 23.847 1.78105 24.2971C2.28115 24.7471 2.95942 25 3.66667 25H22.3333C23.0406 25 23.7189 24.7471 24.219 24.2971C24.719 23.847 25 23.2365 25 22.6V5.8L21 1H5Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                                            <path d="M1 5.7998H25" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                                            <path d="M18.3346 10.6001C18.3346 11.8731 17.7727 13.094 16.7725 13.9942C15.7723 14.8944 14.4158 15.4001 13.0013 15.4001C11.5868 15.4001 10.2303 14.8944 9.23007 13.9942C8.22987 13.094 7.66797 11.8731 7.66797 10.6001" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                                        </svg>
                                    </button>                                 
                                </div>
                                <div className="flex lg:hidden">
                                    <button aria-label="show options" onClick={() => setMdOptionsToggle(!mdOptionsToggle)} className="text-black dark:text-white dark:hover:text-gray-300 hidden md:flex focus:outline-none focus:ring-2 rounded focus:ring-gray-600">
                                        <svg className="fill-stroke" width={24} height={24} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <path d="M4 6H20" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                                            <path d="M10 12H20" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                                            <path d="M6 18H20" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                                        </svg>
                                    </button>
                                    <button aria-label="open menu" onClick={() => setShowMenu(true)} className="text-black dark:text-white dark:hover:text-gray-300 md:hidden focus:outline-none focus:ring-2 rounded focus:ring-gray-600">
                                        <svg className="fill-stroke" width={24} height={24} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <path d="M4 6H20" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                                            <path d="M10 12H20" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                                            <path d="M6 18H20" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    {show && (
                        <div className="z-20 w-full h-full bg-black bg-opacity-90 top-0 overflow-y-auto overflow-x-hidden fixed sticky-0" id="chec-div">
                            <div className="w-full absolute z-10 right-0 h-full overflow-x-hidden transform translate-x-0 transition ease-in-out duration-700" id="checkout">
                                <div className="flex md:flex-row flex-col justify-end" id="cart">
                                    <div className="lg:w-1/2 w-full md:pl-10 pl-4 pr-10 md:pr-4 md:py-12 py-8 bg-white overflow-y-auto overflow-x-hidden h-screen" id="scroll">
                                        <div className="flex items-center text-gray-500 hover:text-gray-600 cursor-pointer" onClick={() => setShow(!show)}>
                                            <svg xmlns="http://www.w3.org/2000/svg" className="icon icon-tabler icon-tabler-chevron-left" width={16} height={16} viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" fill="none" strokeLinecap="round" strokeLinejoin="round">
                                                <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                                                <polyline points="15 6 9 12 15 18" />
                                            </svg>
                                            <p className="text-sm pl-2 leading-none">Back</p>
                                        </div>
                                        <p className="text-5xl font-black leading-10 text-gray-800 pt-3">Bag</p>
                                        <div className="md:flex items-center mt-14 py-8 border-t border-gray-200">
                                            <div className="w-1/4">
                                                <img src="https://cdn.tuk.dev/assets/templates/e-commerce-kit/bestSeller3.png" alt="#" className="w-full h-full object-center object-cover" />
                                            </div>
                                            <div className="md:pl-3 md:w-3/4">
                                                <p className="text-xs leading-3 text-gray-800 md:pt-0 pt-4">RF293</p>
                                                <div className="flex items-center justify-between w-full pt-1">
                                                    <p className="text-base font-black leading-none text-gray-800">North wolf bag</p>
                                                    <select className="py-2 px-1 border border-gray-200 mr-6 focus:outline-none">
                                                        <option>01</option>
                                                        <option>02</option>
                                                        <option>03</option>
                                                    </select>
                                                </div>
                                                <p className="text-xs leading-3 text-gray-600 pt-2">Height: 10 inches</p>
                                                <p className="text-xs leading-3 text-gray-600 py-4">Color: Black</p>
                                                <p className="w-96 text-xs leading-3 text-gray-600">Composition: 100% calf leather</p>
                                                <div className="flex items-center justify-between pt-5 pr-6">
                                                    <div className="flex itemms-center">
                                                        <p className="text-xs leading-3 underline text-gray-800 cursor-pointer">Add to favorites</p>
                                                        <p className="text-xs leading-3 underline text-red-500 pl-5 cursor-pointer">Remove</p>
                                                    </div>
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
                                                    <select className="py-2 px-1 border border-gray-200 mr-6 focus:outline-none">
                                                        <option>01</option>
                                                        <option>02</option>
                                                        <option>03</option>
                                                    </select>
                                                </div>
                                                <p className="text-xs leading-3 text-gray-600 pt-2">Height: 10 inches</p>
                                                <p className="text-xs leading-3 text-gray-600 py-4">Color: Black</p>
                                                <p className="w-96 text-xs leading-3 text-gray-600">Composition: 100% calf leather</p>
                                                <div className="flex items-center justify-between pt-5 pr-6">
                                                    <div className="flex itemms-center">
                                                        <p className="text-xs leading-3 underline text-gray-800 cursor-pointer">Add to favorites</p>
                                                        <p className="text-xs leading-3 underline text-red-500 pl-5 cursor-pointer">Remove</p>
                                                    </div>
                                                    <p className="text-base font-black leading-none text-gray-800">$1,500</p>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="md:flex items-center py-8 border-t border-b border-gray-200">
                                            <div className="h-full w-1/4">
                                                <img src="https://cdn.tuk.dev/assets/templates/e-commerce-kit/bestSeller1.png" alt="#" className="w-full h-full object-center object-cover" />
                                            </div>
                                            <div className="md:pl-3 md:w-3/4 w-full">
                                                <p className="text-xs leading-3 text-gray-800 md:pt-0 pt-4">RF293</p>
                                                <div className="flex items-center justify-between w-full pt-1">
                                                    <p className="text-base font-black leading-none text-gray-800">Luxe Signature Shoes</p>
                                                    <select className="py-2 px-1 border border-gray-200 mr-6 focus:outline-none">
                                                        <option>01</option>
                                                        <option>02</option>
                                                        <option>03</option>
                                                    </select>
                                                </div>
                                                <p className="text-xs leading-3 text-gray-600 pt-2">Height: 10 inches</p>
                                                <p className="text-xs leading-3 text-gray-600 py-4">Color: Black</p>
                                                <p className="w-96 text-xs leading-3 text-gray-600">Composition: 100% calf leather</p>
                                                <div className="flex items-center justify-between pt-5 pr-6">
                                                    <div className="flex itemms-center">
                                                        <p className="text-xs leading-3 underline text-gray-800 cursor-pointer">Add to favorites</p>
                                                        <p className="text-xs leading-3 underline text-red-500 pl-5 cursor-pointer">Remove</p>
                                                    </div>
                                                    <p className="text-base font-black leading-none text-gray-800">$450</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="xl:w-1/2 md:w-1/3 xl:w-1/4 w-full bg-gray-100 h-full">
                                        <div className="flex flex-col md:h-screen px-14 py-20 justify-between overflow-y-auto">
                                            <div>
                                                <p className="text-4xl font-black leading-9 text-gray-800">Summary</p>
                                                <div className="flex items-center justify-between pt-16">
                                                    <p className="text-base leading-none text-gray-800">Subtotal</p>
                                                    <p className="text-base leading-none text-gray-800">$9,000</p>
                                                </div>
                                                <div className="flex items-center justify-between pt-5">
                                                    <p className="text-base leading-none text-gray-800">Shipping</p>
                                                    <p className="text-base leading-none text-gray-800">$0</p>
                                                </div>
                                                <div className="flex items-center justify-between pt-5">
                                                    <p className="text-base leading-none text-gray-800">Tax</p>
                                                    <p className="text-base leading-none text-gray-800">$0</p>
                                                </div>
                                            </div>
                                            <div>
                                                <div className="flex items-center pb-6 justify-between lg:pt-5 pt-20">
                                                    <p className="text-2xl leading-normal text-gray-800">Total</p>
                                                    <p className="text-2xl font-bold leading-normal text-right text-gray-800">$2,850</p>
                                                </div>
                                                <button onClick={() => {
                                                        setShow(!show) 
                                                        navigate('/checkout')
                                                    }} className="text-base leading-none w-full py-5 bg-gray-800 border-gray-800 border focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-800 text-white">
                                                    Checkout
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                    
                    <style>
                        {` /* width */
                        #scroll::-webkit-scrollbar {
                            width: 1px;
                        }

                        /* Track */
                        #scroll::-webkit-scrollbar-track {
                            background: #f1f1f1;
                        }

                        /* Handle */
                        #scroll::-webkit-scrollbar-thumb {
                            background: rgb(133, 132, 132);
                        }
                        `}
                    </style>
                </div>
            </div>
        )
    };
    let authToken = true;
    return (
        authToken ? <><CustomNavbar /> <Outlet /></> : <Navigate to="/home"/>
    )
};
export default MainLayout;
