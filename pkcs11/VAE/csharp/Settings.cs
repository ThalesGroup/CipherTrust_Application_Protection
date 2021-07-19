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
using System.IO;
using System.Reflection;
using Net.Pkcs11Interop.Common;
using Net.Pkcs11Interop.HighLevelAPI;
using Net.Pkcs11Interop.Logging;
using LLA40 = Net.Pkcs11Interop.LowLevelAPI40;
using LLA41 = Net.Pkcs11Interop.LowLevelAPI41;
using LLA80 = Net.Pkcs11Interop.LowLevelAPI80;
using LLA81 = Net.Pkcs11Interop.LowLevelAPI81;

namespace Vormetric.Pkcs11Sample
{
    /// <summary>
    /// Test settings.
    /// </summary>
    public static class Settings
    {
        #region Properties that almost always need to be configured before the tests are executed
        /// <summary>
        /// Factories to be used by Developer and Pkcs11Interop library
        /// </summary>
        public static Pkcs11InteropFactories Factories = new Pkcs11InteropFactories();
        /// <summary>
        /// Relative name or absolute path of unmanaged PKCS#11 library provided by smartcard or HSM vendor.
        /// </summary>
        
           
        public static string Pkcs11LibraryPath = @"/opt/vormetric/DataSecurityExpert/agent/pkcs11/lib/libvorpkcs11.so";
    
        //public static string Pkcs11LibraryPath = @"c:\Program Files\Vormetric\DataSecurityExpert\Agent\pkcs11\bin\vorpkcs11.dll";
        /// <summary>
        /// Type of application that will be using PKCS#11 library.
        /// When set to AppType.MultiThreaded unmanaged PKCS#11 library performs locking to ensure thread safety.
        /// </summary>
        public static AppType AppType = AppType.MultiThreaded;
        /// <summary>
        /// Serial number of token (smartcard) that should be used by these tests.
        /// First slot with token present is used when both TokenSerial and TokenLabel properties are null.
        /// </summary>
        public static string TokenSerial = null;
        /// <summary>
        /// Label of the token (smartcard) that should be used by these tests.
        /// First slot with token present is used when both TokenSerial and TokenLabel properties are null.
        /// </summary>
        public static string TokenLabel = null;
        /// <summary>
        /// PIN of the SO user a.k.a. PUK.
        /// </summary>
        public static string SecurityOfficerPin = @"11111111";
        /// <summary>
        /// PIN of the normal user.
        /// </summary>
        public static string NormalUserPin = @"11111111";
        /// <summary>
        /// Application name that is used as a label for all objects created by these tests.
        /// </summary>
        public static string ApplicationName = @"Pkcs11Interop";
        #endregion
        #region Properties that are set automatically in class constructor
        /// <summary>
        /// Arguments passed to the C_Initialize function in LowLevelAPI40 tests.
        /// </summary>
        public static LLA40.CK_C_INITIALIZE_ARGS InitArgs40 = null;
        /// <summary>
        /// Arguments passed to the C_Initialize function in LowLevelAPI41 tests.
        /// </summary>
        public static LLA41.CK_C_INITIALIZE_ARGS InitArgs41 = null;
        /// <summary>
        /// Arguments passed to the C_Initialize function in LowLevelAPI80 tests.
        /// </summary>
        public static LLA80.CK_C_INITIALIZE_ARGS InitArgs80 = null;
        /// <summary>
        /// Arguments passed to the C_Initialize function in LowLevelAPI81 tests.
        /// </summary>
        public static LLA81.CK_C_INITIALIZE_ARGS InitArgs81 = null;
        /// <summary>
        /// PIN of the SO user a.k.a. PUK.
        /// </summary>
        public static byte[] SecurityOfficerPinArray = null;
        /// <summary>
        /// PIN of the normal user.
        /// </summary>
        public static byte[] NormalUserPinArray = null;
        /// <summary>
        /// Application name that is used as a label for all objects created by these tests.
        /// </summary>
        public static byte[] ApplicationNameArray = null;
        /// <summary>
        /// PKCS#11 URI that identifies private key usable in signature creation tests.
        /// </summary>
        public static string PrivateKeyUri = null;
        #endregion
        /// <summary>
        /// Static class constructor
        /// </summary>
        static Settings()
        {
            // Uncomment following three lines to enable managed logging via System.Diagnostics.Trace class
            SimplePkcs11InteropLoggerFactory simpleLoggerFactory = new SimplePkcs11InteropLoggerFactory();
            simpleLoggerFactory.EnableFileOutput("log.txt");//.EnableDiagnosticsTraceOutput();
            simpleLoggerFactory.MinLogLevel = Pkcs11InteropLogLevel.Debug;
            Pkcs11InteropLoggerFactory.SetLoggerFactory(simpleLoggerFactory);
            // Uncomment following three lines to enable unmanaged logging via PKCS11-LOGGER library
            // System.Environment.SetEnvironmentVariable("PKCS11_LOGGER_LIBRARY_PATH", Pkcs11LibraryPath);
            // System.Environment.SetEnvironmentVariable("PKCS11_LOGGER_LOG_FILE_PATH", @"c:\pkcs11-logger.txt");
            // Pkcs11LibraryPath = @"c:\pkcs11-logger-x86.dll";
            // Setup arguments passed to the C_Initialize function
            if (AppType == AppType.MultiThreaded)
            {
                InitArgs40 = new LLA40.CK_C_INITIALIZE_ARGS();
                InitArgs40.Flags = CKF.CKF_OS_LOCKING_OK;
                InitArgs41 = new LLA41.CK_C_INITIALIZE_ARGS();
                InitArgs41.Flags = CKF.CKF_OS_LOCKING_OK;
                InitArgs80 = new LLA80.CK_C_INITIALIZE_ARGS();
                InitArgs80.Flags = CKF.CKF_OS_LOCKING_OK;
                InitArgs81 = new LLA81.CK_C_INITIALIZE_ARGS();
                InitArgs81.Flags = CKF.CKF_OS_LOCKING_OK;
            }
            // Convert strings to byte arrays
            SecurityOfficerPinArray = ConvertUtils.Utf8StringToBytes(SecurityOfficerPin);
            NormalUserPinArray = ConvertUtils.Utf8StringToBytes(NormalUserPin);
            ApplicationNameArray = ConvertUtils.Utf8StringToBytes(ApplicationName);
            // Build PKCS#11 URI that identifies private key usable in signature creation tests
            Pkcs11UriBuilder pkcs11UriBuilder = new Pkcs11UriBuilder();
            pkcs11UriBuilder.ModulePath = Pkcs11LibraryPath;
            pkcs11UriBuilder.Serial = TokenSerial;
            pkcs11UriBuilder.Token = TokenLabel;
            pkcs11UriBuilder.PinValue = NormalUserPin;
            pkcs11UriBuilder.Type = CKO.CKO_PRIVATE_KEY;
            pkcs11UriBuilder.Object = ApplicationName;

            PrivateKeyUri = pkcs11UriBuilder.ToString();
        }
        

    }
}

