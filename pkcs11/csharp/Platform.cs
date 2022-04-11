using System;
using System.IO;


namespace Vormetric.Pkcs11Sample
{
    /// <summary>
    /// Class for runtime platform detection
    /// </summary>
    public static class Platform
    {
        /// <summary>
        /// True if runtime platform is Windows
        /// </summary>
        private static bool _isWindows = false;

        /// <summary>
        /// True if runtime platform is Windows
        /// </summary>
        public static bool IsWindows
        {
            get
            {
                DetectPlatform();
                return _isWindows;
            }
        }

        /// <summary>
        /// True if runtime platform is Linux
        /// </summary>
        private static bool _isLinux = false;

        /// <summary>
        /// True if runtime platform is Linux
        /// </summary>
        public static bool IsLinux
        {
            get
            {
                DetectPlatform();
                return _isLinux;
            }
        }

        /// <summary>
        /// Performs platform detection
        /// System.Runtime.InteropServices.RuntimeInformation is not used because:
        //  it does not perform platform detection in runtime but uses hardcoded information instead
        //   See https://github.com/dotnet/corefx/issues/3032 for more info
        /// </summary>
        private static void DetectPlatform()
        {
            // Supported platform has already been detected
            if (_isWindows || _isLinux)
                return;          

            string windir = Environment.GetEnvironmentVariable("windir");
            if (!string.IsNullOrEmpty(windir) && windir.Contains(@"\") && Directory.Exists(windir))
            {
                _isWindows = true;
            }
            else if (File.Exists(@"/proc/sys/kernel/ostype"))
            {
                string osType = File.ReadAllText(@"/proc/sys/kernel/ostype");
                if (osType.StartsWith("Linux", StringComparison.OrdinalIgnoreCase))
                {
                    _isLinux = true;
                }
                else
                {
                    throw new Exception($"Pkcs11Interop is not supported on {osType} platform.");
                }
            }
            else
            {
                throw new Exception("Pkcs11Interop is not supported on this platform.");
            }

        }
    }
}
