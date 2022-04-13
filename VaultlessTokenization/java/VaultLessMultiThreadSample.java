import com.safenet.vaultLessTokenization.AlgoSpec;
import com.safenet.vaultLessTokenization.TokenSpec;
import com.safenet.vaultLessTokenization.*;

//IMPORT THE TOKENSERVICEVAULTLESS
import com.safenet.vaultLessTokenization.TokenServiceVaultless;

/**
 * This sample shows how to use CADP Vaultless Tokenization in multithreaded
 * environment.
 */
public class VaultLessMultiThreadSample extends Thread {
	TokenServiceVaultless _ts = null;

	String _dataToEncrypt[] = null;

	TokenSpec _spec = null;

	public static void main(String[] args) throws Exception {

		if (args.length != 5) {
			System.err.println(
					"Usage: java VaultLessMultiThreadSample naeUser naePswd keyName numberofThreads batchSize");
			System.exit(-1);
		}

		String naeUser = args[0];
		char[] naePswd = args[1].toCharArray();
		String keyName = args[2];
		int numberofThreads = Integer.parseInt(args[3]);
		int batchSize = Integer.parseInt(args[4]); // batchsize for each thread

		VaultLessMultiThreadSample[] list = new VaultLessMultiThreadSample[numberofThreads];

		// creating array for PlainText Values
		String dataToEncrypt[][] = new String[numberofThreads][batchSize];

		int num = Integer.MIN_VALUE;

		// populating array with PlainText Values
		for (int i = 0; i < numberofThreads; i++) {
			for (int j = 0; j < batchSize; j++) {
				dataToEncrypt[i][j] = String.valueOf(num);
			}
		}

		try {
			// creating and initializing AlgoSpec
			AlgoSpec algospec = new AlgoSpec();
			algospec.setVersion(1);
			// algospec.setUnicode(algospec.UNICODE_HEBREW); //required when tokenizing
			// unicode values

			// START THE TOKEN SERVICE Vaultless by creating a new TokenServiceVaultless
			// object
			TokenServiceVaultless ts = new TokenServiceVaultless(naeUser, naePswd, keyName, algospec);

			// creating and initializing TokeSpec.
			TokenSpec spec = new TokenSpec();
			spec.setFormat(ts.LAST_FOUR_TOKEN);
			spec.setClearTextSensitive(true);
			// spec.setLuhnCheck(true);
			// spec.setNonIdempotentTokens(false);
			spec.setGroupID(1);

			for (int i = 0; i < numberofThreads; i++) {
				list[i] = new VaultLessMultiThreadSample(ts, dataToEncrypt[i], spec);
			}

			for (int i = 0; i < numberofThreads; i++) {
				list[i].start();
			}

			// wait for all threads to finish before closing sesson.
			for (int i = 0; i < numberofThreads; i++) {
				list[i].join();
			}

			// CLOSE THE CONNECTION
			ts.closeService();
		} catch (Exception e) {
			System.out.println("Got exception: " + e);
			e.printStackTrace();
		}
	}

	public VaultLessMultiThreadSample(TokenServiceVaultless ts, String dataToEncrypt[], TokenSpec spec) {
		_ts = ts;
		_dataToEncrypt = dataToEncrypt;
		_spec = spec;
	}

	public void run() {
		try {
			System.out.println("[" + Thread.currentThread().getName() + "] starting sample.");

			// tokenize
			String tokens[] = _ts.tokenize(_dataToEncrypt, _spec);
			System.out.println("[" + Thread.currentThread().getName() + "] Token Array Length : " + tokens.length);

			// detokenize
			String values[] = _ts.detokenize(tokens, _spec);
			System.out.println("[" + Thread.currentThread().getName() + "] deToken Array Length : " + values.length);

		} catch (Exception e) {
			System.err.println("Got exception: " + e);
			e.printStackTrace();
		}
	}
}
