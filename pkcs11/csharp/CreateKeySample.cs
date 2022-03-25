﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Net.Pkcs11Interop.Common;
using Net.Pkcs11Interop.HighLevelAPI;
using Net.Pkcs11Interop.HighLevelAPI.Factories;
using Net.Pkcs11Interop.HighLevelAPI.MechanismParams;


namespace Vormetric.Pkcs11Sample
{
    class CreateKeySample : ISample
    {
        
        public bool Run(object[] inputParams)
        {
            
            using (IPkcs11Library pkcs11Library = Settings.Factories.Pkcs11LibraryFactory.LoadPkcs11Library(Settings.Factories, Settings.Pkcs11LibraryPath, Settings.AppType))
            {
                // Find first slot with token present
                ISlot slot = Helpers.GetUsableSlot(pkcs11Library);

                // Open RW session
                using (ISession session = slot.OpenSession(SessionType.ReadWrite))
                {
                    uint keySize = 32;
                    string pin = Convert.ToString(inputParams[0]);
                    string keyLabel = Convert.ToString(inputParams[1]);
                    uint genAction = 0; // 0, 1, 2, or 3.  versionCreate...0, versionRotate...1, versionMigrate...2, nonVersionCreate...3
                    bool preactive = false;
                    bool nodelete = false; // 1...do not delete   0...delete as usual
                    bool bAlwSen = false;
                    bool bNevExtr = false;

                    if (inputParams.Length >= 3) genAction = Convert.ToUInt32(inputParams[2]);
                    if (inputParams.Length >= 4) preactive = Convert.ToBoolean(inputParams[3]);
                    if (inputParams.Length >= 5) nodelete = Convert.ToBoolean(inputParams[4]);
                    if (inputParams.Length >= 6) bAlwSen = Convert.ToBoolean(inputParams[5]);
                    if (inputParams.Length >= 7) bNevExtr = Convert.ToBoolean(inputParams[6]);

                    Console.WriteLine("genAction specified as " + genAction);
                    // Login as normal user
                    session.Login(CKU.CKU_USER, pin);

                    if (nodelete == false)
                    {                       
                        Helpers.CleanupKey(session, keyLabel);
                    }
                    if (genAction == 2)
                    {
                        // migrate
                        if (!Helpers.MigrateKey(session, keyLabel, genAction))
                            throw new Exception(keyLabel + "was not found and no migration has been done");
                        Console.WriteLine(keyLabel + " key migrated!");
                    }
                    else
                    {  
                        // Generate symetric key
                        IObjectHandle generatedKey = Helpers.GenerateKey(session, keyLabel, keySize, genAction, preactive, bAlwSen, bNevExtr); // three of four genAction cases are handled in GenerateKey
                        if (null != generatedKey)
                        {
                            if (genAction == 1)
                                Console.WriteLine(keyLabel + " key rotated!");
                            else
                            {
                                Console.WriteLine(keyLabel + " key generated!");
                            }
                        }
                    }
                    session.Logout();
                }              
                return true;
            }
        }
    }
}
