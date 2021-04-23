/*
 *  Pkcs11Interop - Open-source .NET wrapper for unmanaged PKCS#11 libraries
 *  Copyright (c) 2012-2013 JWC s.r.o.
 *  Author: Jaroslav Imrich
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU Affero General Public License version 3
 *  as published by the Free Software Foundation.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 *  GNU Affero General Public License for more details.
 *
 *  You should have received a copy of the GNU Affero General Public License
 *  along with this program. If not, see <http://www.gnu.org/licenses/>.
 * 
 *  You can be released from the requirements of the license by purchasing
 *  a commercial license. Buying such a license is mandatory as soon as you
 *  develop commercial activities involving the Pkcs11Interop software without
 *  disclosing the source code of your own applications.
 * 
 *  For more information, please contact JWC s.r.o. at info@pkcs11interop.net
 */

using System;
using Net.Pkcs11Interop.Common;

namespace Vormetric.Pkcs11Sample
{
    /// <summary>
    /// Test settings.
    /// </summary>
    public class Settings
    {
        /// <summary>
        /// The PKCS#11 unmanaged library path
        /// </summary>
        //public static string Pkcs11LibraryPath = @"vorpkcs11.dll";
        public static string Pkcs11LibraryPath = @"c:\Program Files\Vormetric\DataSecurityExpert\Agent\pkcs11\bin\vorpkcs11.dll";
        
        /// <summary>
        /// The SO pin (PUK).
        /// </summary>
        //public static string SecurityOfficerPin = @"Admin123!";

        /// <summary>
        /// The SO pin (PUK).
        /// </summary>
        //public static byte[] SecurityOfficerPinArray = ConvertUtils.Utf8StringToBytes(SecurityOfficerPin);

        /// <summary>
        /// The normal user pin.
        /// </summary>
        //public static string NormalUserPin = @"Admin123!";

        /// <summary>
        /// The normal user pin.
        /// </summary>
        //public static byte[] NormalUserPinArray = ConvertUtils.Utf8StringToBytes(NormalUserPin);

        /// <summary>
        /// The name of the application.
        /// </summary>
        public static string ApplicationName = @"VPkcs11_Test_Sample";

        /// <summary>
        /// The name of the application.
        /// </summary>
        public static byte[] ApplicationNameArray = ConvertUtils.Utf8StringToBytes(ApplicationName);
    }
}

