import React from "react";

export default function Header() {
    const [navbarOpen, setNavbarOpen] = React.useState(false);
    return (
      <>
        <nav className="relative flex flex-wrap items-center justify-between px-2 bg-white border border-gray shadow-md w-full">
          <div className="container px-4 mx-auto flex flex-wrap items-center justify-between">
            <div className="w-full py-3 relative flex justify-between lg:w-auto lg:static lg:block lg:justify-start">
              <a
                className="text-sm font-bold leading-relaxed inline-block mr-4 whitespace-nowrap uppercase text-black"
                href="#pablo"
              >
                <img className="h-4" src="logo_CM.png" />
              </a>
              <button
                className="text-black cursor-pointer text-xl leading-none px-3 border border-solid border-transparent rounded bg-transparent block lg:hidden outline-none focus:outline-none"
                type="button"
                onClick={() => setNavbarOpen(!navbarOpen)}
              >
                <i className="fas fa-bars"></i>
              </button>
            </div>
            <div
              className={
                "lg:flex flex-grow items-center" +
                (navbarOpen ? " flex" : " hidden")
              }
              id="example-navbar-danger"
            >
                {/*
              <ul className="flex flex-col lg:flex-row list-none lg:ml-auto">
                <li className="nav-item border-l-2 border-gray py-3">
                  <a
                    className="px-3 flex items-center text-s uppercase font-bold leading-snug text-black hover:opacity-75"
                    href="#pablo"
                  >
                    <i className="fab fa-facebook-square text-lg leading-lg text-black opacity-75"></i><span className="ml-2">A</span>
                  </a>
                </li>
                <li className="nav-item border-l-2 border-gray py-3">
                  <a
                    className="px-3 flex items-center text-s uppercase font-bold leading-snug text-black hover:opacity-75"
                    href="#pablo"
                  >
                    <i className="fab fa-twitter text-lg leading-lg text-black opacity-75"></i><span className="ml-2">B</span>
                  </a>
                </li>
              </ul>
            */}
            </div>
          </div>
        </nav>
      </>
    );
  }