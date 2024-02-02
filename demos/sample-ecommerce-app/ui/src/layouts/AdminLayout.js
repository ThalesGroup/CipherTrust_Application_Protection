import React from "react";
import { Outlet, Navigate } from "react-router-dom";
import Sidebar from "../pages/admin/Sidebar";
import MobileSidebar from "../pages/admin/MobileSidebar";
import TopNav from "../pages/admin/TopNav";


function AdminLayout({children}) {
    const CustomNavbarAdmin = ({ onSelect, activeKey, ...props }) => {
        //const navigate = useNavigate();
        return (
            <>
                <div className="w-full h-full bg-gray-200">
                    <div className="flex flex-no-wrap">
                        <Sidebar />
                        <MobileSidebar />
                        <div className="w-full">
                            <TopNav />
                            <div className="container mx-auto py-10 md:w-4/5 w-11/12 px-6">
                                <div className="w-full h-full rounded border-dashed border-2 border-gray-300">
                                    {children}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </>
        );
    };
    let authToken = true;
    return (
        authToken ? <><CustomNavbarAdmin /> <Outlet /></> : <Navigate to="/login"/>
    )    
}
export default AdminLayout;