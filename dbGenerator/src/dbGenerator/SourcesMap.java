package dbGenerator;

import java.io.BufferedReader;
import java.io.FileReader;
import java.util.HashMap;

public class SourcesMap {
public HashMap<String, String> sources;
	
	public SourcesMap() {
		sources = new HashMap <String, String>();
	}
	
	public void readFromFile (String file) {
		int i = 0;
		try {
			// 
			BufferedReader csvFile =  new BufferedReader(new FileReader(file));
			String line = csvFile.readLine(); // Read first line and ignore it	
			
		    while ((line = csvFile.readLine()) != null) {
		    	String[] fields = line.split(";");
		    	String key = fields[0];
		    	sources.put(key, fields[1]);
	    		i++;
		    } 
		    csvFile.close();
		}  catch ( Exception e ) {
	    	System.err.println( e.getClass().getName() + ": " + e.getMessage() +" on textline " + i);
	    	System.exit(0);
	    }
	}
	
	public String get(String orig) {
		String res = sources.get(orig);
		if (res.isEmpty()) {
			res = orig;
		}
		return res;
	}

	public Boolean containsKey(String key) {
		return sources.containsKey(key);
	}

}
