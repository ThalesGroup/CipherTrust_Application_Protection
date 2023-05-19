using System;
using CADP.NetCore.Utility;

namespace CADP.NetCoreNaeSamples
{
    class PassPhraseSecureUtility
    {
        static string textToEncrypt = string.Empty;

        static void Main(string[] args)
        {
            var errorMessage = @"Usage :
Text: -txt <TextToBeObfuscated > --Obfuscates the provided text
File: -file <FileName> --Obfuscates first line of the file provided in file name";
            if (args.Length == 2)
            {
                var option = args[0];
                textToEncrypt = args[1];
                if (option == "-txt")
                {
                    TextEncryption();
                }
                else if (option == "-file")
                {
                    FileEncryption();
                }
                else
                {
                    Console.WriteLine(errorMessage);
                }
            }
            else
            {
                Console.WriteLine(errorMessage);
            }
        }

        private static void TextEncryption()
        {
            Console.WriteLine(PassPhraseSecure.PassPhraseEncryption(PassPhraseSecure.Options.Text, textToEncrypt));
        }

        private static void FileEncryption()
        {
            Console.WriteLine(PassPhraseSecure.PassPhraseEncryption(PassPhraseSecure.Options.File, textToEncrypt));
        }
    }
}