package dbGenerator;

import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.HashMap;

public class AcronymsMap  {
	public HashMap<String, String> acronyms;
	
	public AcronymsMap() {
		acronyms = new HashMap <String, String>();
	}
	
	public HashMap<String, String> getKeywordsForAcronym(String acronym) {
		HashMap<String, String> keywords = new HashMap<String, String>();
		for (String acro : acronyms.keySet()) {
			if (acro.startsWith(acronym)) {
				String key = acro.split(":")[1];
				keywords.put(key, acronyms.get(acro));				
			}
		}
		return keywords;
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
		    	if (fields.length > 3 && !fields[3].equals("")) {
		    		String[] refs = fields[3].split(",");
		    		for (String ref : refs) {
		    			acronyms.put(key + ":" + ref, fields[2]);
		    			i++;
		    		}
		    	} else {
		    		acronyms.put(key, fields[2]);
		    		i++;
		    	}
		    } 
		    csvFile.close();
		}  catch ( Exception e ) {
	    	System.err.println( e.getClass().getName() + ": " + e.getMessage() +" on textline " + i);
	    	System.exit(0);
	    }
	}
	
	/*public String getAcronymForPublicationID(int pubID, String origName) {
		if(acronyms.containsKey(origName + ":" + pubID)) {
			return acronyms.get(origName + ":" + pubID);
		} else if (acronyms.containsKey(origName + ":*")) {
			return acronyms.get(origName + ":*");
		} 		
		return "";
	}*/
}
