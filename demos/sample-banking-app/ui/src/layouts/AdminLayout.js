import { Outlet, Navigate } from "react-router-dom";
import {React, useState} from 'react';
import jwt_decode from "jwt-decode";

function AdminLayout() {
    const [show, setShow] = useState(false);
    const [product, setProduct] = useState(false);
    const [profile, setProfile] = useState(false);

    const CustomNavbar = ({ onSelect, activeKey, ...props }) => {
        return (
            <>
            <div className="App" id="outer-container">
                <div id="page-wrap">
                    <div className="bg-gray-200 pb-10">                
                    {/* Navigation starts */}
                    {/* Mobile */}
                    
                    <div className={show ? "w-full h-full absolute z-40  transform  translate-x-0 " : "   w-full h-full absolute z-40  transform -translate-x-full"}>
                        <div className="bg-gray-800 opacity-50 inset-0 fixed w-full h-full" onClick={() => setShow(!show)} />
                        <div className="w-64 z-20 absolute left-0 z-40 top-0 bg-white shadow flex-col justify-between transition duration-150 ease-in-out h-full">
                            <div className="flex flex-col justify-between h-full">
                                <div className="px-6 pt-4">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center">
                                            <svg aria-label="Home" id="logo" enableBackground="new 0 0 300 300" height={43} viewBox="0 0 300 300" width={43} xmlns="http://www.w3.org/2000/svg" xmlnsXlink="http://www.w3.org/1999/xlink">
                                                <g>
                                                    <path
                                                        fill="#4c51bf"
                                                        d="m234.735 35.532c-8.822 0-16 7.178-16 16s7.178 16 16 16 16-7.178 16-16-7.178-16-16-16zm0 24c-4.412 0-8-3.588-8-8s3.588-8 8-8 8 3.588 8 8-3.588 8-8 8zm-62.529-14c0-2.502 2.028-4.53 4.53-4.53s4.53 2.028 4.53 4.53c0 2.501-2.028 4.529-4.53 4.529s-4.53-2.027-4.53-4.529zm89.059 60c0 2.501-2.028 4.529-4.53 4.529s-4.53-2.028-4.53-4.529c0-2.502 2.028-4.53 4.53-4.53s4.53 2.029 4.53 4.53zm-40.522-5.459-88-51.064c-1.242-.723-2.773-.723-4.016 0l-88 51.064c-1.232.715-1.992 2.033-1.992 3.459v104c0 1.404.736 2.705 1.938 3.428l88 52.936c.635.381 1.35.572 2.062.572s1.428-.191 2.062-.572l88-52.936c1.201-.723 1.938-2.023 1.938-3.428v-104c0-1.426-.76-2.744-1.992-3.459zm-90.008-42.98 80.085 46.47-52.95 31.289-23.135-13.607v-21.713c0-2.209-1.791-4-4-4s-4 1.791-4 4v21.713l-26.027 15.309c-1.223.719-1.973 2.029-1.973 3.447v29.795l-52 30.727v-94.688zm0 198.707-80.189-48.237 51.467-30.412 24.723 14.539v19.842c0 2.209 1.791 4 4 4s4-1.791 4-4v-19.842l26.027-15.307c1.223-.719 1.973-2.029 1.973-3.447v-31.667l52-30.728v94.729z"
                                                    />
                                                </g>
                                            </svg>
                                            <p className="text-bold md:text2xl text-base pl-3 text-gray-800">Ciphertrust Bank BackOffice</p>
                                        </div>
                                        <div id="cross" className=" text-gray-800" onClick={() => setShow(!show)}>
                                            <svg xmlns="http://www.w3.org/2000/svg" className="icon icon-tabler icon-tabler-x" width={24} height={24} viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor" fill="none" strokeLinecap="round" strokeLinejoin="round">
                                                <path stroke="none" d="M0 0h24v24H0z" />
                                                <line x1={18} y1={6} x2={6} y2={18} />
                                                <line x1={6} y1={6} x2={18} y2={18} />
                                            </svg>
                                        </div>
                                    </div>
                                    <ul className="f-m-m">
                                        <a href='/auth/user/home'>
                                            <li className="text-white pt-8">
                                                <div className="flex items-center">
                                                    <div className="md:w-6 md:h-6 w-5 h-5">
                                                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="none">
                                                            <path d="M7.16667 3H3.83333C3.3731 3 3 3.3731 3 3.83333V7.16667C3 7.6269 3.3731 8 3.83333 8H7.16667C7.6269 8 8 7.6269 8 7.16667V3.83333C8 3.3731 7.6269 3 7.16667 3Z" stroke="#667EEA" strokeWidth={1} strokeLinecap="round" strokeLinejoin="round" />
                                                            <path d="M7.16667 11.6667H3.83333C3.3731 11.6667 3 12.0398 3 12.5V15.8333C3 16.2936 3.3731 16.6667 3.83333 16.6667H7.16667C7.6269 16.6667 8 16.2936 8 15.8333V12.5C8 12.0398 7.6269 11.6667 7.16667 11.6667Z" stroke="#667EEA" strokeWidth={1} strokeLinecap="round" strokeLinejoin="round" />
                                                            <path d="M16.1667 11.6667H12.8333C12.3731 11.6667 12 12.0398 12 12.5V15.8334C12 16.2936 12.3731 16.6667 12.8333 16.6667H16.1667C16.6269 16.6667 17 16.2936 17 15.8334V12.5C17 12.0398 16.6269 11.6667 16.1667 11.6667Z" stroke="#667EEA" strokeWidth={1} strokeLinecap="round" strokeLinejoin="round" />
                                                            <path d="M16.1667 3H12.8333C12.3731 3 12 3.3731 12 3.83333V7.16667C12 7.6269 12.3731 8 12.8333 8H16.1667C16.6269 8 17 7.6269 17 7.16667V3.83333C17 3.3731 16.6269 3 16.1667 3Z" stroke="#667EEA" strokeWidth={1} strokeLinecap="round" strokeLinejoin="round" />
                                                        </svg>
                                                    </div>
                                                    <p className="text-indigo-500 ml-3 text-lg">Dashboard</p>
                                                </div>
                                            </li>
                                        </a>
                                        <li className="text-gray-700 pt-8">
                                            <div className="flex items-center">
                                                <div className="flex items-center">
                                                    <div className="md:w-6 md:h-6 w-5 h-5">
                                                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 18 18" fill="none">
                                                            <path
                                                                d="M2.33333 4.83333H4.83333C5.05435 4.83333 5.26631 4.74554 5.42259 4.58926C5.57887 4.43298 5.66667 4.22101 5.66667 4V3.16667C5.66667 2.72464 5.84226 2.30072 6.15482 1.98816C6.46738 1.67559 6.89131 1.5 7.33333 1.5C7.77536 1.5 8.19928 1.67559 8.51184 1.98816C8.8244 2.30072 9 2.72464 9 3.16667V4C9 4.22101 9.0878 4.43298 9.24408 4.58926C9.40036 4.74554 9.61232 4.83333 9.83333 4.83333H12.3333C12.5543 4.83333 12.7663 4.92113 12.9226 5.07741C13.0789 5.23369 13.1667 5.44565 13.1667 5.66667V8.16667C13.1667 8.38768 13.2545 8.59964 13.4107 8.75592C13.567 8.9122 13.779 9 14 9H14.8333C15.2754 9 15.6993 9.17559 16.0118 9.48816C16.3244 9.80072 16.5 10.2246 16.5 10.6667C16.5 11.1087 16.3244 11.5326 16.0118 11.8452C15.6993 12.1577 15.2754 12.3333 14.8333 12.3333H14C13.779 12.3333 13.567 12.4211 13.4107 12.5774C13.2545 12.7337 13.1667 12.9457 13.1667 13.1667V15.6667C13.1667 15.8877 13.0789 16.0996 12.9226 16.2559C12.7663 16.4122 12.5543 16.5 12.3333 16.5H9.83333C9.61232 16.5 9.40036 16.4122 9.24408 16.2559C9.0878 16.0996 9 15.8877 9 15.6667V14.8333C9 14.3913 8.8244 13.9674 8.51184 13.6548C8.19928 13.3423 7.77536 13.1667 7.33333 13.1667C6.89131 13.1667 6.46738 13.3423 6.15482 13.6548C5.84226 13.9674 5.66667 14.3913 5.66667 14.8333V15.6667C5.66667 15.8877 5.57887 16.0996 5.42259 16.2559C5.26631 16.4122 5.05435 16.5 4.83333 16.5H2.33333C2.11232 16.5 1.90036 16.4122 1.74408 16.2559C1.5878 16.0996 1.5 15.8877 1.5 15.6667V13.1667C1.5 12.9457 1.5878 12.7337 1.74408 12.5774C1.90036 12.4211 2.11232 12.3333 2.33333 12.3333H3.16667C3.60869 12.3333 4.03262 12.1577 4.34518 11.8452C4.65774 11.5326 4.83333 11.1087 4.83333 10.6667C4.83333 10.2246 4.65774 9.80072 4.34518 9.48816C4.03262 9.17559 3.60869 9 3.16667 9H2.33333C2.11232 9 1.90036 8.9122 1.74408 8.75592C1.5878 8.59964 1.5 8.38768 1.5 8.16667V5.66667C1.5 5.44565 1.5878 5.23369 1.74408 5.07741C1.90036 4.92113 2.11232 4.83333 2.33333 4.83333"
                                                                stroke="currentColor"
                                                                strokeWidth={1}
                                                                strokeLinecap="round"
                                                                strokeLinejoin="round"
                                                            />
                                                        </svg>
                                                    </div>
                                                    <p className="text-gray-700 ml-3 text-lg">Accounts</p>
                                                </div>
                                                <div onClick={() => setProduct(!product)}>
                                                    {product ? (
                                                        <div className=" ml-4">
                                                            <svg xmlns="http://www.w3.org/2000/svg" className="icon icon-tabler icon-tabler-chevron-up" width={14} height={14} viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor" fill="none" strokeLinecap="round" strokeLinejoin="round">
                                                                <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                                                                <polyline points="6 15 12 9 18 15" />
                                                            </svg>
                                                        </div>
                                                    ) : (
                                                        <div className="ml-4">
                                                            <svg xmlns="http://www.w3.org/2000/svg" className="icon icon-tabler icon-tabler-chevron-down" width={14} height={14} viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor" fill="none" strokeLinecap="round" strokeLinejoin="round">
                                                                <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                                                                <polyline points="6 9 12 15 18 9" />
                                                            </svg>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                            {product ? (
                                                <div>
                                                    <ul className="my-3">
                                                        <li className="text-sm text-indigo-500 py-2 px-6"><a href="/auth/admin/home" className="text-black hover:text-blue-800 visited:text-black">List</a></li>
                                                    </ul>
                                                </div>
                                            ) : (
                                                ""
                                            )}
                                        </li>
                                    </ul>
                                </div>
                                <div className="w-full">
                                    <div className="flex justify-center mb-4 w-full px-6">
                                        <div className="relative w-full">
                                            <div className="text-gray-500 absolute ml-4 inset-0 m-auto w-4 h-4">
                                                <svg xmlns="http://www.w3.org/2000/svg" className="icon icon-tabler icon-tabler-search" width={16} height={16} viewBox="0 0 24 24" strokeWidth={1} stroke="#A0AEC0" fill="none" strokeLinecap="round" strokeLinejoin="round">
                                                    <path stroke="none" d="M0 0h24v24H0z" />
                                                    <circle cx={10} cy={10} r={7} />
                                                    <line x1={21} y1={21} x2={15} y2={15} />
                                                </svg>
                                            </div>
                                            <input className="bg-gray-100 focus:outline-none rounded w-full text-sm text-gray-500 bg-gray-100 pl-10 py-2" type="text" placeholder="Search" />
                                        </div>
                                    </div>
                                    <div className="border-t border-gray-300">
                                        <div className="w-full flex items-center justify-between px-6 pt-1">
                                            <div className="flex items-center">
                                                <img alt="profile-pic" src="https://tuk-cdn.s3.amazonaws.com/assets/components/boxed_layout/bl_1.png" className="w-8 h-8 rounded-md" />
                                                <p className=" text-gray-800 text-base leading-4 ml-2">Jane Doe</p>
                                            </div>
                                            <ul className="flex">
                                                <li className="cursor-pointer text-white pt-5 pb-3">
                                                    <svg xmlns="http://www.w3.org/2000/svg" className="icon icon-tabler icon-tabler-messages" width={24} height={24} viewBox="0 0 24 24" strokeWidth={1} stroke="#718096" fill="none" strokeLinecap="round" strokeLinejoin="round">
                                                        <path stroke="none" d="M0 0h24v24H0z" />
                                                        <path d="M21 14l-3 -3h-7a1 1 0 0 1 -1 -1v-6a1 1 0 0 1 1 -1h9a1 1 0 0 1 1 1v10" />
                                                        <path d="M14 15v2a1 1 0 0 1 -1 1h-7l-3 3v-10a1 1 0 0 1 1 -1h2" />
                                                    </svg>
                                                </li>
                                                <li className="cursor-pointer text-white pt-5 pb-3 pl-3">
                                                    <svg xmlns="http://www.w3.org/2000/svg" className="icon icon-tabler icon-tabler-bell" width={24} height={24} viewBox="0 0 24 24" strokeWidth={1} stroke="#718096" fill="none" strokeLinecap="round" strokeLinejoin="round">
                                                        <path stroke="none" d="M0 0h24v24H0z" />
                                                        <path d="M10 5a2 2 0 0 1 4 0a7 7 0 0 1 4 6v3a4 4 0 0 0 2 3h-16a4 4 0 0 0 2 -3v-3a7 7 0 0 1 4 -6" />
                                                        <path d="M9 17v1a3 3 0 0 0 6 0v-1" />
                                                    </svg>
                                                </li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    {/* Mobile */}
                    <nav className="w-full mx-auto bg-white shadow relative z-20">
                        <div className="justify-between container px-6 h-16 flex items-center lg:items-stretch mx-auto">
                            <div className="flex items-center">
                                <div className="mr-10 flex items-center">
                                    <img src="https://dwglogo.com/wp-content/uploads/2016/03/Thales-SA-HO.png" width="50px" />
                                    <h3 className="text-base text-gray-800 font-bold tracking-normal leading-tight ml-3 hidden lg:block">Ciphertrust Bank BackOffice</h3>
                                </div>
                                <ul className="pr-32 xl:flex hidden items-center h-full">
                                    <li className="hover:text-indigo-700 cursor-pointer h-full flex items-center text-sm text-indigo-700 tracking-normal"><a href="/auth/user/home" className="text-black hover:text-blue-800 visited:text-black no-underline">Dashboard</a></li>
                                    <li className="hover:text-indigo-700 cursor-pointer h-full flex items-center text-sm text-gry-800 mx-10 tracking-normal relative">
                                        {product ? (
                                            <ul className="bg-white shadow rounded py-1 w-32 left-0 mt-16 -ml-4 absolute  top-0">
                                                <li className="cursor-pointer text-gray-600 text-sm leading-3 tracking-normal py-3 hover:bg-gray-100 px-3 font-normal"><a href="/auth/admin/home" className="text-black hover:text-blue-800 visited:text-black no-underline">List</a></li>
                                            </ul>
                                        ) : (
                                            ""
                                        )}
                                        Accounts
                                        <span className="ml-2" onClick={() => setProduct(!product)}>
                                            <svg xmlns="http://www.w3.org/2000/svg" className="icon icon-tabler icon-tabler-chevron-down" width={16} height={16} viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor" fill="none" strokeLinecap="round" strokeLinejoin="round">
                                                <path stroke="none" d="M0 0h24v24H0z" />
                                                <polyline points="6 9 12 15 18 9" />
                                            </svg>
                                        </span>
                                    </li>
                                </ul>
                            </div>
                            <div className="h-full xl:flex hidden items-center justify-end">
                                <div className="h-full flex items-center">
                                    <div className="w-32 pr-16 h-full flex items-center justify-end border-r" />
                                    <div className="w-full h-full flex">
                                        <div className="w-16 xl:w-32 h-full flex items-center justify-center xl:border-r">
                                            <div className="relative">
                                                <div className="cursor-pointer w-6 h-6 xl:w-auto xl:h-auto text-gray-600">
                                                    <svg xmlns="http://www.w3.org/2000/svg" className="icon icon-tabler icon-tabler-bell" width={28} height={28} viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor" fill="none" strokeLinecap="round" strokeLinejoin="round">
                                                        <path stroke="none" d="M0 0h24v24H0z" />
                                                        <path d="M10 5a2 2 0 0 1 4 0a7 7 0 0 1 4 6v3a4 4 0 0 0 2 3h-16a4 4 0 0 0 2 -3v-3a7 7 0 0 1 4 -6" />
                                                        <path d="M9 17v1a3 3 0 0 0 6 0v-1" />
                                                    </svg>
                                                </div>
                                                <div className="animate-ping w-2 h-2 rounded-full bg-red-400 border border-white absolute inset-0 mt-1 mr-1 m-auto" />
                                            </div>
                                        </div>
                                        <div aria-haspopup="true" className="cursor-pointer w-full flex items-center justify-end relative" onClick={() => setProfile(!profile)}>
                                            {profile ? (
                                                <ul className="p-2 w-40 border-r bg-white absolute rounded z-40 left-0 shadow mt-64 ">
                                                    <li className="cursor-pointer text-gray-600 text-sm leading-3 tracking-normal py-2 hover:text-indigo-700 focus:text-indigo-700 focus:outline-none">
                                                        <div className="flex items-center">
                                                            <svg xmlns="http://www.w3.org/2000/svg" className="icon icon-tabler icon-tabler-user" width={20} height={20} viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor" fill="none" strokeLinecap="round" strokeLinejoin="round">
                                                                <path stroke="none" d="M0 0h24v24H0z" />
                                                                <circle cx={12} cy={7} r={4} />
                                                                <path d="M6 21v-2a4 4 0 0 1 4 -4h4a4 4 0 0 1 4 4v2" />
                                                            </svg>
                                                            <span className="ml-2"><a href="/logout" className="text-black hover:text-blue-800 visited:text-black no-underline">Logout</a></span>
                                                        </div>
                                                    </li>
                                                </ul>
                                            ) : (
                                                ""
                                            )}
                                            <img className="rounded-full h-10 w-10 object-cover" src="https://cdn.tuk.dev/assets/webapp/master_layouts/boxed_layout/boxed_layout2.jpg" alt="avatar" />
                                            <p className="text-gray-800 text-sm ml-2">{decodedToken.preferred_username}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="visible xl:hidden flex items-center">
                                <div>
                                    <div id="menu" className="text-gray-800" onClick={() => setShow(!show)}>
                                        <svg xmlns="http://www.w3.org/2000/svg" className="icon icon-tabler icon-tabler-menu-2" width={24} height={24} viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor" fill="none" strokeLinecap="round" strokeLinejoin="round">
                                            <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                                            <line x1={4} y1={6} x2={20} y2={6} />
                                            <line x1={4} y1={12} x2={20} y2={12} />
                                            <line x1={4} y1={18} x2={20} y2={18} />
                                        </svg>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </nav>            
                    {/* Navigation ends */}
                    {/* Page title starts */}
                    <div className="bg-gray-800 pt-8 pb-16 relative z-10">
                        <div className="container px-6 mx-auto flex flex-col lg:flex-row items-start lg:items-center justify-between">
                            <div className="flex-col flex lg:flex-row items-start lg:items-center">
                                <div className="ml-0 lg:ml-20 my-6 lg:my-0">
                                    <h4 className="text-2xl font-bold leading-tight text-white mb-2">Administration</h4>
                                </div>
                            </div>
                            <div>
                                <button className="focus:outline-none mr-3 bg-transparent transition duration-150 ease-in-out rounded hover:bg-gray-700 text-white px-5 py-2 text-sm border border-white">Home</button>
                            </div>
                        </div>
                    </div>
                    {/* Page title ends */}
                    </div>
                </div>
            </div>
            </>
        )
    };

    let token = sessionStorage.getItem('token');
    var decodedToken = jwt_decode(token);
    var dateNow = new Date();
    
    let authToken = false;
    if(token && (decodedToken.exp * 1000 > dateNow.getTime())) {
        authToken = true;
    } else {
        authToken = false;
    }
    return (
      authToken ? <><CustomNavbar /> <Outlet /></> : <Navigate to="/login"/>
    )
};

export default AdminLayout;