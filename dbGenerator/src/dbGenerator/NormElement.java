package dbGenerator;

import java.util.ArrayList;
import java.util.HashMap;

public class NormElement {
	public ArrayList<Integer> sourceKeys;
	public ArrayList<String> sourceTagNames;
	public HashMap<String, NormElement> normElementRefs;
	public int id;
	public String key;
	public String value;
	private boolean generic;
	
	public NormElement(int id, String key, boolean generic) {
		sourceKeys = new ArrayList<Integer>();
		sourceTagNames = new ArrayList<String>();
		normElementRefs = new HashMap<String, NormElement>();
		this.id = id;
		this.key = key;
		this.generic = generic;
	}
	
	public NormElement getElementRefernce(String key) {
		NormElement res = null;
		if (this.generic) {
			res = normElementRefs.get(key);
			// Try to find default, if not a specific ref is found
			if (res == null) {
				res = normElementRefs.get("*");
			}
		}
		return res;
	}
	
	public boolean isGeneric() {
		return this.generic;
	}

}
