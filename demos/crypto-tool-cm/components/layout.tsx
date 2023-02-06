// import custom components
import Head from "next/head";
import React from "react";
import Header from "./header";
import Sidebar from './sidebar';

type Layout = React.PropsWithChildren<{}>;
export interface props {
    children?: React.ReactNode; 
}

export default function Layout({children}: props) {
    // styles the main html tag
    const styles = {
        display: "flex",
        flexDirection: "row"
    };

    return (
    <>
        <Head>
            <title>CipherTrust Vault Crypto Tools</title>
            <meta name="description" content="" />
            <link rel="icon" href="/favicon.ico" />
        </Head>
        <Header />
        <div className="flex">
            <Sidebar />
            <div className="container mx-auto p-10">
                { children }
            </div>
        </div>
    </>
    );
}