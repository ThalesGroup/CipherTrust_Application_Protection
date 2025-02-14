using CryptoHeaderModule;
using System;
using System.Text;


namespace CADP.NetCoreNaeSamples
{
    class CryptoHeaderModuleSample
    {
        public static void Main()
        {
            // Array with operation descriptions
            string[] operations = new string[]
            {
            "1: Encryption and Decryption",
            "2: Legacy Encryption and Decryption",
            "3: HMAC Generation and Verification"
            };

            Console.WriteLine("Choose an operation:");
            foreach (var operation in operations)
            {
                Console.WriteLine(operation);
            }

            int choice = int.Parse(Console.ReadLine());

            Console.WriteLine("Enter Key name to be used for crypto operation (already generated)");
            string keyName = Console.ReadLine();

            CryptoFactory cryptoFactory = new CryptoFactory();

            //There is an alternative form of initialization to use in the event that there is an alternative properties file that the user wishes to use with the NaeSession.
            //CryptoFactory cryptoFactory = new CryptoFactory(<PathToPropertiesFile>);

            string plaintext = "this is the data to encrypt";
            string algo = "AES/CBC/PKCS7PADDING";
            IEncryptionHandler handler;

            switch (choice)
            {
                case 1: // Encryption and Decryption
                    handler = cryptoFactory.GetEncryptionHandler(algo, keyName);
                    byte[] toEncrypt = Encoding.UTF8.GetBytes(plaintext);
                    byte[] ciphertextWithHeaderInfo = handler.Encrypt(toEncrypt, keyName);
                    Console.WriteLine($"Ciphertext: {Encoding.UTF8.GetString(ciphertextWithHeaderInfo)}");

                    var decrypted = handler.Decrypt(ciphertextWithHeaderInfo);
                    Console.WriteLine($"Decrypted: {Encoding.UTF8.GetString(decrypted)}");
                    break;

                case 2: // Legay Encryption and Decryption
                    handler = cryptoFactory.GetEncryptionHandler(algo, keyName);
                    byte[] toLegayEncrypt = Encoding.UTF8.GetBytes(plaintext);
                    byte[] ciphertextWithoutHeaderInfo = handler.EncryptLegacyData(toLegayEncrypt);
                    Console.WriteLine($"Ciphertext: {Encoding.UTF8.GetString(ciphertextWithoutHeaderInfo)}");

                    var leagacyDecrypted = handler.DecryptLegacyData(ciphertextWithoutHeaderInfo);
                    Console.WriteLine($"Decrypted: {Encoding.UTF8.GetString(leagacyDecrypted)}");
                    break;

                case 3: //HMAC Generation & Verification
                    IHMACHandler _hmacHandler = cryptoFactory.GetHmacHandler();
                    byte[] toHMAC = Encoding.UTF8.GetBytes(plaintext);
                    byte[] hmac = _hmacHandler.GenerateHMAC(toHMAC, keyName);

                    Boolean verified = _hmacHandler.VerifyHMAC(toHMAC, hmac);
                    if (verified) Console.WriteLine("Hmac Verifiied");
                    break;
            }

        }
    }
}

