import React from "react";
import Link from "next/link";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faLock, faLockOpen, faShield, faCheck, faRandom, faHashtag, faGears } from '@fortawesome/free-solid-svg-icons'

export default function Sidebar() {
    return (
        <div className="flex flex-col h-screen bg-[#192129] border-r-2 border-gray w-1/4 items-center">
            <div className="space-y-3 py-3 w-1/2">
                <div className="items-center">
                    <ul className="pt-2 pb-4 space-y-1 text-sm">
                        <li className="rounded-sm py-2 text-center">
                            <Link
                                href="/encrypt"
                                className="items-center text-center text-white p-2 space-x-3 rounded-md"
                            >
                                <span><FontAwesomeIcon icon={faLock} className="mr-2" />Encrypt</span>
                            </Link>
                        </li>
                        <li className="rounded-sm py-2 text-center">
                            <Link
                                href="/decrypt"
                                className="text-center items-center text-white p-2 space-x-3 rounded-md"
                            >
                                <span><FontAwesomeIcon icon={faLockOpen} className="mr-2" />Decrypt</span>
                            </Link>
                        </li>
                        <li className="rounded-sm py-2 text-center">
                            <Link
                                href="/signing"
                                className="text-center items-center text-white p-2 space-x-3 rounded-md"
                            >
                                <span><FontAwesomeIcon icon={faShield} className="mr-2" />Sign</span>
                            </Link>
                        </li>
                        <li className="rounded-sm py-2 text-center">
                            <Link
                                href="/verification"
                                className="text-center items-center text-white p-2 space-x-3 rounded-md"
                            >
                                <span><FontAwesomeIcon icon={faCheck} className="mr-2" />Verify</span>
                            </Link>
                        </li>
                        <li className="rounded-sm py-2 text-center">
                            <Link
                                href="/random"
                                className="text-center items-center text-white p-2 space-x-3 rounded-md"
                            >
                                <span><FontAwesomeIcon icon={faRandom} className="mr-2" />Random</span>
                            </Link>
                        </li>
                        <li className="rounded-sm border-b-2 border-gray-50 py-2 text-center">
                            <Link
                                href="/hashing"
                                className="text-center items-center text-white p-2 space-x-3 rounded-md"
                            >
                                <span><FontAwesomeIcon icon={faHashtag} className="mr-2" />Hash</span>
                            </Link>
                        </li>                            
                        <li className="rounded-sm py-4 text-center">
                            <Link
                                href="/sessions"
                                className="text-center items-center text-white p-2 space-x-3 rounded-md"
                            >
                                <span><FontAwesomeIcon icon={faGears} className="mr-2" />Sessions</span>
                            </Link>
                        </li>
                    </ul>
                </div>
            </div>
        </div>            
    );
}