import React from 'react';
import Footer from '../../components/Footer';
import { useNavigate } from "react-router-dom";
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export default function Home() {
    const navigate = useNavigate();
    const showToastMessage = () => {
      toast.success('Item added to bag!', {
          position: toast.POSITION.BOTTOM_LEFT
      });
    };
    return(
      <>
      <div className>
        <div className="flex justify-end items-center">
          <img className="object-cover md:hidden  w-full h-60" src="https://tuk-cdn.s3.amazonaws.com/can-uploader/banner_12_bg.png" alt="background" />
          <img className="hidden md:block object-cover  w-full h-56 lg:h-52" src="https://tuk-cdn.s3.amazonaws.com/can-uploader/banner_12_bg_ipad_desktop.png" alt="background" />
          <div className=" flex xl:px-20 justify-start items-start flex-col absolute">
            <h1 className="text0-xl xl:text-2xl font-medium leading-5 xl:leading-normal text-gray-800">Sale now on</h1>
            <p className="w-44 sm:w-64 lg:w-2/3 mt-4 text-base leading-6 xl:leading-5 text-gray-800">Shop our mid Season sale for a range of discounted items</p>
            <button className="mt-5 xl:mt-6 hover:underline underline-offset-4 transition duration-300 ease-in-out flex justify-start items-center space-x-2">
              <p className="text-base font-medium leading-none pb-0.5">Shop Sale</p>
              <svg width={6} height={12} viewBox="0 0 6 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path fillRule="evenodd" clipRule="evenodd" d="M0.21967 0.96967C0.512563 0.676777 0.987437 0.676777 1.28033 0.96967L5.78033 5.46967C6.07322 5.76256 6.07322 6.23744 5.78033 6.53033L1.28033 11.0303C0.987437 11.3232 0.512563 11.3232 0.21967 11.0303C-0.0732233 10.7374 -0.0732233 10.2626 0.21967 9.96967L4.18934 6L0.21967 2.03033C-0.0732233 1.73744 -0.0732233 1.26256 0.21967 0.96967Z" fill="#242424" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div className="2xl:mx-auto 2xl:container px-4 md:px-6 2xl:px-0 py-16 flex justify-center">
        <div className="fle flex-col justify-center items-center">
            <div className="flex justify-start items-start">
                <p className="text-3xl lg:text-4xl font-semibold leading-9 text-gray-800">Featured items</p>
            </div>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 justify-items-between mt-8 gap-y-8 lg:gap-y-0 gap-x-8">
                <div className="flex items-start flex-col">
                    <div className="relative flex justify-center items-center bg-gray-100 py-12 px-16">
                        <a href='/product'>
                          <img src="https://cdn.tuk.dev/assets/templates/e-commerce-kit/bestSeller3.png" width={160} alt="mobile" />
                        </a>
                        <button 
                        className="absolute top-4 right-4 flex justify-center items-center p-3.5 bg-white rounded-full"
                        onClick={showToastMessage}>
                            <svg className="fill-stroke text-gray-600 hover:text-gray-500" width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M6.00002 6.59999V5.39999C6.00002 4.44521 6.37931 3.52953 7.05444 2.8544C7.72957 2.17927 8.64525 1.79999 9.60003 1.79999V1.79999C10.5548 1.79999 11.4705 2.17927 12.1456 2.8544C12.8207 3.52953 13.2 4.44521 13.2 5.39999V6.59999M3.00002 6.59999C2.84089 6.59999 2.68828 6.6632 2.57576 6.77572C2.46324 6.88825 2.40002 7.04086 2.40002 7.19999V15.3C2.40002 16.434 3.36602 17.4 4.50002 17.4H14.7C15.834 17.4 16.8 16.4809 16.8 15.3469V7.19999C16.8 7.04086 16.7368 6.88825 16.6243 6.77572C16.5118 6.6632 16.3592 6.59999 16.2 6.59999H3.00002Z"
                                    stroke="currentColor"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                />
                                <path d="M6 8.40002V9.00002C6 9.9548 6.37928 10.8705 7.05442 11.5456C7.72955 12.2207 8.64522 12.6 9.6 12.6C10.5548 12.6 11.4705 12.2207 12.1456 11.5456C12.8207 10.8705 13.2 9.9548 13.2 9.00002V8.40002" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                        </button>
                    </div>
                    <div className="flex flex-col items-start jusitfy-start mt-3 space-y-3">
                        <div>
                            <p className="text-lg font-medium leading-4 text-gray-800"><a href='/product'>North wolf bag</a></p>
                        </div>
                        <div>
                            <p className="text-lg leading-4 text-gray-600">$900</p>
                        </div>
                    </div>
                </div>

                <div className="flex items-start flex-col">
                    <div className="relative flex justify-center items-center bg-gray-100 py-12 px-16">
                        <a href='/product'>
                          <img src="https://cdn.tuk.dev/assets/templates/e-commerce-kit/bestSeller2.png" width={160} alt="headphones" />
                        </a>
                        <button 
                        className="absolute top-4 right-4 flex justify-center items-center p-3.5 bg-white rounded-full"
                        onClick={showToastMessage}>
                            <svg className="fill-stroke text-gray-600 hover:text-gray-500" width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M6.00002 6.59999V5.39999C6.00002 4.44521 6.37931 3.52953 7.05444 2.8544C7.72957 2.17927 8.64525 1.79999 9.60003 1.79999V1.79999C10.5548 1.79999 11.4705 2.17927 12.1456 2.8544C12.8207 3.52953 13.2 4.44521 13.2 5.39999V6.59999M3.00002 6.59999C2.84089 6.59999 2.68828 6.6632 2.57576 6.77572C2.46324 6.88825 2.40002 7.04086 2.40002 7.19999V15.3C2.40002 16.434 3.36602 17.4 4.50002 17.4H14.7C15.834 17.4 16.8 16.4809 16.8 15.3469V7.19999C16.8 7.04086 16.7368 6.88825 16.6243 6.77572C16.5118 6.6632 16.3592 6.59999 16.2 6.59999H3.00002Z"
                                    stroke="currentColor"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                />
                                <path d="M6 8.40002V9.00002C6 9.9548 6.37928 10.8705 7.05442 11.5456C7.72955 12.2207 8.64522 12.6 9.6 12.6C10.5548 12.6 11.4705 12.2207 12.1456 11.5456C12.8207 10.8705 13.2 9.9548 13.2 9.00002V8.40002" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                        </button>
                    </div>
                    <div className="flex flex-col items-start jusitfy-start mt-3 space-y-3">
                        <div>
                            <p className="text-lg font-medium leading-4 text-gray-800"><a href='/product'>Luxe Signature Ring</a></p>
                        </div>
                        <div>
                            <p className="text-lg leading-4 text-gray-600">$1,500</p>
                        </div>
                    </div>
                </div>

                <div className="flex items-start flex-col">
                    <div className="relative flex justify-center items-center bg-gray-100 py-12 px-16">
                        <a href='/product'>
                          <img src="https://cdn.tuk.dev/assets/templates/e-commerce-kit/bestSeller1.png" width={160} alt="camera" />
                        </a>
                        <button 
                        className="absolute top-4 right-4 flex justify-center items-center p-3.5 bg-white rounded-full"
                        onClick={showToastMessage}>
                            <svg className="fill-stroke text-gray-600 hover:text-gray-500" width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M6.00002 6.59999V5.39999C6.00002 4.44521 6.37931 3.52953 7.05444 2.8544C7.72957 2.17927 8.64525 1.79999 9.60003 1.79999V1.79999C10.5548 1.79999 11.4705 2.17927 12.1456 2.8544C12.8207 3.52953 13.2 4.44521 13.2 5.39999V6.59999M3.00002 6.59999C2.84089 6.59999 2.68828 6.6632 2.57576 6.77572C2.46324 6.88825 2.40002 7.04086 2.40002 7.19999V15.3C2.40002 16.434 3.36602 17.4 4.50002 17.4H14.7C15.834 17.4 16.8 16.4809 16.8 15.3469V7.19999C16.8 7.04086 16.7368 6.88825 16.6243 6.77572C16.5118 6.6632 16.3592 6.59999 16.2 6.59999H3.00002Z"
                                    stroke="currentColor"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                />
                                <path d="M6 8.40002V9.00002C6 9.9548 6.37928 10.8705 7.05442 11.5456C7.72955 12.2207 8.64522 12.6 9.6 12.6C10.5548 12.6 11.4705 12.2207 12.1456 11.5456C12.8207 10.8705 13.2 9.9548 13.2 9.00002V8.40002" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                        </button>
                    </div>
                    <div className="flex flex-col items-start jusitfy-start mt-3 space-y-3">
                        <div>
                            <p className="text-lg font-medium leading-4 text-gray-800"><a href='/product'>Luxe Signature Shoes</a></p>
                        </div>
                        <div>
                            <p className="text-lg leading-4 text-gray-600">$450</p>
                        </div>
                    </div>
                </div>

                <div className="flex items-start flex-col">
                    <div className="relative flex justify-center items-center bg-gray-100 py-12 px-16">
                        <a href='/product'>
                          <img src="https://cdn.tuk.dev/assets/templates/e-commerce-kit/bestSeller3.png" width={160} alt="speaker" />
                        </a>
                        <button 
                        className="absolute top-4 right-4 flex justify-center items-center p-3.5 bg-white rounded-full"
                        onClick={showToastMessage}>
                            <svg className="fill-stroke text-gray-600 hover:text-gray-500" width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M6.00002 6.59999V5.39999C6.00002 4.44521 6.37931 3.52953 7.05444 2.8544C7.72957 2.17927 8.64525 1.79999 9.60003 1.79999V1.79999C10.5548 1.79999 11.4705 2.17927 12.1456 2.8544C12.8207 3.52953 13.2 4.44521 13.2 5.39999V6.59999M3.00002 6.59999C2.84089 6.59999 2.68828 6.6632 2.57576 6.77572C2.46324 6.88825 2.40002 7.04086 2.40002 7.19999V15.3C2.40002 16.434 3.36602 17.4 4.50002 17.4H14.7C15.834 17.4 16.8 16.4809 16.8 15.3469V7.19999C16.8 7.04086 16.7368 6.88825 16.6243 6.77572C16.5118 6.6632 16.3592 6.59999 16.2 6.59999H3.00002Z"
                                    stroke="currentColor"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                />
                                <path d="M6 8.40002V9.00002C6 9.9548 6.37928 10.8705 7.05442 11.5456C7.72955 12.2207 8.64522 12.6 9.6 12.6C10.5548 12.6 11.4705 12.2207 12.1456 11.5456C12.8207 10.8705 13.2 9.9548 13.2 9.00002V8.40002" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                        </button>
                    </div>
                    <div className="flex flex-col items-start jusitfy-start mt-3 space-y-3">
                        <div>
                            <p className="text-lg font-medium leading-4 text-gray-800"><a href='/product'>North wolf bag</a></p>
                        </div>
                        <div>
                            <p className="text-lg leading-4 text-gray-600">$900</p>
                        </div>
                    </div>
                </div>
                <ToastContainer />
            </div>
        </div>
    </div>
      <div className="pb-16">
            <div className="flex justify-center items-center">
                <div className="2xl:mx-auto 2xl:container py-12 px-4 sm:px-6 xl:px-20 2xl:px-0 w-full">
                    <div className="flex flex-col jusitfy-center items-center space-y-10">
                        <div className="flex flex-col justify-center items-center space-y-2">
                            <h1 className="text-2xl xl:text-2xl font-semibold leading-7 xl:leading-9 text-gray-800">Shop By Category</h1>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 md:gap-x-4 md:gap-x-8 w-full">
                            <div className="relative group flex justify-center items-center h-full w-full">
                                <img className="object-center object-cover h-full w-full" src="https://i.ibb.co/ThPFmzv/omid-armin-m-VSb6-PFk-VXw-unsplash-1-1.png" alt="girl" />
                                <button className="focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-400 bottom-4 z-10 absolute text-base font-medium leading-none text-gray-800 py-3 w-36 bg-white" onClick={() => { navigate('/category') }}>Women</button>
                                <div className="absolute opacity-0 group-hover:opacity-100 transition duration-500 bottom-3 py-6 z-0 px-20 w-36 bg-white bg-opacity-50" />
                            </div>
                            <div className="flex flex-col space-y-4 md:space-y-8 mt-4 md:mt-0">
                                <div className="relative group flex justify-center items-center h-full w-full">
                                    <img className="object-center object-cover h-full w-full" src="https://i.ibb.co/SXZvYHs/irene-kredenets-DDqx-X0-7v-KE-unsplash-1.png" alt="shoe" />
                                    <button className="focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-400 bottom-4 z-10 absolute text-base font-medium leading-none text-gray-800 py-3 w-36 bg-white" onClick={() => { navigate('/category') }}>Shoes</button>
                                    <div className="absolute opacity-0 group-hover:opacity-100 transition duration-500 bottom-3 py-6 z-0 px-20 w-36 bg-white bg-opacity-50" />
                                </div>
                                <div className="relative group flex justify-center items-center h-full w-full">
                                    <img className="object-center object-cover h-full w-full" src="https://i.ibb.co/Hd1pVxW/louis-mornaud-Ju-6-TPKXd-Bs-unsplash-1-2.png" alt="watch" />
                                    <button className="focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-400 bottom-4 z-10 absolute text-base font-medium leading-none text-gray-800 py-3 w-36 bg-white" onClick={() => { navigate('/category') }}>Watches</button>
                                    <div className="absolute opacity-0 group-hover:opacity-100 transition duration-500 bottom-3 py-6 z-0 px-20 w-36 bg-white bg-opacity-50" />
                                </div>
                            </div>
                            <div className="relative group justify-center items-center h-full w-full hidden lg:flex">
                                <img className="object-center object-cover h-full w-full" src="https://i.ibb.co/PTtRBLL/olive-tatiane-Im-Ez-F9-B91-Mk-unsplash-1.png" alt="girl" />
                                <button className="focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-400 bottom-4 z-10 absolute text-base font-medium leading-none text-gray-800 py-3 w-36 bg-white" onClick={() => { navigate('/category') }}>Women</button>
                                <div className="absolute opacity-0 group-hover:opacity-100 transition duration-500 bottom-3 py-6 z-0 px-20 w-36 bg-white bg-opacity-50" />
                            </div>
                            <div className="relative group flex justify-center items-center h-full w-full mt-4 md:hidden md:mt-8 lg:hidden">
                                <img className="object-center object-cover h-full w-full hidden md:block" src="https://i.ibb.co/6FjW19n/olive-tatiane-Im-Ez-F9-B91-Mk-unsplash-2.png" alt="girl" />
                                <img className="object-center object-cover h-full w-full md:hidden" src="https://i.ibb.co/sQgHwHn/olive-tatiane-Im-Ez-F9-B91-Mk-unsplash-1.png" alt="olive-tatiane-Im-Ez-F9-B91-Mk-unsplash-2" />
                                <button className="focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-400 bottom-4 z-10 absolute text-base font-medium leading-none text-gray-800 py-3 w-36 bg-white" onClick={() => { navigate('/category') }}>Women</button>
                                <div className="absolute opacity-0 group-hover:opacity-100 transition duration-500 bottom-3 py-6 z-0 px-20 w-36 bg-white bg-opacity-50" />
                            </div>
                        </div>
                        <div className="relative group hidden md:flex justify-center items-center h-full w-full mt-4 md:mt-8 lg:hidden">
                            <img className="object-center object-cover h-full w-full hidden md:block" src="https://i.ibb.co/6FjW19n/olive-tatiane-Im-Ez-F9-B91-Mk-unsplash-2.png" alt="girl" />
                            <img className="object-center object-cover h-full w-full sm:hidden" src="https://i.ibb.co/sQgHwHn/olive-tatiane-Im-Ez-F9-B91-Mk-unsplash-1.png" alt="olive-tatiane-Im-Ez-F9-B91-Mk-unsplash-2" />
                            <button className="focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-400 bottom-4 z-10 absolute text-base font-medium leading-none text-gray-800 py-3 w-36 bg-white" onClick={() => { navigate('/category') }}>Women</button>
                            <div className="absolute opacity-0 group-hover:opacity-100 transition duration-500 bottom-3 py-6 z-0 px-20 w-36 bg-white bg-opacity-50" />
                        </div>
                    </div>
                </div>
            </div>
        </div>


        <div className="px-4 py-12">
        <div className="lg:max-w-[1440px] md:max-w-[744px] max-w-[375px] w-full  py-12 bg-gray-100 mx-auto">
          <div className="mb-10">
            <p className="text-3xl font-semibold leading-9 text-center text-gray-800 lg:text-4xl">
              Valuable Partnerships
            </p>
          </div>
          <div className="lg:max-w-[1280px] w-full bg-white px-12 py-12 mx-auto">
            <div className="block lg:block md:hidden">
              <div className="flex flex-col items-center justify-center lg:justify-between lg:flex-row gap-x-8 gap-y-12">
                <svg
                  width={100}
                  height={20}
                  viewBox="0 0 100 20"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <g clipPath="url(#clip0_2049_3195)">
                    <path
                      d="M6.03911 8.40417L9.92953 4.5203L13.822 8.40622L16.0857 6.14623L9.92953 0L3.77539 6.14417L6.03911 8.40417Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M4.44141 9.99824L2.17773 7.73828L-0.086054 9.99835L2.17762 12.2583L4.44141 9.99824Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M6.04048 11.5956L9.9309 15.4795L13.8232 11.5938L16.0882 13.8525L16.0871 13.8537L9.9309 19.9998L3.7766 13.8558L3.77344 13.8526L6.04048 11.5956Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M17.6835 12.2601L19.9473 10L17.6836 7.74005L15.4198 10.0001L17.6835 12.2601Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M12.2252 10.0004H12.2262L9.92907 7.70703L8.23148 9.40183H8.23132L8.03639 9.5966L7.63402 9.9983L7.63086 10.0015L7.63402 10.0048L9.92907 12.296L12.2262 10.0027L12.2273 10.0015L12.2252 10.0004Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M23.4766 4.84766H28.4C29.622 4.84766 30.546 5.16074 31.1723 5.78691C31.6569 6.27186 31.8992 6.87291 31.8992 7.58991V7.62024C31.8992 7.92322 31.8617 8.19097 31.7862 8.42317C31.7109 8.6557 31.6102 8.865 31.4845 9.05187C31.359 9.2389 31.2131 9.40303 31.0473 9.54425C30.8813 9.68578 30.703 9.8071 30.512 9.90788C31.1262 10.1404 31.6098 10.4559 31.9623 10.8549C32.3147 11.254 32.4911 11.8071 32.4911 12.514V12.5441C32.4911 13.0291 32.3977 13.4532 32.2109 13.817C32.024 14.1805 31.7563 14.4836 31.4077 14.7261C31.0591 14.9686 30.64 15.1502 30.1501 15.2716C29.6603 15.3927 29.1174 15.4532 28.5217 15.4532H23.4766V4.84766ZM27.9078 9.13528C28.4239 9.13528 28.8337 9.04713 29.137 8.87021C29.4405 8.69345 29.5922 8.40801 29.5922 8.0142V7.98388C29.5922 7.63051 29.4606 7.36039 29.1976 7.17336C28.9345 6.98649 28.5551 6.89298 28.0595 6.89298H25.7528V9.13528H27.9078ZM28.5301 13.408C29.0461 13.408 29.4505 13.3148 29.7441 13.1278C30.0375 12.9409 30.1843 12.6505 30.1843 12.2565V12.2263C30.1843 11.8728 30.0476 11.5926 29.7745 11.3853C29.5013 11.1785 29.0612 11.0749 28.4541 11.0749H25.7528V13.4082H28.5301V13.408Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M35.4219 4.84766H37.7592V15.4535H35.4219V4.84766Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M41.2988 4.84766H43.4535L48.4314 11.3779V4.84766H50.7382V15.4535H48.7502L43.6054 8.7113V15.4535H41.2988V4.84766Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M57.8149 4.76953H59.9698L64.5229 15.4511H62.0794L61.1081 13.0724H56.6159L55.6447 15.4511H53.2617L57.8149 4.76953ZM60.2734 11.0116L58.8619 7.57245L57.4509 11.0116H60.2734Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M67.0449 4.84766H69.2001L74.1777 11.3779V4.84766H76.4844V15.4535H74.4965L69.3517 8.7113V15.4535H67.0449V4.84766Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M84.8956 15.6334C84.1162 15.6334 83.3931 15.4919 82.7252 15.2093C82.0573 14.9267 81.4808 14.5401 80.9952 14.0501C80.5094 13.5603 80.1298 12.982 79.8571 12.3154C79.5838 11.6486 79.4473 10.9365 79.4473 10.1789V10.1487C79.4473 9.39114 79.5838 8.68172 79.8571 8.02001C80.13 7.35846 80.5094 6.77762 80.9952 6.27767C81.4806 5.77771 82.0626 5.38359 82.7402 5.09578C83.4179 4.80797 84.1671 4.66406 84.9865 4.66406C85.4819 4.66406 85.9346 4.70466 86.3444 4.78522C86.7542 4.86626 87.1259 4.97715 87.4601 5.11853C87.7941 5.26006 88.1023 5.43177 88.386 5.63365C88.6687 5.83584 88.932 6.05794 89.1749 6.30041L87.6879 8.01243C87.2726 7.63884 86.8504 7.34566 86.4205 7.13367C85.9903 6.92169 85.5074 6.81553 84.9712 6.81553C84.5259 6.81553 84.1136 6.90147 83.7345 7.07317C83.3551 7.24488 83.0287 7.48214 82.7554 7.78512C82.4825 8.08809 82.27 8.43925 82.1179 8.83811C81.9665 9.23728 81.8907 9.66394 81.8907 10.1184V10.1486C81.8907 10.603 81.9665 11.0325 82.1179 11.4363C82.27 11.8405 82.4795 12.1939 82.748 12.4969C83.0159 12.7998 83.3397 13.04 83.719 13.2167C84.0987 13.3936 84.516 13.4818 84.9712 13.4818C85.5785 13.4818 86.0914 13.3707 86.5113 13.1485C86.9313 12.9265 87.3488 12.6234 87.7635 12.2394L89.2508 13.7394C88.9776 14.0324 88.6939 14.2951 88.401 14.5272C88.1075 14.7597 87.7863 14.9591 87.4371 15.1259C87.0882 15.2924 86.706 15.4189 86.2916 15.5045C85.8764 15.5903 85.4112 15.6334 84.8956 15.6334Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M92.002 4.84766H99.9997V6.92346H94.3089V9.07493H99.317V11.1506H94.3089V13.3779H100.076V15.4535H92.002V4.84766Z"
                      fill="#1F2937"
                    />
                  </g>
                  <defs>
                    <clipPath id="clip0_2049_3195">
                      <rect width={100} height={20} fill="white" />
                    </clipPath>
                  </defs>
                </svg>
                <p className="border-r border-gray-400 lg:block hidden h-[30px] " />
                <svg
                  width={100}
                  height={20}
                  viewBox="0 0 100 20"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M28.0684 0.196078H34.2915L35.4503 2.39216H30.7293V4.58824H35.5362V6.78431H30.7293V9.68628H36.0083V11.8824H28.0684V0.196078ZM39.5276 0.196078L43.3902 7.05882L47.0383 0.196078H49.7851L43.3044 12.0784L36.4804 0.196078H39.5276ZM55.0641 0L61.8023 11.8824H58.9267L58.0684 10.3137H51.8881L51.0726 11.8824H48.3259L55.0641 0ZM56.9096 8.11765L54.9353 4.47059L53.004 8.11765H56.9096ZM63.519 0.196078H68.6692C69.5705 0.196078 70.4289 0.352941 71.2443 0.627451C72.0598 0.941177 72.7894 1.33333 73.3902 1.84314C73.9911 2.35294 74.4632 2.98039 74.8065 3.68627C75.1499 4.43137 75.3216 5.17647 75.3216 6C75.3216 6.82353 75.1499 7.60784 74.8065 8.31373C74.4632 9.01961 73.9911 9.64706 73.3902 10.1569C72.7894 10.6667 72.1027 11.0588 71.2443 11.3726C70.4289 11.6863 69.5705 11.8039 68.6692 11.8039H63.519V0.196078ZM68.7121 9.68628C69.828 9.68628 70.7722 9.33333 71.5447 8.62745C72.3173 7.92157 72.7035 7.05882 72.7035 6C72.7035 4.94118 72.3173 4.07843 71.5447 3.41176C70.7722 2.70588 69.828 2.39216 68.7121 2.39216H66.1799V9.68628H68.7121ZM82.1027 0L88.8409 11.8824H85.9653L85.1499 10.3137H78.9696L78.1542 11.8824H75.4074L82.1027 0ZM83.9911 8.11765L82.0168 4.47059L80.0855 8.11765H83.9911ZM89.313 0.196078L93.1757 7.05882L96.8237 0.196078H99.5705L93.0898 12.0784L86.2658 0.196078H89.313Z"
                    fill="#1F2937"
                  />
                  <path
                    d="M29.8293 15.6868V15.177H27.4688V15.6868H28.3271V18.6672H28.928V15.6868H29.8293ZM30.6447 18.6672H31.2027V17.6084C31.2027 17.3339 31.2456 17.177 31.3314 17.0594C31.4172 16.9417 31.546 16.8633 31.7606 16.8633C31.8894 16.8633 32.0181 16.9025 32.061 16.9809C32.1469 17.0594 32.1469 17.177 32.1898 17.2947V18.6672H32.7477V17.3339C32.7477 17.177 32.7477 16.9025 32.576 16.7064L32.5331 16.6672C32.4473 16.5496 32.2327 16.4319 31.8464 16.4319C31.7177 16.4319 31.4602 16.4711 31.2027 16.6672V14.8633H30.6447V18.6672ZM35.5803 17.9613C35.5374 18.0397 35.4516 18.1182 35.3657 18.1966C35.237 18.275 35.1512 18.3143 34.9795 18.3143C34.8507 18.3143 34.6791 18.275 34.5503 18.1574C34.4215 18.0397 34.3357 17.8829 34.3357 17.726H36.0524V17.6476C36.0524 17.4123 36.0095 17.0201 35.7091 16.7064C35.5803 16.5888 35.3228 16.4319 34.9366 16.4319C34.5932 16.4319 34.3357 16.5496 34.1211 16.7456C33.8636 16.9809 33.7348 17.2947 33.7348 17.6476C33.7348 17.9613 33.8636 18.275 34.0782 18.4711C34.2928 18.6672 34.5503 18.7456 34.8936 18.7456C35.1512 18.7456 35.4087 18.7064 35.6233 18.5888C35.7949 18.5103 35.9237 18.3535 36.0095 18.1966L35.5803 17.9613ZM34.4215 17.2947C34.4645 17.177 34.5074 17.0986 34.5932 17.0201C34.679 16.9417 34.8078 16.8633 34.9795 16.8633C35.1512 16.8633 35.2799 16.9417 35.3657 16.9809C35.4516 17.0594 35.4945 17.177 35.5374 17.2947H34.4215ZM41.3314 15.2162H39.2284V18.7064H41.3314V18.1966H39.8293V17.0986H41.2885V16.5888H39.8293V15.6868H41.3314V15.2162ZM42.2327 16.4711L43.4773 18.8241L44.722 16.4711H44.0782L43.4773 17.726L42.8765 16.4711H42.2327ZM46.825 16.4319C46.0954 16.4319 45.5374 16.9025 45.5374 17.6084C45.5374 18.275 46.0954 18.7848 46.825 18.7848C47.5546 18.7848 48.1125 18.275 48.1125 17.6084C48.1125 16.9025 47.5117 16.4319 46.825 16.4319ZM46.825 18.275C46.3958 18.275 46.0954 18.0005 46.0954 17.5692C46.0954 17.0594 46.4387 16.8633 46.825 16.8633C47.1683 16.8633 47.5546 17.0594 47.5546 17.5692C47.5117 18.0005 47.2542 18.275 46.825 18.275ZM49.2284 14.8633V18.6672H49.7863V14.8633H49.2284ZM50.7735 16.4711L52.0181 18.8241L53.2627 16.4711H52.619L52.0181 17.726L51.4172 16.4711H50.7735ZM54.2069 16.4711V18.6672H54.7649V16.4711H54.2069ZM54.1211 15.5692C54.1211 15.7652 54.2928 15.8829 54.4645 15.8829C54.6791 15.8829 54.8078 15.726 54.8078 15.5692C54.8078 15.3731 54.6361 15.2554 54.4645 15.2554C54.2928 15.2554 54.1211 15.3731 54.1211 15.5692ZM56.0524 18.6672H56.6104V17.6476C56.6104 16.9809 56.825 16.9025 57.0825 16.9025H57.1683C57.34 16.9025 57.5546 16.9809 57.5546 17.4907V18.7064H58.1125V17.3731C58.1125 17.0201 58.0696 16.8633 57.9838 16.7456L57.9409 16.7064C57.855 16.5888 57.6404 16.4711 57.2542 16.4711H57.1683C57.0396 16.4711 56.7821 16.5103 56.6104 16.7456V16.4711H56.0524V18.6672ZM61.1597 16.7064C60.9451 16.4711 60.6876 16.3927 60.4301 16.3927C60.1297 16.3927 59.8722 16.4711 59.6147 16.7064C59.443 16.8633 59.2713 17.1378 59.2713 17.5692C59.2713 17.9221 59.4001 18.2358 59.6147 18.4319C59.8293 18.6672 60.0868 18.7456 60.4301 18.7456H60.516C60.6876 18.7456 60.9451 18.6672 61.1597 18.4319V18.7064C61.1597 18.8633 61.1597 19.0986 60.9881 19.2554C60.9022 19.3339 60.7735 19.4123 60.5589 19.4123C60.3443 19.4123 60.1726 19.3339 60.1297 19.2554C60.0439 19.177 59.958 19.0201 59.958 18.9025H59.4001C59.443 19.177 59.5718 19.4123 59.7434 19.5692C59.958 19.7652 60.2584 19.8437 60.516 19.8437C60.9022 19.8437 61.1597 19.726 61.3314 19.6084C61.6748 19.3339 61.7177 18.9809 61.7177 18.4711V16.4711H61.1597V16.7064ZM60.516 16.9025C60.6876 16.9025 60.8164 16.9417 60.9881 17.0594C61.1168 17.177 61.2027 17.3731 61.2027 17.6084C61.2027 17.7652 61.1597 17.9613 60.9881 18.1182C60.8593 18.2358 60.6876 18.3143 60.516 18.3143C60.3443 18.3143 60.1726 18.2358 60.0868 18.1574C59.958 18.0397 59.8293 17.8045 59.8293 17.6084C59.8293 17.3731 59.9151 17.177 60.0868 17.0594C60.2155 16.9417 60.3443 16.9025 60.516 16.9025ZM67.6404 18.6672H68.2842L66.4816 14.9809L64.5932 18.6672H65.237L65.6662 17.8437H67.2971L67.6404 18.6672ZM65.8378 17.3339L66.4387 16.1574L66.9967 17.3339H65.8378ZM70.9881 16.7456C70.7735 16.4711 70.4301 16.4319 70.2584 16.4319C69.6147 16.4319 69.0997 16.8633 69.0997 17.5692C69.0997 18.1574 69.5288 18.7456 70.2584 18.7456C70.4301 18.7456 70.7305 18.7064 70.9881 18.4319V18.6672H71.546V14.8633H70.9881V16.7456ZM70.3443 16.9025C70.6876 16.9025 71.031 17.1378 71.031 17.6084C71.031 18.079 70.6876 18.3143 70.3443 18.3143C69.958 18.3143 69.6576 18.0005 69.6576 17.6084C69.6576 17.2162 69.9151 16.9025 70.3443 16.9025ZM75.4087 18.6672V16.2358L78.1554 18.9025V15.2162H77.5546V17.6476L74.8078 14.9809V18.7064L75.4087 18.6672ZM81.2456 17.9613C81.2027 18.0397 81.1168 18.1182 81.031 18.1966C80.9022 18.275 80.8164 18.3143 80.6447 18.3143C80.516 18.3143 80.3443 18.275 80.2155 18.1574C80.0868 18.0397 80.0009 17.8829 80.0009 17.726H81.7177V17.6476C81.7177 17.4123 81.6748 17.0201 81.3743 16.7064C81.2456 16.5888 80.9881 16.4319 80.6018 16.4319C80.2585 16.4319 80.0009 16.5496 79.7863 16.7456C79.5288 16.9809 79.4001 17.2947 79.4001 17.6476C79.4001 17.9613 79.5288 18.275 79.7434 18.4711C79.958 18.6672 80.2155 18.7456 80.5589 18.7456C80.8164 18.7456 81.0739 18.7064 81.2885 18.5888C81.4602 18.5103 81.5889 18.3535 81.6748 18.1966L81.2456 17.9613ZM80.0439 17.2947C80.0868 17.177 80.1297 17.0986 80.2155 17.0201C80.3014 16.9417 80.4301 16.8633 80.6018 16.8633C80.7735 16.8633 80.9022 16.9417 80.9881 16.9809C81.0739 17.0594 81.1168 17.177 81.1597 17.2947H80.0439ZM83.9065 16.9417V16.4711H83.4773V15.6868H82.9194V16.4711H82.7048V16.9417H82.9194V18.6672H83.4773V16.9417H83.9065ZM84.6361 16.4711L85.8808 18.8241L86.5675 17.4123L87.2542 18.8241L88.4988 16.4711H87.855L87.2112 17.726L86.5245 16.275L85.8378 17.726L85.1941 16.4711H84.6361ZM90.5589 16.4319C89.8293 16.4319 89.2713 16.9025 89.2713 17.6084C89.2713 18.275 89.8293 18.7848 90.5589 18.7848C91.2885 18.7848 91.8464 18.275 91.8464 17.6084C91.8464 16.9025 91.2885 16.4319 90.5589 16.4319ZM90.5589 18.275C90.1297 18.275 89.8293 18.0005 89.8293 17.5692C89.8293 17.0594 90.1726 16.8633 90.5589 16.8633C90.9022 16.8633 91.2885 17.0594 91.2885 17.5692C91.2456 18.0005 90.9881 18.275 90.5589 18.275ZM92.9623 18.6672H93.5202V17.5299C93.5202 17.3731 93.5203 17.177 93.6919 17.0201C93.7778 16.9417 93.9065 16.9025 93.9924 16.9025H94.0353C94.0782 16.9025 94.2069 16.9025 94.3357 16.9809L94.5503 16.5103C94.3786 16.4319 94.2499 16.3927 94.1211 16.3927C93.9924 16.3927 93.9065 16.3927 93.7778 16.4711C93.6919 16.5103 93.6061 16.5888 93.5632 16.6672V16.4711H93.0052L92.9623 18.6672ZM95.4516 14.8633H96.0095V17.2162L96.7821 16.4711H97.5117L96.4816 17.3731L97.5975 18.6672H96.8679L96.0954 17.726L96.0095 17.8045V18.6672H95.4516V14.8633Z"
                    fill="#4B5563"
                  />
                  <mask
                    id="mask0_2049_3208"
                    style={{ maskType: "alpha" }}
                    maskUnits="userSpaceOnUse"
                    x={0}
                    y={0}
                    width={13}
                    height={19}
                  >
                    <path
                      d="M7.16738 0.195312L12.9185 9.29335L7.03863 18.509H0L5.87983 9.29335L0 0.195312H7.16738Z"
                      fill="white"
                    />
                  </mask>
                  <g mask="url(#mask0_2049_3208)">
                    <path
                      d="M7.16738 0.195312L12.9185 9.29335L7.03863 18.509H0L5.87983 9.29335L0 0.195312H7.16738Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M5.19287 8.23438L9.99973 15.4893C9.6993 19.254 9.48471 21.1363 9.31304 21.1363C9.14136 21.1363 5.92248 20.7834 -0.386533 20.0775C-1.20198 17.9207 -1.50241 16.8618 -1.37366 16.8618C-1.2449 16.901 0.943939 14.0383 5.19287 8.23438Z"
                      fill="#1F2937"
                    />
                  </g>
                  <mask
                    id="mask1_2049_3208"
                    style={{ maskType: "alpha" }}
                    maskUnits="userSpaceOnUse"
                    x={9}
                    y={0}
                    width={14}
                    height={19}
                  >
                    <path
                      d="M17.0384 0.195312L22.7895 9.29335L16.9097 18.5482H9.82812L15.708 9.33256L9.82812 0.195312H17.0384Z"
                      fill="white"
                    />
                  </mask>
                  <g mask="url(#mask1_2049_3208)">
                    <path
                      d="M17.0384 0.195312L22.7895 9.29335L16.9097 18.5482H9.82812L15.708 9.33256L9.82812 0.195312H17.0384Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M15.0649 8.35156L19.8718 15.6457C19.5714 19.4104 19.3568 21.2927 19.1851 21.2927C19.0134 21.2927 15.7945 20.9398 9.44261 20.2339C8.67008 18.0771 8.32673 17.0182 8.4984 17.0182C8.62716 17.0574 10.816 14.1555 15.0649 8.35156Z"
                      fill="#1F2937"
                    />
                  </g>
                </svg>
                <p className="border-r border-gray-400 lg:block hidden h-[30px]" />
                <svg
                  width={100}
                  height={20}
                  viewBox="0 0 100 20"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M35.6824 19.7766C32.0744 19.7766 28.7252 18.5701 26.4896 16.3325C24.8006 14.642 23.989 12.3457 23.989 9.98235C23.989 7.64775 24.8356 5.33567 26.4894 3.65408C28.5656 1.54407 32.2312 0.222656 35.6824 0.222656C39.5016 0.222656 42.5584 1.2954 44.8952 3.65988C46.5578 5.34236 47.3616 7.64418 47.3616 9.98257C47.3616 12.2492 46.5086 14.6629 44.8952 16.3325C42.7192 18.5846 39.2996 19.7766 35.6824 19.7766V17.1976C37.5974 17.1976 39.3738 16.4603 40.6144 15.0838C41.8464 13.7166 42.4204 12.0362 42.4204 9.98235C42.4204 8.01484 41.8012 6.17535 40.6144 4.87067C39.3904 3.52629 37.5716 2.7698 35.6824 2.7698C33.7874 2.7698 31.9674 3.51848 30.7424 4.87067C29.562 6.17491 28.9412 8.01975 28.9412 9.98235C28.9412 11.9389 29.5692 13.7827 30.7424 15.084C31.9684 16.444 33.782 17.1978 35.6824 17.1978V19.7768V19.7766ZM9.31162 0.232023C7.38162 0.232023 5.18902 0.634579 3.32602 1.56235C1.60662 2.41787 0.199219 3.8015 0.199219 6.09529C0.198419 8.16115 1.37582 9.37104 1.34382 9.33759C1.84462 9.85166 2.65082 10.727 4.75862 11.2411C5.70062 11.4708 7.71462 11.8236 9.72022 12.0574C11.711 12.2915 13.6702 12.5141 14.4682 12.7394C15.1022 12.9193 16.1672 13.1644 16.1672 14.4968C16.1672 15.8238 15.0452 16.2288 14.8502 16.3166C14.6554 16.4025 13.3094 17.0912 10.8898 17.0912C9.10342 17.0912 6.95582 16.4922 6.17302 16.1799C5.27062 15.8218 4.32402 15.3481 3.44102 14.1453C3.22142 13.8471 2.87502 13.0271 2.87502 12.215H0.685219V19.0574H3.11922V18.1329C3.11922 18.0277 3.23722 17.5948 3.64582 17.8006C4.15422 18.0582 5.64662 18.7208 7.20702 19.0841C8.48642 19.3825 9.31142 19.5964 10.902 19.5964C13.4972 19.5964 14.8914 19.1249 15.8552 18.8181C16.7632 18.5281 17.8852 18.0076 18.7966 17.1971C19.2902 16.7589 20.3726 15.6355 20.3726 13.5964C20.3726 11.6392 19.4306 10.4244 19.0992 10.0548C18.6478 9.55125 18.0964 9.16096 17.5218 8.8601C17.0212 8.59738 16.2312 8.2818 15.5848 8.10539C14.3302 7.76194 11.4934 7.33819 10.1368 7.17985C8.71422 7.01414 6.24642 6.78621 5.26082 6.4461C4.96202 6.34284 4.35282 6.01924 4.35282 5.23063C4.35282 4.66973 4.63142 4.19424 5.18202 3.80997C6.05602 3.19934 7.82142 2.81975 9.66162 2.81975C11.8372 2.81083 13.6796 3.36549 14.8516 3.94981C15.2502 4.1483 15.7166 4.43332 16.087 4.77053C16.505 5.15056 17.0918 5.94029 17.304 7.0418H19.27V1.08575H17.0748V1.77802C17.0748 2.00148 16.8678 2.29186 16.4764 2.05189C15.494 1.47716 12.7164 0.237153 9.31122 0.232023H9.31162ZM57.4184 1.31435L68.1268 12.0908L68.0168 4.83521C68.006 3.8838 67.8488 3.48659 66.926 3.48659H64.9126V1.31614H74.0686V3.48659H72.1046C71.1634 3.48659 71.104 3.82224 71.0926 4.83521L71.2586 18.699H68.123L55.789 6.4238L55.7916 15.1355C55.8024 16.0825 55.8422 16.5285 56.7172 16.5285H58.9162V18.6981H49.9242V16.5287H52.0262C52.8114 16.5287 52.7802 15.694 52.7802 15.0862V4.91773C52.7802 4.26137 52.6976 3.48815 51.4648 3.48815H49.7592V1.31435H57.4184ZM84.5312 16.5245C84.6172 16.5245 84.9992 16.5122 85.0732 16.487C85.2846 16.4134 85.428 16.2453 85.4944 16.07C85.5224 15.9964 85.5364 15.6708 85.5364 15.6001L85.538 12.17C85.538 12.0875 85.5326 12.0518 85.407 11.868C85.269 11.6673 79.798 4.75358 79.5476 4.44916C79.2366 4.07113 78.6906 3.48682 77.861 3.48682H75.9584V1.31547H86.6958V3.48414H85.4014C85.102 3.48414 84.903 3.80083 85.1588 4.15276C85.1588 4.15276 88.7714 8.97161 88.8056 9.02201C88.8392 9.07331 88.868 9.08558 88.914 9.03874C88.9592 8.99079 92.6172 4.19692 92.646 4.15901C92.82 3.92662 92.702 3.48659 92.327 3.48659H90.9992V1.31547H99.7992V3.48659H97.8332C97.12 3.48659 96.8298 3.63379 96.2932 4.31021C96.0478 4.61977 90.5184 11.6577 90.368 11.8484C90.2892 11.9481 90.296 12.087 90.296 12.1695V15.5992C90.296 15.6688 90.31 15.9948 90.338 16.068C90.4046 16.2442 90.5488 16.4123 90.76 16.485C90.834 16.5104 91.2108 16.5229 91.2966 16.5229H93.3076V18.6938H82.6256V16.5227L84.5316 16.5245H84.5312Z"
                    fill="#1F2937"
                  />
                </svg>
                <p className="border-r border-gray-400 lg:block hidden h-[30px]" />
                <svg
                  width={101}
                  height={20}
                  viewBox="0 0 101 20"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M85.4336 7.91406V19.9748H87.9552V11.9448H97.1327V19.9748H99.6525V7.93498L85.4336 7.91406Z"
                    fill="#1F2937"
                  />
                  <path
                    d="M87.6753 4.01277H97.3713C98.718 3.60215 99.7195 1.77917 100.002 0.015625H85.0449C85.3245 1.77972 86.3407 3.60215 87.6753 4.01277Z"
                    fill="#1F2937"
                  />
                  <path
                    d="M77.7943 19.9844C79.0657 19.1576 79.7496 17.7277 80.0116 16.0544H68.7019L68.7091 0.0273438L66.1738 0.038346V19.9844H77.7943Z"
                    fill="#1F2937"
                  />
                  <path
                    d="M47.3223 3.95901H56.2769C57.6269 3.35741 58.7605 1.77992 59.0368 0.03125H44.8122V11.8184H56.4546V15.9548L47.3223 15.9658C45.8912 16.5778 44.6776 18.0519 44.0723 19.9987L44.8122 19.9778H58.9561V7.89944H47.3223V3.95901Z"
                    fill="#1F2937"
                  />
                  <path
                    d="M25.2177 3.99873H34.9105C36.259 3.58647 37.2613 1.76517 37.5422 0H22.5859C22.8651 1.76517 23.8821 3.58647 25.2177 3.99873Z"
                    fill="#1F2937"
                  />
                  <path
                    d="M25.2177 11.8799H34.9105C36.259 11.4721 37.2613 9.64909 37.5422 7.88281H22.5859C22.8651 9.64964 23.8821 11.4721 25.2177 11.8799Z"
                    fill="#1F2937"
                  />
                  <path
                    d="M25.2177 19.982H34.9105C36.259 19.5709 37.2613 17.7484 37.5422 15.9844H22.5859C22.8651 17.749 23.8821 19.5709 25.2177 19.982Z"
                    fill="#1F2937"
                  />
                  <path
                    d="M0 0.0463457C0.291381 1.78951 1.27533 3.57121 2.6253 4.0176H6.70536L6.91349 4.14364V19.9356H9.46128V4.14364L9.69274 4.0176H13.7764C15.1414 3.47819 16.1042 1.78951 16.3906 0.0463457V0.0078125H0V0.0463457Z"
                    fill="#1F2937"
                  />
                </svg>
                <p className="border-r border-gray-400 lg:block hidden h-[30px]" />
                <svg
                  width={101}
                  height={30}
                  viewBox="0 0 101 30"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <g clipPath="url(#clip0_2049_3237)">
                    <path
                      d="M96.8861 18.3353L99.6602 20.0261C98.7598 21.2387 96.6063 23.3189 92.8831 23.3189C88.2597 23.3189 84.8164 20.0484 84.8164 15.8879C84.8164 11.4605 88.2962 8.45703 92.4938 8.45703C96.7158 8.45703 98.7841 11.5273 99.4533 13.1848L99.8183 14.0302L88.941 18.1461C89.7684 19.6368 91.0581 20.3932 92.8831 20.3932C94.7082 20.3932 95.9736 19.57 96.8861 18.3353ZM88.357 15.6543L95.6207 12.8956C95.2192 11.9723 94.0268 11.3159 92.6033 11.3159C90.7904 11.3159 88.2718 12.7843 88.357 15.6543Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M79.5723 0.882812H83.0764V22.6416H79.5723V0.882812Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M74.0488 9.03489H77.4312V22.2504C77.4312 27.7345 73.8906 29.9927 69.7051 29.9927C65.763 29.9927 63.3905 27.5677 62.5023 25.5987L65.6049 24.4196C66.1645 25.6321 67.5151 27.0671 69.7051 27.0671C72.3941 27.0671 74.0488 25.5431 74.0488 22.6953V21.6274H73.9271C73.1241 22.5173 71.591 23.3183 69.6443 23.3183C65.5805 23.3183 61.8574 20.0811 61.8574 15.9096C61.8574 11.7158 65.5805 8.44531 69.6443 8.44531C71.5789 8.44531 73.1241 9.23513 73.9271 10.1028H74.0488V9.03489ZM74.2921 15.9096C74.2921 13.2843 72.3819 11.371 69.9485 11.371C67.4908 11.371 65.4224 13.2843 65.4224 15.9096C65.4224 18.5015 67.4908 20.3815 69.9485 20.3815C72.3819 20.3926 74.2921 18.5015 74.2921 15.9096Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M42.6223 15.8561C42.6223 20.1389 38.9722 23.287 34.4948 23.287C30.0173 23.287 26.3672 20.1278 26.3672 15.8561C26.3672 11.5511 30.0173 8.41406 34.4948 8.41406C38.9722 8.41406 42.6223 11.5511 42.6223 15.8561ZM39.0695 15.8561C39.0695 13.1863 36.9525 11.3508 34.4948 11.3508C32.037 11.3508 29.92 13.1863 29.92 15.8561C29.92 18.5036 32.037 20.3614 34.4948 20.3614C36.9525 20.3614 39.0695 18.5036 39.0695 15.8561Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M60.3723 15.8879C60.3723 20.1707 56.7222 23.3189 52.2447 23.3189C47.7673 23.3189 44.1172 20.1707 44.1172 15.8879C44.1172 11.5829 47.7673 8.45703 52.2447 8.45703C56.7222 8.45703 60.3723 11.5718 60.3723 15.8879ZM56.8074 15.8879C56.8074 13.2182 54.6903 11.3827 52.2326 11.3827C49.7748 11.3827 47.6578 13.2182 47.6578 15.8879C47.6578 18.5355 49.7748 20.3932 52.2326 20.3932C54.7025 20.3932 56.8074 18.5244 56.8074 15.8879Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M13.007 20.0592C7.90904 20.0592 3.91826 16.2992 3.91826 11.6382C3.91826 6.9772 7.90904 3.21725 13.007 3.21725C15.7568 3.21725 17.7643 4.2073 19.2487 5.47545L21.6943 3.2395C19.6259 1.42627 16.864 0.046875 13.007 0.046875C6.02315 0.046875 0.146484 5.25296 0.146484 11.6382C0.146484 18.0235 6.02315 23.2295 13.007 23.2295C16.7788 23.2295 19.6259 22.0949 21.8524 19.9813C24.1398 17.89 24.8455 14.9532 24.8455 12.5726C24.8455 11.8273 24.7482 11.0598 24.6387 10.4924H13.007V13.5849H21.2928C21.0494 15.5205 20.3802 16.8443 19.3947 17.7454C18.2023 18.8466 16.3164 20.0592 13.007 20.0592Z"
                      fill="#1F2937"
                    />
                  </g>
                  <defs>
                    <clipPath id="clip0_2049_3237">
                      <rect
                        width={100}
                        height={30}
                        fill="white"
                        transform="translate(0.00195312)"
                      />
                    </clipPath>
                  </defs>
                </svg>
                <p className="border-r border-gray-400 lg:block hidden h-[30px]" />
                <svg
                  width={101}
                  height={20}
                  viewBox="0 0 101 20"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M6.33695 19.6918H2.56885V9.98507H0.00195312V6.82477H2.56875V4.57599C2.56875 1.91118 3.70405 0 7.46195 0C8.25675 0 9.50455 0.165543 9.50455 0.165543V3.10005H8.19395C6.85855 3.10005 6.33715 3.5198 6.33715 4.68026V6.82477H9.45455L9.17695 9.98507H6.33705L6.33695 19.6918ZM14.983 6.57222C14.9281 6.57222 14.8716 6.57429 14.8157 6.57573C11.3217 6.57573 9.72305 9.29159 9.72305 13.1468C9.72305 18.0034 11.7967 19.9471 14.843 19.9471C16.5859 19.9471 17.731 19.189 18.427 17.7744V19.6931H22.011V6.82611H18.427V8.80488C17.8587 7.53179 16.6816 6.58731 14.983 6.57222ZM15.8943 9.61265C17.3618 9.61265 18.2426 10.6704 18.2426 12.4696L18.246 14.3072C18.246 15.5198 17.5185 16.9385 15.8943 16.9385C13.3973 16.9385 13.464 14.1524 13.464 13.2244C13.464 10.103 14.7944 9.61265 15.8943 9.61265ZM23.4584 13.2603C23.4584 11.6967 23.386 6.58059 29.8364 6.58059C32.4257 6.58059 33.5069 7.43135 33.5069 7.43135L32.6379 10.2165C32.6379 10.2165 31.5581 9.60211 30.1511 9.60211C28.349 9.60211 27.1991 10.6817 27.1991 12.5811L27.2011 13.943C27.2011 15.7681 28.3106 16.9864 30.1548 16.9864C31.4366 16.9864 32.618 16.3662 32.618 16.3662L33.4848 19.0932C33.4848 19.0932 32.4962 19.9494 29.8545 19.9494C23.7127 19.9494 23.4585 15.3592 23.4585 13.2603H23.4584ZM54.5212 6.57573C58.0153 6.57573 59.639 9.29159 59.639 13.1468C59.639 18.0034 57.5654 19.9471 54.5191 19.9471C52.7762 19.9471 51.4878 19.1891 50.7918 17.7744V19.6931L47.2529 19.6916V0.391227L51.0103 0.0525976V8.63055C51.5526 7.12981 53.3348 6.57573 54.5213 6.57573H54.5212ZM53.4678 9.61265C52.0003 9.61265 51.0103 10.6704 51.0103 12.4696L51.0068 14.3072C51.0046 15.5198 51.6924 16.9385 53.4678 16.9385C55.9648 16.9385 55.8981 14.1524 55.8981 13.2244C55.8981 10.103 54.5678 9.61265 53.4678 9.61265ZM40.0263 6.58638C36.0633 6.58638 33.9711 8.81914 33.9711 12.787V13.5242C33.9711 18.6741 36.9092 20 40.412 20C43.8167 20 45.3578 19.0159 45.3578 19.0159L44.6547 16.3954C44.6547 16.3954 42.8419 17.1924 40.8625 17.1924C38.8105 17.1924 37.928 16.6519 37.7018 14.6142H45.6582V12.5118C45.6582 8.2077 43.3101 6.58627 40.0262 6.58627L40.0263 6.58638ZM40.1218 9.21047C41.4936 9.21047 42.3825 10.0797 42.3337 12.0957H37.7087C37.7889 9.97391 38.7475 9.21057 40.1218 9.21057V9.21047ZM67.1312 6.56871C63.0615 6.56871 60.919 8.93859 60.919 13.1856C60.919 19.0126 64.6122 19.9506 67.138 19.9506C70.8356 19.9506 73.2956 17.8935 73.2956 13.2385C73.2956 8.3934 70.5296 6.56871 67.1312 6.56871ZM67.08 9.62319C68.8695 9.62319 69.5786 11.0072 69.5786 12.5825V13.9369C69.5786 15.8453 68.5863 16.9491 67.0732 16.9491C65.658 16.9491 64.6634 15.9166 64.6634 13.9369V12.5825C64.6634 10.4712 65.8469 9.62319 67.08 9.62319ZM80.781 6.56871C76.7113 6.56871 74.5688 8.93859 74.5688 13.1856C74.5688 19.0126 78.262 19.9506 80.7878 19.9506C84.4853 19.9506 86.9454 17.8935 86.9454 13.2385C86.9454 8.3934 84.1793 6.56871 80.781 6.56871ZM80.7298 9.62319C82.5193 9.62319 83.2283 11.0072 83.2283 12.5825V13.9369C83.2283 15.8453 82.2361 16.9491 80.723 16.9491C79.3078 16.9491 78.3132 15.9166 78.3132 13.9369V12.5825C78.3132 10.4712 79.4967 9.62319 80.7298 9.62319ZM88.3653 19.6918V0.391227L92.1336 0.0525976V12.989L95.8722 6.82477H99.8518L95.9518 13.2091L100.002 19.6918H96.0111L92.1336 13.3972V19.6918H88.3653Z"
                    fill="#1F2937"
                  />
                </svg>
              </div>
            </div>
            <div className="hidden lg:hidden md:block ">
              <div className="flex justify-between gap-x-8 ">
                <svg
                  width={100}
                  height={20}
                  viewBox="0 0 100 20"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <g clipPath="url(#clip0_2049_3195)">
                    <path
                      d="M6.03911 8.40417L9.92953 4.5203L13.822 8.40622L16.0857 6.14623L9.92953 0L3.77539 6.14417L6.03911 8.40417Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M4.44141 9.99824L2.17773 7.73828L-0.086054 9.99835L2.17762 12.2583L4.44141 9.99824Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M6.04048 11.5956L9.9309 15.4795L13.8232 11.5938L16.0882 13.8525L16.0871 13.8537L9.9309 19.9998L3.7766 13.8558L3.77344 13.8526L6.04048 11.5956Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M17.6835 12.2601L19.9473 10L17.6836 7.74005L15.4198 10.0001L17.6835 12.2601Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M12.2252 10.0004H12.2262L9.92907 7.70703L8.23148 9.40183H8.23132L8.03639 9.5966L7.63402 9.9983L7.63086 10.0015L7.63402 10.0048L9.92907 12.296L12.2262 10.0027L12.2273 10.0015L12.2252 10.0004Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M23.4766 4.84766H28.4C29.622 4.84766 30.546 5.16074 31.1723 5.78691C31.6569 6.27186 31.8992 6.87291 31.8992 7.58991V7.62024C31.8992 7.92322 31.8617 8.19097 31.7862 8.42317C31.7109 8.6557 31.6102 8.865 31.4845 9.05187C31.359 9.2389 31.2131 9.40303 31.0473 9.54425C30.8813 9.68578 30.703 9.8071 30.512 9.90788C31.1262 10.1404 31.6098 10.4559 31.9623 10.8549C32.3147 11.254 32.4911 11.8071 32.4911 12.514V12.5441C32.4911 13.0291 32.3977 13.4532 32.2109 13.817C32.024 14.1805 31.7563 14.4836 31.4077 14.7261C31.0591 14.9686 30.64 15.1502 30.1501 15.2716C29.6603 15.3927 29.1174 15.4532 28.5217 15.4532H23.4766V4.84766ZM27.9078 9.13528C28.4239 9.13528 28.8337 9.04713 29.137 8.87021C29.4405 8.69345 29.5922 8.40801 29.5922 8.0142V7.98388C29.5922 7.63051 29.4606 7.36039 29.1976 7.17336C28.9345 6.98649 28.5551 6.89298 28.0595 6.89298H25.7528V9.13528H27.9078ZM28.5301 13.408C29.0461 13.408 29.4505 13.3148 29.7441 13.1278C30.0375 12.9409 30.1843 12.6505 30.1843 12.2565V12.2263C30.1843 11.8728 30.0476 11.5926 29.7745 11.3853C29.5013 11.1785 29.0612 11.0749 28.4541 11.0749H25.7528V13.4082H28.5301V13.408Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M35.4219 4.84766H37.7592V15.4535H35.4219V4.84766Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M41.2988 4.84766H43.4535L48.4314 11.3779V4.84766H50.7382V15.4535H48.7502L43.6054 8.7113V15.4535H41.2988V4.84766Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M57.8149 4.76953H59.9698L64.5229 15.4511H62.0794L61.1081 13.0724H56.6159L55.6447 15.4511H53.2617L57.8149 4.76953ZM60.2734 11.0116L58.8619 7.57245L57.4509 11.0116H60.2734Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M67.0449 4.84766H69.2001L74.1777 11.3779V4.84766H76.4844V15.4535H74.4965L69.3517 8.7113V15.4535H67.0449V4.84766Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M84.8956 15.6334C84.1162 15.6334 83.3931 15.4919 82.7252 15.2093C82.0573 14.9267 81.4808 14.5401 80.9952 14.0501C80.5094 13.5603 80.1298 12.982 79.8571 12.3154C79.5838 11.6486 79.4473 10.9365 79.4473 10.1789V10.1487C79.4473 9.39114 79.5838 8.68172 79.8571 8.02001C80.13 7.35846 80.5094 6.77762 80.9952 6.27767C81.4806 5.77771 82.0626 5.38359 82.7402 5.09578C83.4179 4.80797 84.1671 4.66406 84.9865 4.66406C85.4819 4.66406 85.9346 4.70466 86.3444 4.78522C86.7542 4.86626 87.1259 4.97715 87.4601 5.11853C87.7941 5.26006 88.1023 5.43177 88.386 5.63365C88.6687 5.83584 88.932 6.05794 89.1749 6.30041L87.6879 8.01243C87.2726 7.63884 86.8504 7.34566 86.4205 7.13367C85.9903 6.92169 85.5074 6.81553 84.9712 6.81553C84.5259 6.81553 84.1136 6.90147 83.7345 7.07317C83.3551 7.24488 83.0287 7.48214 82.7554 7.78512C82.4825 8.08809 82.27 8.43925 82.1179 8.83811C81.9665 9.23728 81.8907 9.66394 81.8907 10.1184V10.1486C81.8907 10.603 81.9665 11.0325 82.1179 11.4363C82.27 11.8405 82.4795 12.1939 82.748 12.4969C83.0159 12.7998 83.3397 13.04 83.719 13.2167C84.0987 13.3936 84.516 13.4818 84.9712 13.4818C85.5785 13.4818 86.0914 13.3707 86.5113 13.1485C86.9313 12.9265 87.3488 12.6234 87.7635 12.2394L89.2508 13.7394C88.9776 14.0324 88.6939 14.2951 88.401 14.5272C88.1075 14.7597 87.7863 14.9591 87.4371 15.1259C87.0882 15.2924 86.706 15.4189 86.2916 15.5045C85.8764 15.5903 85.4112 15.6334 84.8956 15.6334Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M92.002 4.84766H99.9997V6.92346H94.3089V9.07493H99.317V11.1506H94.3089V13.3779H100.076V15.4535H92.002V4.84766Z"
                      fill="#1F2937"
                    />
                  </g>
                  <defs>
                    <clipPath id="clip0_2049_3195">
                      <rect width={100} height={20} fill="white" />
                    </clipPath>
                  </defs>
                </svg>
                <p className="border-r border-gray-400 h-[30px]" />
                <svg
                  width={100}
                  height={20}
                  viewBox="0 0 100 20"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M28.0684 0.196078H34.2915L35.4503 2.39216H30.7293V4.58824H35.5362V6.78431H30.7293V9.68628H36.0083V11.8824H28.0684V0.196078ZM39.5276 0.196078L43.3902 7.05882L47.0383 0.196078H49.7851L43.3044 12.0784L36.4804 0.196078H39.5276ZM55.0641 0L61.8023 11.8824H58.9267L58.0684 10.3137H51.8881L51.0726 11.8824H48.3259L55.0641 0ZM56.9096 8.11765L54.9353 4.47059L53.004 8.11765H56.9096ZM63.519 0.196078H68.6692C69.5705 0.196078 70.4289 0.352941 71.2443 0.627451C72.0598 0.941177 72.7894 1.33333 73.3902 1.84314C73.9911 2.35294 74.4632 2.98039 74.8065 3.68627C75.1499 4.43137 75.3216 5.17647 75.3216 6C75.3216 6.82353 75.1499 7.60784 74.8065 8.31373C74.4632 9.01961 73.9911 9.64706 73.3902 10.1569C72.7894 10.6667 72.1027 11.0588 71.2443 11.3726C70.4289 11.6863 69.5705 11.8039 68.6692 11.8039H63.519V0.196078ZM68.7121 9.68628C69.828 9.68628 70.7722 9.33333 71.5447 8.62745C72.3173 7.92157 72.7035 7.05882 72.7035 6C72.7035 4.94118 72.3173 4.07843 71.5447 3.41176C70.7722 2.70588 69.828 2.39216 68.7121 2.39216H66.1799V9.68628H68.7121ZM82.1027 0L88.8409 11.8824H85.9653L85.1499 10.3137H78.9696L78.1542 11.8824H75.4074L82.1027 0ZM83.9911 8.11765L82.0168 4.47059L80.0855 8.11765H83.9911ZM89.313 0.196078L93.1757 7.05882L96.8237 0.196078H99.5705L93.0898 12.0784L86.2658 0.196078H89.313Z"
                    fill="#1F2937"
                  />
                  <path
                    d="M29.8293 15.6868V15.177H27.4688V15.6868H28.3271V18.6672H28.928V15.6868H29.8293ZM30.6447 18.6672H31.2027V17.6084C31.2027 17.3339 31.2456 17.177 31.3314 17.0594C31.4172 16.9417 31.546 16.8633 31.7606 16.8633C31.8894 16.8633 32.0181 16.9025 32.061 16.9809C32.1469 17.0594 32.1469 17.177 32.1898 17.2947V18.6672H32.7477V17.3339C32.7477 17.177 32.7477 16.9025 32.576 16.7064L32.5331 16.6672C32.4473 16.5496 32.2327 16.4319 31.8464 16.4319C31.7177 16.4319 31.4602 16.4711 31.2027 16.6672V14.8633H30.6447V18.6672ZM35.5803 17.9613C35.5374 18.0397 35.4516 18.1182 35.3657 18.1966C35.237 18.275 35.1512 18.3143 34.9795 18.3143C34.8507 18.3143 34.6791 18.275 34.5503 18.1574C34.4215 18.0397 34.3357 17.8829 34.3357 17.726H36.0524V17.6476C36.0524 17.4123 36.0095 17.0201 35.7091 16.7064C35.5803 16.5888 35.3228 16.4319 34.9366 16.4319C34.5932 16.4319 34.3357 16.5496 34.1211 16.7456C33.8636 16.9809 33.7348 17.2947 33.7348 17.6476C33.7348 17.9613 33.8636 18.275 34.0782 18.4711C34.2928 18.6672 34.5503 18.7456 34.8936 18.7456C35.1512 18.7456 35.4087 18.7064 35.6233 18.5888C35.7949 18.5103 35.9237 18.3535 36.0095 18.1966L35.5803 17.9613ZM34.4215 17.2947C34.4645 17.177 34.5074 17.0986 34.5932 17.0201C34.679 16.9417 34.8078 16.8633 34.9795 16.8633C35.1512 16.8633 35.2799 16.9417 35.3657 16.9809C35.4516 17.0594 35.4945 17.177 35.5374 17.2947H34.4215ZM41.3314 15.2162H39.2284V18.7064H41.3314V18.1966H39.8293V17.0986H41.2885V16.5888H39.8293V15.6868H41.3314V15.2162ZM42.2327 16.4711L43.4773 18.8241L44.722 16.4711H44.0782L43.4773 17.726L42.8765 16.4711H42.2327ZM46.825 16.4319C46.0954 16.4319 45.5374 16.9025 45.5374 17.6084C45.5374 18.275 46.0954 18.7848 46.825 18.7848C47.5546 18.7848 48.1125 18.275 48.1125 17.6084C48.1125 16.9025 47.5117 16.4319 46.825 16.4319ZM46.825 18.275C46.3958 18.275 46.0954 18.0005 46.0954 17.5692C46.0954 17.0594 46.4387 16.8633 46.825 16.8633C47.1683 16.8633 47.5546 17.0594 47.5546 17.5692C47.5117 18.0005 47.2542 18.275 46.825 18.275ZM49.2284 14.8633V18.6672H49.7863V14.8633H49.2284ZM50.7735 16.4711L52.0181 18.8241L53.2627 16.4711H52.619L52.0181 17.726L51.4172 16.4711H50.7735ZM54.2069 16.4711V18.6672H54.7649V16.4711H54.2069ZM54.1211 15.5692C54.1211 15.7652 54.2928 15.8829 54.4645 15.8829C54.6791 15.8829 54.8078 15.726 54.8078 15.5692C54.8078 15.3731 54.6361 15.2554 54.4645 15.2554C54.2928 15.2554 54.1211 15.3731 54.1211 15.5692ZM56.0524 18.6672H56.6104V17.6476C56.6104 16.9809 56.825 16.9025 57.0825 16.9025H57.1683C57.34 16.9025 57.5546 16.9809 57.5546 17.4907V18.7064H58.1125V17.3731C58.1125 17.0201 58.0696 16.8633 57.9838 16.7456L57.9409 16.7064C57.855 16.5888 57.6404 16.4711 57.2542 16.4711H57.1683C57.0396 16.4711 56.7821 16.5103 56.6104 16.7456V16.4711H56.0524V18.6672ZM61.1597 16.7064C60.9451 16.4711 60.6876 16.3927 60.4301 16.3927C60.1297 16.3927 59.8722 16.4711 59.6147 16.7064C59.443 16.8633 59.2713 17.1378 59.2713 17.5692C59.2713 17.9221 59.4001 18.2358 59.6147 18.4319C59.8293 18.6672 60.0868 18.7456 60.4301 18.7456H60.516C60.6876 18.7456 60.9451 18.6672 61.1597 18.4319V18.7064C61.1597 18.8633 61.1597 19.0986 60.9881 19.2554C60.9022 19.3339 60.7735 19.4123 60.5589 19.4123C60.3443 19.4123 60.1726 19.3339 60.1297 19.2554C60.0439 19.177 59.958 19.0201 59.958 18.9025H59.4001C59.443 19.177 59.5718 19.4123 59.7434 19.5692C59.958 19.7652 60.2584 19.8437 60.516 19.8437C60.9022 19.8437 61.1597 19.726 61.3314 19.6084C61.6748 19.3339 61.7177 18.9809 61.7177 18.4711V16.4711H61.1597V16.7064ZM60.516 16.9025C60.6876 16.9025 60.8164 16.9417 60.9881 17.0594C61.1168 17.177 61.2027 17.3731 61.2027 17.6084C61.2027 17.7652 61.1597 17.9613 60.9881 18.1182C60.8593 18.2358 60.6876 18.3143 60.516 18.3143C60.3443 18.3143 60.1726 18.2358 60.0868 18.1574C59.958 18.0397 59.8293 17.8045 59.8293 17.6084C59.8293 17.3731 59.9151 17.177 60.0868 17.0594C60.2155 16.9417 60.3443 16.9025 60.516 16.9025ZM67.6404 18.6672H68.2842L66.4816 14.9809L64.5932 18.6672H65.237L65.6662 17.8437H67.2971L67.6404 18.6672ZM65.8378 17.3339L66.4387 16.1574L66.9967 17.3339H65.8378ZM70.9881 16.7456C70.7735 16.4711 70.4301 16.4319 70.2584 16.4319C69.6147 16.4319 69.0997 16.8633 69.0997 17.5692C69.0997 18.1574 69.5288 18.7456 70.2584 18.7456C70.4301 18.7456 70.7305 18.7064 70.9881 18.4319V18.6672H71.546V14.8633H70.9881V16.7456ZM70.3443 16.9025C70.6876 16.9025 71.031 17.1378 71.031 17.6084C71.031 18.079 70.6876 18.3143 70.3443 18.3143C69.958 18.3143 69.6576 18.0005 69.6576 17.6084C69.6576 17.2162 69.9151 16.9025 70.3443 16.9025ZM75.4087 18.6672V16.2358L78.1554 18.9025V15.2162H77.5546V17.6476L74.8078 14.9809V18.7064L75.4087 18.6672ZM81.2456 17.9613C81.2027 18.0397 81.1168 18.1182 81.031 18.1966C80.9022 18.275 80.8164 18.3143 80.6447 18.3143C80.516 18.3143 80.3443 18.275 80.2155 18.1574C80.0868 18.0397 80.0009 17.8829 80.0009 17.726H81.7177V17.6476C81.7177 17.4123 81.6748 17.0201 81.3743 16.7064C81.2456 16.5888 80.9881 16.4319 80.6018 16.4319C80.2585 16.4319 80.0009 16.5496 79.7863 16.7456C79.5288 16.9809 79.4001 17.2947 79.4001 17.6476C79.4001 17.9613 79.5288 18.275 79.7434 18.4711C79.958 18.6672 80.2155 18.7456 80.5589 18.7456C80.8164 18.7456 81.0739 18.7064 81.2885 18.5888C81.4602 18.5103 81.5889 18.3535 81.6748 18.1966L81.2456 17.9613ZM80.0439 17.2947C80.0868 17.177 80.1297 17.0986 80.2155 17.0201C80.3014 16.9417 80.4301 16.8633 80.6018 16.8633C80.7735 16.8633 80.9022 16.9417 80.9881 16.9809C81.0739 17.0594 81.1168 17.177 81.1597 17.2947H80.0439ZM83.9065 16.9417V16.4711H83.4773V15.6868H82.9194V16.4711H82.7048V16.9417H82.9194V18.6672H83.4773V16.9417H83.9065ZM84.6361 16.4711L85.8808 18.8241L86.5675 17.4123L87.2542 18.8241L88.4988 16.4711H87.855L87.2112 17.726L86.5245 16.275L85.8378 17.726L85.1941 16.4711H84.6361ZM90.5589 16.4319C89.8293 16.4319 89.2713 16.9025 89.2713 17.6084C89.2713 18.275 89.8293 18.7848 90.5589 18.7848C91.2885 18.7848 91.8464 18.275 91.8464 17.6084C91.8464 16.9025 91.2885 16.4319 90.5589 16.4319ZM90.5589 18.275C90.1297 18.275 89.8293 18.0005 89.8293 17.5692C89.8293 17.0594 90.1726 16.8633 90.5589 16.8633C90.9022 16.8633 91.2885 17.0594 91.2885 17.5692C91.2456 18.0005 90.9881 18.275 90.5589 18.275ZM92.9623 18.6672H93.5202V17.5299C93.5202 17.3731 93.5203 17.177 93.6919 17.0201C93.7778 16.9417 93.9065 16.9025 93.9924 16.9025H94.0353C94.0782 16.9025 94.2069 16.9025 94.3357 16.9809L94.5503 16.5103C94.3786 16.4319 94.2499 16.3927 94.1211 16.3927C93.9924 16.3927 93.9065 16.3927 93.7778 16.4711C93.6919 16.5103 93.6061 16.5888 93.5632 16.6672V16.4711H93.0052L92.9623 18.6672ZM95.4516 14.8633H96.0095V17.2162L96.7821 16.4711H97.5117L96.4816 17.3731L97.5975 18.6672H96.8679L96.0954 17.726L96.0095 17.8045V18.6672H95.4516V14.8633Z"
                    fill="#4B5563"
                  />
                  <mask
                    id="mask0_2049_3208"
                    style={{ maskType: "alpha" }}
                    maskUnits="userSpaceOnUse"
                    x={0}
                    y={0}
                    width={13}
                    height={19}
                  >
                    <path
                      d="M7.16738 0.195312L12.9185 9.29335L7.03863 18.509H0L5.87983 9.29335L0 0.195312H7.16738Z"
                      fill="white"
                    />
                  </mask>
                  <g mask="url(#mask0_2049_3208)">
                    <path
                      d="M7.16738 0.195312L12.9185 9.29335L7.03863 18.509H0L5.87983 9.29335L0 0.195312H7.16738Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M5.19287 8.23438L9.99973 15.4893C9.6993 19.254 9.48471 21.1363 9.31304 21.1363C9.14136 21.1363 5.92248 20.7834 -0.386533 20.0775C-1.20198 17.9207 -1.50241 16.8618 -1.37366 16.8618C-1.2449 16.901 0.943939 14.0383 5.19287 8.23438Z"
                      fill="#1F2937"
                    />
                  </g>
                  <mask
                    id="mask1_2049_3208"
                    style={{ maskType: "alpha" }}
                    maskUnits="userSpaceOnUse"
                    x={9}
                    y={0}
                    width={14}
                    height={19}
                  >
                    <path
                      d="M17.0384 0.195312L22.7895 9.29335L16.9097 18.5482H9.82812L15.708 9.33256L9.82812 0.195312H17.0384Z"
                      fill="white"
                    />
                  </mask>
                  <g mask="url(#mask1_2049_3208)">
                    <path
                      d="M17.0384 0.195312L22.7895 9.29335L16.9097 18.5482H9.82812L15.708 9.33256L9.82812 0.195312H17.0384Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M15.0649 8.35156L19.8718 15.6457C19.5714 19.4104 19.3568 21.2927 19.1851 21.2927C19.0134 21.2927 15.7945 20.9398 9.44261 20.2339C8.67008 18.0771 8.32673 17.0182 8.4984 17.0182C8.62716 17.0574 10.816 14.1555 15.0649 8.35156Z"
                      fill="#1F2937"
                    />
                  </g>
                </svg>
                <p className="border-r border-gray-400 h-[30px]" />
                <svg
                  width={100}
                  height={20}
                  viewBox="0 0 100 20"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M35.6824 19.7766C32.0744 19.7766 28.7252 18.5701 26.4896 16.3325C24.8006 14.642 23.989 12.3457 23.989 9.98235C23.989 7.64775 24.8356 5.33567 26.4894 3.65408C28.5656 1.54407 32.2312 0.222656 35.6824 0.222656C39.5016 0.222656 42.5584 1.2954 44.8952 3.65988C46.5578 5.34236 47.3616 7.64418 47.3616 9.98257C47.3616 12.2492 46.5086 14.6629 44.8952 16.3325C42.7192 18.5846 39.2996 19.7766 35.6824 19.7766V17.1976C37.5974 17.1976 39.3738 16.4603 40.6144 15.0838C41.8464 13.7166 42.4204 12.0362 42.4204 9.98235C42.4204 8.01484 41.8012 6.17535 40.6144 4.87067C39.3904 3.52629 37.5716 2.7698 35.6824 2.7698C33.7874 2.7698 31.9674 3.51848 30.7424 4.87067C29.562 6.17491 28.9412 8.01975 28.9412 9.98235C28.9412 11.9389 29.5692 13.7827 30.7424 15.084C31.9684 16.444 33.782 17.1978 35.6824 17.1978V19.7768V19.7766ZM9.31162 0.232023C7.38162 0.232023 5.18902 0.634579 3.32602 1.56235C1.60662 2.41787 0.199219 3.8015 0.199219 6.09529C0.198419 8.16115 1.37582 9.37104 1.34382 9.33759C1.84462 9.85166 2.65082 10.727 4.75862 11.2411C5.70062 11.4708 7.71462 11.8236 9.72022 12.0574C11.711 12.2915 13.6702 12.5141 14.4682 12.7394C15.1022 12.9193 16.1672 13.1644 16.1672 14.4968C16.1672 15.8238 15.0452 16.2288 14.8502 16.3166C14.6554 16.4025 13.3094 17.0912 10.8898 17.0912C9.10342 17.0912 6.95582 16.4922 6.17302 16.1799C5.27062 15.8218 4.32402 15.3481 3.44102 14.1453C3.22142 13.8471 2.87502 13.0271 2.87502 12.215H0.685219V19.0574H3.11922V18.1329C3.11922 18.0277 3.23722 17.5948 3.64582 17.8006C4.15422 18.0582 5.64662 18.7208 7.20702 19.0841C8.48642 19.3825 9.31142 19.5964 10.902 19.5964C13.4972 19.5964 14.8914 19.1249 15.8552 18.8181C16.7632 18.5281 17.8852 18.0076 18.7966 17.1971C19.2902 16.7589 20.3726 15.6355 20.3726 13.5964C20.3726 11.6392 19.4306 10.4244 19.0992 10.0548C18.6478 9.55125 18.0964 9.16096 17.5218 8.8601C17.0212 8.59738 16.2312 8.2818 15.5848 8.10539C14.3302 7.76194 11.4934 7.33819 10.1368 7.17985C8.71422 7.01414 6.24642 6.78621 5.26082 6.4461C4.96202 6.34284 4.35282 6.01924 4.35282 5.23063C4.35282 4.66973 4.63142 4.19424 5.18202 3.80997C6.05602 3.19934 7.82142 2.81975 9.66162 2.81975C11.8372 2.81083 13.6796 3.36549 14.8516 3.94981C15.2502 4.1483 15.7166 4.43332 16.087 4.77053C16.505 5.15056 17.0918 5.94029 17.304 7.0418H19.27V1.08575H17.0748V1.77802C17.0748 2.00148 16.8678 2.29186 16.4764 2.05189C15.494 1.47716 12.7164 0.237153 9.31122 0.232023H9.31162ZM57.4184 1.31435L68.1268 12.0908L68.0168 4.83521C68.006 3.8838 67.8488 3.48659 66.926 3.48659H64.9126V1.31614H74.0686V3.48659H72.1046C71.1634 3.48659 71.104 3.82224 71.0926 4.83521L71.2586 18.699H68.123L55.789 6.4238L55.7916 15.1355C55.8024 16.0825 55.8422 16.5285 56.7172 16.5285H58.9162V18.6981H49.9242V16.5287H52.0262C52.8114 16.5287 52.7802 15.694 52.7802 15.0862V4.91773C52.7802 4.26137 52.6976 3.48815 51.4648 3.48815H49.7592V1.31435H57.4184ZM84.5312 16.5245C84.6172 16.5245 84.9992 16.5122 85.0732 16.487C85.2846 16.4134 85.428 16.2453 85.4944 16.07C85.5224 15.9964 85.5364 15.6708 85.5364 15.6001L85.538 12.17C85.538 12.0875 85.5326 12.0518 85.407 11.868C85.269 11.6673 79.798 4.75358 79.5476 4.44916C79.2366 4.07113 78.6906 3.48682 77.861 3.48682H75.9584V1.31547H86.6958V3.48414H85.4014C85.102 3.48414 84.903 3.80083 85.1588 4.15276C85.1588 4.15276 88.7714 8.97161 88.8056 9.02201C88.8392 9.07331 88.868 9.08558 88.914 9.03874C88.9592 8.99079 92.6172 4.19692 92.646 4.15901C92.82 3.92662 92.702 3.48659 92.327 3.48659H90.9992V1.31547H99.7992V3.48659H97.8332C97.12 3.48659 96.8298 3.63379 96.2932 4.31021C96.0478 4.61977 90.5184 11.6577 90.368 11.8484C90.2892 11.9481 90.296 12.087 90.296 12.1695V15.5992C90.296 15.6688 90.31 15.9948 90.338 16.068C90.4046 16.2442 90.5488 16.4123 90.76 16.485C90.834 16.5104 91.2108 16.5229 91.2966 16.5229H93.3076V18.6938H82.6256V16.5227L84.5316 16.5245H84.5312Z"
                    fill="#1F2937"
                  />
                </svg>
              </div>
              <div className="flex justify-between mt-12 gap-x-8">
                <svg
                  width={101}
                  height={20}
                  viewBox="0 0 101 20"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M85.4336 7.91406V19.9748H87.9552V11.9448H97.1327V19.9748H99.6525V7.93498L85.4336 7.91406Z"
                    fill="#1F2937"
                  />
                  <path
                    d="M87.6753 4.01277H97.3713C98.718 3.60215 99.7195 1.77917 100.002 0.015625H85.0449C85.3245 1.77972 86.3407 3.60215 87.6753 4.01277Z"
                    fill="#1F2937"
                  />
                  <path
                    d="M77.7943 19.9844C79.0657 19.1576 79.7496 17.7277 80.0116 16.0544H68.7019L68.7091 0.0273438L66.1738 0.038346V19.9844H77.7943Z"
                    fill="#1F2937"
                  />
                  <path
                    d="M47.3223 3.95901H56.2769C57.6269 3.35741 58.7605 1.77992 59.0368 0.03125H44.8122V11.8184H56.4546V15.9548L47.3223 15.9658C45.8912 16.5778 44.6776 18.0519 44.0723 19.9987L44.8122 19.9778H58.9561V7.89944H47.3223V3.95901Z"
                    fill="#1F2937"
                  />
                  <path
                    d="M25.2177 3.99873H34.9105C36.259 3.58647 37.2613 1.76517 37.5422 0H22.5859C22.8651 1.76517 23.8821 3.58647 25.2177 3.99873Z"
                    fill="#1F2937"
                  />
                  <path
                    d="M25.2177 11.8799H34.9105C36.259 11.4721 37.2613 9.64909 37.5422 7.88281H22.5859C22.8651 9.64964 23.8821 11.4721 25.2177 11.8799Z"
                    fill="#1F2937"
                  />
                  <path
                    d="M25.2177 19.982H34.9105C36.259 19.5709 37.2613 17.7484 37.5422 15.9844H22.5859C22.8651 17.749 23.8821 19.5709 25.2177 19.982Z"
                    fill="#1F2937"
                  />
                  <path
                    d="M0 0.0463457C0.291381 1.78951 1.27533 3.57121 2.6253 4.0176H6.70536L6.91349 4.14364V19.9356H9.46128V4.14364L9.69274 4.0176H13.7764C15.1414 3.47819 16.1042 1.78951 16.3906 0.0463457V0.0078125H0V0.0463457Z"
                    fill="#1F2937"
                  />
                </svg>
                <p className="border-r border-gray-400" />
                <svg
                  width={101}
                  height={30}
                  viewBox="0 0 101 30"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <g clipPath="url(#clip0_2049_3237)">
                    <path
                      d="M96.8861 18.3353L99.6602 20.0261C98.7598 21.2387 96.6063 23.3189 92.8831 23.3189C88.2597 23.3189 84.8164 20.0484 84.8164 15.8879C84.8164 11.4605 88.2962 8.45703 92.4938 8.45703C96.7158 8.45703 98.7841 11.5273 99.4533 13.1848L99.8183 14.0302L88.941 18.1461C89.7684 19.6368 91.0581 20.3932 92.8831 20.3932C94.7082 20.3932 95.9736 19.57 96.8861 18.3353ZM88.357 15.6543L95.6207 12.8956C95.2192 11.9723 94.0268 11.3159 92.6033 11.3159C90.7904 11.3159 88.2718 12.7843 88.357 15.6543Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M79.5723 0.882812H83.0764V22.6416H79.5723V0.882812Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M74.0488 9.03489H77.4312V22.2504C77.4312 27.7345 73.8906 29.9927 69.7051 29.9927C65.763 29.9927 63.3905 27.5677 62.5023 25.5987L65.6049 24.4196C66.1645 25.6321 67.5151 27.0671 69.7051 27.0671C72.3941 27.0671 74.0488 25.5431 74.0488 22.6953V21.6274H73.9271C73.1241 22.5173 71.591 23.3183 69.6443 23.3183C65.5805 23.3183 61.8574 20.0811 61.8574 15.9096C61.8574 11.7158 65.5805 8.44531 69.6443 8.44531C71.5789 8.44531 73.1241 9.23513 73.9271 10.1028H74.0488V9.03489ZM74.2921 15.9096C74.2921 13.2843 72.3819 11.371 69.9485 11.371C67.4908 11.371 65.4224 13.2843 65.4224 15.9096C65.4224 18.5015 67.4908 20.3815 69.9485 20.3815C72.3819 20.3926 74.2921 18.5015 74.2921 15.9096Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M42.6223 15.8561C42.6223 20.1389 38.9722 23.287 34.4948 23.287C30.0173 23.287 26.3672 20.1278 26.3672 15.8561C26.3672 11.5511 30.0173 8.41406 34.4948 8.41406C38.9722 8.41406 42.6223 11.5511 42.6223 15.8561ZM39.0695 15.8561C39.0695 13.1863 36.9525 11.3508 34.4948 11.3508C32.037 11.3508 29.92 13.1863 29.92 15.8561C29.92 18.5036 32.037 20.3614 34.4948 20.3614C36.9525 20.3614 39.0695 18.5036 39.0695 15.8561Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M60.3723 15.8879C60.3723 20.1707 56.7222 23.3189 52.2447 23.3189C47.7673 23.3189 44.1172 20.1707 44.1172 15.8879C44.1172 11.5829 47.7673 8.45703 52.2447 8.45703C56.7222 8.45703 60.3723 11.5718 60.3723 15.8879ZM56.8074 15.8879C56.8074 13.2182 54.6903 11.3827 52.2326 11.3827C49.7748 11.3827 47.6578 13.2182 47.6578 15.8879C47.6578 18.5355 49.7748 20.3932 52.2326 20.3932C54.7025 20.3932 56.8074 18.5244 56.8074 15.8879Z"
                      fill="#1F2937"
                    />
                    <path
                      d="M13.007 20.0592C7.90904 20.0592 3.91826 16.2992 3.91826 11.6382C3.91826 6.9772 7.90904 3.21725 13.007 3.21725C15.7568 3.21725 17.7643 4.2073 19.2487 5.47545L21.6943 3.2395C19.6259 1.42627 16.864 0.046875 13.007 0.046875C6.02315 0.046875 0.146484 5.25296 0.146484 11.6382C0.146484 18.0235 6.02315 23.2295 13.007 23.2295C16.7788 23.2295 19.6259 22.0949 21.8524 19.9813C24.1398 17.89 24.8455 14.9532 24.8455 12.5726C24.8455 11.8273 24.7482 11.0598 24.6387 10.4924H13.007V13.5849H21.2928C21.0494 15.5205 20.3802 16.8443 19.3947 17.7454C18.2023 18.8466 16.3164 20.0592 13.007 20.0592Z"
                      fill="#1F2937"
                    />
                  </g>
                  <defs>
                    <clipPath id="clip0_2049_3237">
                      <rect
                        width={100}
                        height={30}
                        fill="white"
                        transform="translate(0.00195312)"
                      />
                    </clipPath>
                  </defs>
                </svg>
                <p className="border-r border-gray-400" />
                <svg
                  width={101}
                  height={20}
                  viewBox="0 0 101 20"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M6.33695 19.6918H2.56885V9.98507H0.00195312V6.82477H2.56875V4.57599C2.56875 1.91118 3.70405 0 7.46195 0C8.25675 0 9.50455 0.165543 9.50455 0.165543V3.10005H8.19395C6.85855 3.10005 6.33715 3.5198 6.33715 4.68026V6.82477H9.45455L9.17695 9.98507H6.33705L6.33695 19.6918ZM14.983 6.57222C14.9281 6.57222 14.8716 6.57429 14.8157 6.57573C11.3217 6.57573 9.72305 9.29159 9.72305 13.1468C9.72305 18.0034 11.7967 19.9471 14.843 19.9471C16.5859 19.9471 17.731 19.189 18.427 17.7744V19.6931H22.011V6.82611H18.427V8.80488C17.8587 7.53179 16.6816 6.58731 14.983 6.57222ZM15.8943 9.61265C17.3618 9.61265 18.2426 10.6704 18.2426 12.4696L18.246 14.3072C18.246 15.5198 17.5185 16.9385 15.8943 16.9385C13.3973 16.9385 13.464 14.1524 13.464 13.2244C13.464 10.103 14.7944 9.61265 15.8943 9.61265ZM23.4584 13.2603C23.4584 11.6967 23.386 6.58059 29.8364 6.58059C32.4257 6.58059 33.5069 7.43135 33.5069 7.43135L32.6379 10.2165C32.6379 10.2165 31.5581 9.60211 30.1511 9.60211C28.349 9.60211 27.1991 10.6817 27.1991 12.5811L27.2011 13.943C27.2011 15.7681 28.3106 16.9864 30.1548 16.9864C31.4366 16.9864 32.618 16.3662 32.618 16.3662L33.4848 19.0932C33.4848 19.0932 32.4962 19.9494 29.8545 19.9494C23.7127 19.9494 23.4585 15.3592 23.4585 13.2603H23.4584ZM54.5212 6.57573C58.0153 6.57573 59.639 9.29159 59.639 13.1468C59.639 18.0034 57.5654 19.9471 54.5191 19.9471C52.7762 19.9471 51.4878 19.1891 50.7918 17.7744V19.6931L47.2529 19.6916V0.391227L51.0103 0.0525976V8.63055C51.5526 7.12981 53.3348 6.57573 54.5213 6.57573H54.5212ZM53.4678 9.61265C52.0003 9.61265 51.0103 10.6704 51.0103 12.4696L51.0068 14.3072C51.0046 15.5198 51.6924 16.9385 53.4678 16.9385C55.9648 16.9385 55.8981 14.1524 55.8981 13.2244C55.8981 10.103 54.5678 9.61265 53.4678 9.61265ZM40.0263 6.58638C36.0633 6.58638 33.9711 8.81914 33.9711 12.787V13.5242C33.9711 18.6741 36.9092 20 40.412 20C43.8167 20 45.3578 19.0159 45.3578 19.0159L44.6547 16.3954C44.6547 16.3954 42.8419 17.1924 40.8625 17.1924C38.8105 17.1924 37.928 16.6519 37.7018 14.6142H45.6582V12.5118C45.6582 8.2077 43.3101 6.58627 40.0262 6.58627L40.0263 6.58638ZM40.1218 9.21047C41.4936 9.21047 42.3825 10.0797 42.3337 12.0957H37.7087C37.7889 9.97391 38.7475 9.21057 40.1218 9.21057V9.21047ZM67.1312 6.56871C63.0615 6.56871 60.919 8.93859 60.919 13.1856C60.919 19.0126 64.6122 19.9506 67.138 19.9506C70.8356 19.9506 73.2956 17.8935 73.2956 13.2385C73.2956 8.3934 70.5296 6.56871 67.1312 6.56871ZM67.08 9.62319C68.8695 9.62319 69.5786 11.0072 69.5786 12.5825V13.9369C69.5786 15.8453 68.5863 16.9491 67.0732 16.9491C65.658 16.9491 64.6634 15.9166 64.6634 13.9369V12.5825C64.6634 10.4712 65.8469 9.62319 67.08 9.62319ZM80.781 6.56871C76.7113 6.56871 74.5688 8.93859 74.5688 13.1856C74.5688 19.0126 78.262 19.9506 80.7878 19.9506C84.4853 19.9506 86.9454 17.8935 86.9454 13.2385C86.9454 8.3934 84.1793 6.56871 80.781 6.56871ZM80.7298 9.62319C82.5193 9.62319 83.2283 11.0072 83.2283 12.5825V13.9369C83.2283 15.8453 82.2361 16.9491 80.723 16.9491C79.3078 16.9491 78.3132 15.9166 78.3132 13.9369V12.5825C78.3132 10.4712 79.4967 9.62319 80.7298 9.62319ZM88.3653 19.6918V0.391227L92.1336 0.0525976V12.989L95.8722 6.82477H99.8518L95.9518 13.2091L100.002 19.6918H96.0111L92.1336 13.3972V19.6918H88.3653Z"
                    fill="#1F2937"
                  />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>
      <Footer />
      </>
    );
}