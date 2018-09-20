package dbGenerator;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.text.Normalizer;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;

public class NormalizationMap {

	public HashMap<String, NormElement> normElements; // List of all normalized 
	public HashMap<String, String> sourceElements; // 
	public AcronymsMap acronyms;
	
	public NormalizationMap(AcronymsMap acronyms) {
		normElements = new HashMap <String, NormElement>();
		sourceElements = new  HashMap<String, String>();
		this.acronyms = acronyms;
	}
		
	public Collection<NormElement> values() {
		return normElements.values();
	}
	
	public int readFromFile (String file, int startID) {
		int i = startID;
		try {
			BufferedReader csvFile =  new BufferedReader(new InputStreamReader(
					new FileInputStream(file), "UTF8"));
			String line = csvFile.readLine(); // Read first line and ignore it
			NormElement el;
			String orgID, orgName, normName;
			String[] fields;
			int count = 0;
		    while ((line = csvFile.readLine()) != null) {
		    	count++;
		    	fields = line.split(";");
		    	if (fields.length != 2) {
		    		System.out.println("Error in normalization file: " + line + " in line " + count);
		    	}
		    	orgID = "0"; //fields[0];
		    	orgName = fields[0];
		    	normName = fields[1];
		    	sourceElements.put(orgID, orgName);
		    	
		    	// Treat special Case **** here
		    	if (normName.equals("****")) {
		    		el = new NormElement(i++, normName, true);
		    		el.sourceKeys.add(Integer.parseInt(orgID));
		    		el.sourceTagNames.add(orgName);
					// find correct translation in list of acronyms																			
		    		HashMap<String, String> alternatives = acronyms.getKeywordsForAcronym(orgName);
					for (String key : alternatives.keySet()) {
						String value = alternatives.get(key);
						NormElement refEl = normElements.get(value);
						if (refEl != null) {
							el.normElementRefs.put(key, refEl);
						} else {
							refEl = new NormElement(i++, value, false);
							normElements.put(refEl.key, refEl);
							el.normElementRefs.put(key, refEl);
						}
					}
					
					normElements.put(el.key + ":" + orgName, el);
				} else {
			    	el = normElements.get(normName);
			    	if (el != null) {
			    		el.sourceKeys.add(Integer.parseInt(orgID));
			    		el.sourceTagNames.add(orgName);
			    	} else {
			    		el = new NormElement(i++, normName, false);
			    		el.sourceKeys.add(Integer.parseInt(orgID));
			    		el.sourceTagNames.add(orgName);
			    		normElements.put(el.key, el);
			    	}
				}
		    } 
		    csvFile.close();		    
		}  catch ( Exception e ) {
	    	System.err.println( e.getClass().getName() + ": " + e.getMessage() );
	    	System.exit(0);	 	    	
	    }
		return i;
	}
	
	public NormElement getNormElement(int origID) {
		for (NormElement el : normElements.values()) {
			if (el.sourceKeys.contains(origID)) {
				return el;
			}
		}
		return null;
	}
	
	public NormElement getNormElement(String origKey) {
		for (NormElement el : normElements.values()) {
			
			if (el.sourceTagNames.contains((CharSequence)origKey)) {
				return el;
			}
		}
		return null;
	}
}
