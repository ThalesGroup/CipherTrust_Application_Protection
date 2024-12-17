/*
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package io.trino.plugin.thales;/*
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package io.trino.plugin.thales;

import com.google.common.cache.CacheBuilder;
import com.google.common.cache.CacheLoader;
import com.google.common.cache.LoadingCache;
import com.ingrian.security.nae.FPEParameterAndFormatSpec;
import com.ingrian.security.nae.FPEParameterAndFormatSpec.FPEParameterAndFormatBuilder;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESession;
import io.airlift.slice.Slice;
import io.airlift.slice.Slices;
import io.trino.spi.StandardErrorCode;
import io.trino.spi.TrinoException;
import io.trino.spi.function.Description;
import io.trino.spi.function.ScalarFunction;
import io.trino.spi.function.SqlNullable;
import io.trino.spi.function.SqlType;
import io.trino.spi.type.StandardTypes;

import javax.crypto.Cipher;

import java.nio.charset.StandardCharsets;
import java.security.Key;
import java.security.Security;
import java.security.spec.AlgorithmParameterSpec;
import java.util.concurrent.TimeUnit;

public final class ThalesCADPFunctions
{
    private ThalesCADPFunctions() {}

    private static final LoadingCache<CacheKey, Key> keyCache = CacheBuilder.newBuilder()
            .maximumSize(1000)
            .expireAfterAccess(10, TimeUnit.MINUTES)
            .build(CacheLoader.from(ThalesCADPFunctions::getKey));

    @ScalarFunction("cadp_encrypt_char")
    @Description("cadp_encrypt_char")
    // todo this is not correct function should generally return VARBINARY, as the result not not valid UTF8
    // if you want VARCHAR you should either base 64 the output or convert to hex.  I recommend VARBINARY, and
    // that lets users choose a different format
    @SqlType(StandardTypes.VARCHAR)
    public static Slice cadpEncryptChar(@SqlNullable @SqlType(StandardTypes.VARCHAR) Slice data)
    {
        try {
            Key key = keyCache.get(new CacheKey("testfaas", "apiuser", "Yourpwd123!"));
            String encdata = "";
            String tweakAlgo = null;
            String tweakData = null;

            String algorithm = "FPE/FF1/CARD62";
            AlgorithmParameterSpec param = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo).build();
            Cipher encryptCipher = Cipher.getInstance(algorithm, "IngrianProvider");
            encryptCipher.init(Cipher.ENCRYPT_MODE, key, param);
            byte[] encrypted = encryptCipher.doFinal(data.getBytes());
            encdata = new String(encrypted, StandardCharsets.UTF_8);
            return Slices.utf8Slice(encdata);
        }
        catch (Exception e) {
            throw new TrinoException(StandardErrorCode.INVALID_FUNCTION_ARGUMENT, "Error in encrypting data", e);
        }
    }

    private record CacheKey(String keyName, String userName, String password) {}

    private static Key getKey(CacheKey cacheKey)
    {
        // TODO I'd avoid setting system properties or using a Security provider plugin.  Instead, I would just call your caching
        // service directly.  This introduces complexity with the JVM that should just be avoided.
        System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename", "/config/CADP_for_JAVA.properties");
        Security.addProvider(new IngrianProvider());
        //Security.addProvider((new IngrianProvider(new CustomLogger())));
        //System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename", "CADP_for_JAVA.properties");
        //IngrianProvider builder = new Builder().addConfigFileInputStream(getClass().getClassLoader().getResourceAsStream("CADP_for_JAVA.properties")).build();
        NAESession session = NAESession.getSession(cacheKey.userName(), cacheKey.password().toCharArray());
        try {
            return NAEKey.getSecretKey(cacheKey.keyName(), session);
        }
        finally {
            //if (session != null) {
            //    session.closeSession();
            //}
        }
    }

    @ScalarFunction("cadp_decrypt_char")
    @Description("Returns FPE Decrypted data")
    @SqlType(StandardTypes.VARCHAR)
    public static Slice cadp_decrypt_char(@SqlNullable @SqlType(StandardTypes.VARCHAR) Slice inputstring)
    {
        String decdata = "";
        String tweakAlgo = null;
        String tweakData = null;
        NAESession session = null;
        try {
            String keyName = "testfaas";
            String userName = "apiuser";
            String password = "Yourpwd123!";
            //String userName =  System.getenv("CMUSER");
            //String password =  System.getenv("CMPWD");
            System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename", "/config/CADP_for_JAVA.properties");
            //System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename", "CADP_for_JAVA.properties");
            //IngrianProvider builder = new Builder().addConfigFileInputStream(getClass().getClassLoader().getResourceAsStream("CADP_for_JAVA.properties")).build();
            session = NAESession.getSession(userName, password.toCharArray());
            NAEKey key = NAEKey.getSecretKey(keyName, session);
            String algorithm = "FPE/FF1/CARD62";
            FPEParameterAndFormatSpec param = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo).build();
            Cipher decryptCipher = Cipher.getInstance(algorithm, "IngrianProvider");
            // initialize cipher to decrypt.
            decryptCipher.init(Cipher.DECRYPT_MODE, key, param);
            // decrypt data
            byte[] outbuf = decryptCipher.doFinal(inputstring.getBytes());
            decdata = new String(outbuf, StandardCharsets.UTF_8);
        }
        catch (Exception e) {
            //     return "check exception";
        }
        finally {
            if (session != null) {
                session.closeSession();
            }
        }

        return (Slices.utf8Slice(decdata));
    }

    @ScalarFunction("cadp_encrypt_int")
    @Description("Returns FPE Encrypted data")
    @SqlType(StandardTypes.BIGINT)
    public static String cadp_encrypt_int(@SqlNullable @SqlType(StandardTypes.BIGINT) Slice inputstring)
    {
        String encdata = "";
        String tweakAlgo = null;
        String tweakData = null;

        NAESession session = null;
        try {
            String keyName = "testfaas";
            String userName = "apiuser";
            String password = "Yourpwd123!";
            //String userName =  System.getenv("CMUSER");
            //String password =  System.getenv("CMPWD");
            System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename", "/config/CADP_for_JAVA.properties");
            //System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename", "CADP_for_JAVA.properties");
            //IngrianProvider builder = new Builder().addConfigFileInputStream(getClass().getClassLoader().getResourceAsStream("CADP_for_JAVA.properties")).build();
            session = NAESession.getSession(userName, password.toCharArray());
            NAEKey key = NAEKey.getSecretKey(keyName, session);
            String algorithm = "FPE/FF1/CARD10";
            FPEParameterAndFormatSpec param = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo).build();
            Cipher encryptCipher = Cipher.getInstance(algorithm, "IngrianProvider");
            // initialize cipher to encrypt.
            encryptCipher.init(Cipher.ENCRYPT_MODE, key, param);
            // encrypt data
            byte[] outbuf = encryptCipher.doFinal(inputstring.getBytes());
            encdata = new String(outbuf, StandardCharsets.UTF_8);
        }
        catch (Exception e) {
            //     return "check exception";
        }
        finally {
            if (session != null) {
                session.closeSession();
            }
        }

        return (encdata);
    }

    @ScalarFunction("cadp_decrypt_int")
    @Description("Returns FPE Decrypted data")
    @SqlType(StandardTypes.BIGINT)
    public static String cadp_decrypt_int(@SqlNullable @SqlType(StandardTypes.BIGINT) Slice inputstring)
    {
        String decdata = "";
        String tweakAlgo = null;
        String tweakData = null;
        NAESession session = null;
        try {
            String keyName = "testfaas";
            String userName = "apiuser";
            String password = "Yourpwd123!";
            //String userName =  System.getenv("CMUSER");
            //String password =  System.getenv("CMPWD");
            System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename", "/config/CADP_for_JAVA.properties");
            //System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename", "CADP_for_JAVA.properties");
            //IngrianProvider builder = new Builder().addConfigFileInputStream(getClass().getClassLoader().getResourceAsStream("CADP_for_JAVA.properties")).build();
            session = NAESession.getSession(userName, password.toCharArray());
            NAEKey key = NAEKey.getSecretKey(keyName, session);
            String algorithm = "FPE/FF1/CARD10";
            FPEParameterAndFormatSpec param = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo).build();
            Cipher decryptCipher = Cipher.getInstance(algorithm, "IngrianProvider");
            // initialize cipher to decrypt.
            decryptCipher.init(Cipher.DECRYPT_MODE, key, param);
            // decrypt data
            byte[] outbuf = decryptCipher.doFinal(inputstring.getBytes());
            decdata = new String(outbuf, StandardCharsets.UTF_8);
        }
        catch (Exception e) {
            //     return "check exception";
        }
        finally {
            if (session != null) {
                session.closeSession();
            }
        }

        return (decdata);
    }
}


import com.ingrian.security.nae.FPEParameterAndFormatSpec;
import com.ingrian.security.nae.FPEParameterAndFormatSpec.FPEParameterAndFormatBuilder;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESession;
import io.airlift.slice.Slice;
import io.trino.spi.function.Description;
import io.trino.spi.function.ScalarFunction;
import io.trino.spi.function.SqlNullable;
import io.trino.spi.function.SqlType;
import io.trino.spi.type.StandardTypes;

import javax.crypto.Cipher;

public final class ThalesCADPFunctions
{
    private ThalesCADPFunctions() {}

    @ScalarFunction("cadp_encrypt_char")
    @Description("Returns FPE Encrypted data")
    @SqlType(StandardTypes.VARCHAR)
    public static String cadp_encrypt_char(@SqlNullable @SqlType(StandardTypes.VARCHAR) Slice inputstring)
    {
        String encdata = "";
        String tweakAlgo = null;
        String tweakData = null;

        NAESession session = null;
        try {
            String keyName = "testfaas";
            String userName = "apiuser";
            String password = "Yourpwd123!";
            //String userName =  System.getenv("CMUSER");
            //String password =  System.getenv("CMPWD");
            System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename", "/config/CADP_for_JAVA.properties");
            //System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename", "CADP_for_JAVA.properties");
            //IngrianProvider builder = new Builder().addConfigFileInputStream(getClass().getClassLoader().getResourceAsStream("CADP_for_JAVA.properties")).build();
            session = NAESession.getSession(userName, password.toCharArray());
            NAEKey key = NAEKey.getSecretKey(keyName, session);
            String algorithm = "FPE/FF1/CARD62";
            FPEParameterAndFormatSpec param = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo).build();
            Cipher encryptCipher = Cipher.getInstance(algorithm, "IngrianProvider");
            // initialize cipher to encrypt.
            encryptCipher.init(Cipher.ENCRYPT_MODE, key, param);
            // encrypt data
            byte[] outbuf = encryptCipher.doFinal(inputstring.getBytes());
            encdata = new String(outbuf);
        }
        catch (Exception e) {
            //     return "check exception";
        }
        finally {
            if (session != null) {
                session.closeSession();
            }
        }
        return (encdata);
    }

    @ScalarFunction("cadp_decrypt_char")
    @Description("Returns FPE Decrypted data")
    @SqlType(StandardTypes.VARCHAR)
    public static String cadp_decrypt_char(@SqlNullable @SqlType(StandardTypes.VARCHAR) Slice inputstring)
    {
        String decdata = "";
        String tweakAlgo = null;
        String tweakData = null;
        NAESession session = null;
        try {
            String keyName = "testfaas";
            String userName = "apiuser";
            String password = "Yourpwd123!";
            //String userName =  System.getenv("CMUSER");
            //String password =  System.getenv("CMPWD");
            System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename", "/config/CADP_for_JAVA.properties");
            //System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename", "CADP_for_JAVA.properties");
            //IngrianProvider builder = new Builder().addConfigFileInputStream(getClass().getClassLoader().getResourceAsStream("CADP_for_JAVA.properties")).build();
            session = NAESession.getSession(userName, password.toCharArray());
            NAEKey key = NAEKey.getSecretKey(keyName, session);
            String algorithm = "FPE/FF1/CARD62";
            FPEParameterAndFormatSpec param = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo).build();
            Cipher decryptCipher = Cipher.getInstance(algorithm, "IngrianProvider");
            // initialize cipher to decrypt.
            decryptCipher.init(Cipher.DECRYPT_MODE, key, param);
            // decrypt data
            byte[] outbuf = decryptCipher.doFinal(inputstring.getBytes());
            decdata = new String(outbuf);
        }
        catch (Exception e) {
            //     return "check exception";
        }
        finally {
            if (session != null) {
                session.closeSession();
            }
        }

        return (decdata);
    }

    @ScalarFunction("cadp_encrypt_int")
    @Description("Returns FPE Encrypted data")
    @SqlType(StandardTypes.BIGINT)
    public static String cadp_encrypt_int(@SqlNullable @SqlType(StandardTypes.BIGINT) Slice inputstring)
    {
        String encdata = "";
        String tweakAlgo = null;
        String tweakData = null;

        NAESession session = null;
        try {
            String keyName = "testfaas";
            String userName = "apiuser";
            String password = "Yourpwd123!";
            //String userName =  System.getenv("CMUSER");
            //String password =  System.getenv("CMPWD");
            System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename", "/config/CADP_for_JAVA.properties");
            //System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename", "CADP_for_JAVA.properties");
            //IngrianProvider builder = new Builder().addConfigFileInputStream(getClass().getClassLoader().getResourceAsStream("CADP_for_JAVA.properties")).build();
            session = NAESession.getSession(userName, password.toCharArray());
            NAEKey key = NAEKey.getSecretKey(keyName, session);
            String algorithm = "FPE/FF1/CARD10";
            FPEParameterAndFormatSpec param = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo).build();
            Cipher encryptCipher = Cipher.getInstance(algorithm, "IngrianProvider");
            // initialize cipher to encrypt.
            encryptCipher.init(Cipher.ENCRYPT_MODE, key, param);
            // encrypt data
            byte[] outbuf = encryptCipher.doFinal(inputstring.getBytes());
            encdata = new String(outbuf);
        }
        catch (Exception e) {
            //     return "check exception";
        }
        finally {
            if (session != null) {
                session.closeSession();
            }
        }

        return (encdata);
    }

    @ScalarFunction("cadp_decrypt_int")
    @Description("Returns FPE Decrypted data")
    @SqlType(StandardTypes.BIGINT)
    public static String cadp_decrypt_int(@SqlNullable @SqlType(StandardTypes.BIGINT) Slice inputstring)
    {
        String decdata = "";
        String tweakAlgo = null;
        String tweakData = null;
        NAESession session = null;
        try {
            String keyName = "testfaas";
            String userName = "apiuser";
            String password = "Yourpwd123!";
            //String userName =  System.getenv("CMUSER");
            //String password =  System.getenv("CMPWD");
            System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename", "/config/CADP_for_JAVA.properties");
            //System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename", "CADP_for_JAVA.properties");
            //IngrianProvider builder = new Builder().addConfigFileInputStream(getClass().getClassLoader().getResourceAsStream("CADP_for_JAVA.properties")).build();
            session = NAESession.getSession(userName, password.toCharArray());
            NAEKey key = NAEKey.getSecretKey(keyName, session);
            String algorithm = "FPE/FF1/CARD10";
            FPEParameterAndFormatSpec param = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo).build();
            Cipher decryptCipher = Cipher.getInstance(algorithm, "IngrianProvider");
            // initialize cipher to decrypt.
            decryptCipher.init(Cipher.DECRYPT_MODE, key, param);
            // decrypt data
            byte[] outbuf = decryptCipher.doFinal(inputstring.getBytes());
            decdata = new String(outbuf);
        }
        catch (Exception e) {
            //     return "check exception";
        }
        finally {
            if (session != null) {
                session.closeSession();
            }
        }

        return (decdata);
    }
}
