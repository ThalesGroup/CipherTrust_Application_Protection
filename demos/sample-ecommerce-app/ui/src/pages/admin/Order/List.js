import React, {useEffect, useState} from 'react';
import AdminLayout from '../../../layouts/AdminLayout';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import jwt_decode from "jwt-decode";

export default function List() {
    const navigate = useNavigate();
    const [orders, setOrders] = useState("");
    useEffect(() => {
        let token = sessionStorage.getItem('token');
        let user = sessionStorage.getItem('user');

        if(user===null || user==="") {
            if(token === null || token==="") {
                navigate('/admin/login');
            } else {
                var decodedToken = jwt_decode(token);
                var dateNow = new Date();
                if(decodedToken.exp * 1000 > dateNow.getTime()) {
                    //do nothing
                } else {
                    sessionStorage.removeItem('token');
                    navigate('/admin/login');
                }
            }
        } else {
            navigate('/admin/login');
        }        

        axios
        .get('http://'+process.env.REACT_APP_BACKEND_IP_ADDRESS+':8081/proxy/order-mgmt/order/list')
        .then((res) => {
            console.log(res.data);
            setOrders(res.data.data);
        })
        .catch((err) => console.log(err));
      }, [navigate]);

    const rows = {};
    for (const order of orders) {
        if (order.orderId in rows) {
          rows[order.orderId].push(order);
        } else {
          rows[order.orderId] = [order];
        }
    }
    console.log(rows);

    return(
        <AdminLayout>
            <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                    <tr>
                        <th scope="col" className="px-6 py-3 text-xs font-bold text-left text-gray-500 uppercase ">Order ID</th>
                        <th scope="col" className="px-6 py-3 text-xs font-bold text-left text-gray-500 uppercase ">User Name</th>
                        <th scope="col" className="px-6 py-3 text-xs font-bold text-left text-gray-500 uppercase ">Credit Card</th>
                        <th scope="col" className="px-6 py-3 text-xs font-bold text-left text-gray-500 uppercase ">CVV</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                {Object.entries(rows).map((entry) => {
                    const row = entry[0];
                    const details = entry[1];
                    return(
                        <tr>
                            <td className="px-6 py-4 text-sm font-medium text-gray-800 whitespace-nowrap">{row}</td>
                            <td className="px-6 py-4 text-sm text-gray-800 whitespace-nowrap">{details[0].user.username}</td>
                            <td className="px-6 py-4 text-sm text-gray-800 whitespace-nowrap">{details[0].card.cardNumber}</td>
                            <td className="px-6 py-4 text-sm text-gray-800 whitespace-nowrap">{details[0].card.cvv}</td>
                        </tr>
                    )
                })}
                </tbody>
            </table>
        </AdminLayout>
    )
}