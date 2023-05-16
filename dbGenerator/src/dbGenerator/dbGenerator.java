package dbGenerator;
import java.io.*;
import java.sql.*;
import java.util.ArrayList;


//import org.apache.commons.lang3.StringEscapeUtils;

// A small comment from Christian
public class dbGenerator {
	//static String dbPrefix = "BIM";
	static String dbPrefix = "PLM";
	//static String dbPrefix = "PLM";
	static int minYear = 2000;
	static int maxYear = 2018;
	
	static String rootDir = "/Users/nyfelix/dev/plmstudy/database/";
	static String source = rootDir + dbPrefix + "_zotero.sqlite";
	static String target = rootDir + dbPrefix + "_analysis.sqlite";
	static String normKeywordFile = rootDir + dbPrefix + "_normalized.csv";
	static String acronymsFile = rootDir + dbPrefix + "_acronyms.csv";
	static String sourcesFile = rootDir + dbPrefix + "_sources.csv";
	static String missingKeywordsFile = rootDir + dbPrefix + "_missingKeywords.txt";
	static String missingSourcesFile = rootDir + dbPrefix + "_missingSources.txt";
	static int currentIDKeywords = 50000;
	
	public static void main(String[] args) {
		Connection cSource = null;
		Connection cTarget = null;
	    try {
	    	Class.forName("org.sqlite.JDBC");
	    	cSource = DriverManager.getConnection("jdbc:sqlite:" + source);
	    	cTarget = DriverManager.getConnection("jdbc:sqlite:" + target);

		    System.out.println("Opened database successfully");
		    
		    // Clear Target (for debug)
		    createTargetDatabase(cTarget);
		    
		    // Read Blacklist (TODO: Read from file)
		    ArrayList<Integer> blacklist = new ArrayList<Integer>();
		    if (dbPrefix == "PLM") {
		    	blacklist.add(1129);
		    	blacklist.add(3065);
		    	blacklist.add(1113);
		    	blacklist.add(1215);
		    	blacklist.add(1299);
		    	blacklist.add(812);
		    	blacklist.add(980);
		    }
		    
		    // Read AcronymsTable
		    AcronymsMap acronyms = new AcronymsMap();
		    acronyms.readFromFile(acronymsFile);
		    
		    // Read TagNomalization File into ArrayMap
		    NormalizationMap normKeywords = new NormalizationMap(acronyms);
		    currentIDKeywords = normKeywords.readFromFile(normKeywordFile, currentIDKeywords);

		    // Read Translation of SourceNames
		    SourcesMap sources = new SourcesMap();
		    sources.readFromFile(sourcesFile);
		    
		    // Write Normalized Tags into Target
		    writeNormalizedKeywords(cTarget, normKeywords, acronyms);
		    
		    // Collect Logdata
		    ArrayList<String> missingKeywords = new ArrayList<String>();
		    ArrayList<String> missingSources = new ArrayList<String>();
		    
		    // Loop through Publications List and insert Publication and Normalized Keywords into Target DB
		    Statement stmtPublications = cSource.createStatement();
		    Statement stmtCreatePublicaiton = cTarget.createStatement();
		    Statement stmtCountry = cTarget.createStatement();

		    // Only Papers with itemTypeID = 4 OR itemTypeID = 33
		    /*
		    ResultSet rs = stmtPublications.executeQuery( "SELECT itemID, fieldName, value " +
		    "FROM items NATURAL JOIN itemTypes NATURAL JOIN itemData NATURAL JOIN fields NATURAL JOIN itemDataValues " +
		    "WHERE libraryID isNull AND (itemTypeID = 4 OR itemTypeID = 33) AND fieldName IN ('title', 'date', 'abstractNote', 'publicationTitle', " +
		    "'conferenceName') ORDER BY itemID;" );*/
		    
		    // Final query for PLM
		    //ResultSet rs = stmtPublications.executeQuery( "SELECT itemID, fieldName, value FROM items NATURAL JOIN itemTypes NATURAL JOIN itemData NATURAL JOIN fields NATURAL JOIN itemDataValues NATURAL JOIN collectionItems WHERE collectionID = 12 AND fieldName IN ('title', 'date', 'abstractNote', 'publicationTitle', 'conferenceName') ORDER BY itemID" );
		    
		    // Final query for I40
		    ResultSet rs = stmtPublications.executeQuery( "SELECT itemID, fieldName, value FROM items NATURAL JOIN itemTypes NATURAL JOIN itemData NATURAL JOIN fields NATURAL JOIN itemDataValues NATURAL JOIN collectionItems WHERE fieldName IN ('title', 'date', 'abstractNote', 'publicationTitle', 'conferenceName') ORDER BY itemID" );
				    
		    
			int rowcount = 0;
			int tagRelCount = 0;
			int prevID = 0;
			int itemID = 0;
			String attributes = "";
			String values = "";
			boolean timeFilter = false;
			boolean pubTypeFilter = true;
			
			while (rs.next()) {
				//Collect values for publication
				itemID = rs.getInt(1);

				if (prevID != itemID) {
					//Check for Blacklist
					if (blacklist.contains(itemID)) {
						System.out.println("Blacklist publication ignored: " + itemID);
						prevID = itemID;
						continue;
					}
					// Make sure all Publications contain an Abstract and pubYear is in the defined Scope
					if (prevID != 0) { //prevID != 0 && attributes.contains("pubAbstract") && timeFilter == false && pubTypeFilter == false) {
						// Write Publication into targetDB
						String sqlInsert = "INSERT OR REPLACE INTO publications (pubID, " + attributes + ") VALUES (" + prevID + "," + values + ");";						
						//System.out.println(sqlInsert);
						stmtCreatePublicaiton.addBatch(sqlInsert);						
						
						// Read tags for publication
						// Make sure keyWord Type (0 and 1) are imported, they might be the same with different ids
						ResultSet rsTags = cSource.createStatement().executeQuery( "SELECT tagID, name FROM itemTags NATURAL JOIN tags WHERE itemID = " + prevID );
						// Check that publication has keywords, if not publication must be removed in export
						int countryID = 0;						
						while (rsTags.next()) {							
							Integer origTagID = rsTags.getInt(1);
							String origName = rsTags.getString(2);
							if (origName.startsWith("COUNTRY_") || origName.startsWith("country_Estonia")) {								
								ResultSet rsCounty = stmtCountry.executeQuery("SELECT couID FROM countries WHERE couZoteroName LIKE '" + origName +"';" );
								if (rsCounty.next()) {
									countryID = rsCounty.getInt(1);
								} else {
									System.out.println("Country not Found: " + origName);
								}
								rsCounty.close();
							} else {							
								NormElement normTag = normKeywords.getNormElement(origName);
								
								if (normTag != null) {

									if (normTag.isGeneric()) {
										// find correct translation in list of acronyms
										normTag = normTag.getElementRefernce(String.valueOf(prevID));
										//System.out.println("# " + origName + " translated to " + normTag.key + " ID: " + normTag.id);
									}
									
									String sqlItemTags = "INSERT OR REPLACE INTO publicationTags (pubID, tagID) VALUES (" + prevID + "," + normTag.id + ");";	
									stmtCreatePublicaiton.addBatch(sqlItemTags);
									tagRelCount++;
								}
								else {
									// Write to normalization Log
									if (!missingKeywords.contains(origName)) {
										missingKeywords.add(origName);
									}
									System.out.println("No normalized tag found for: " + origTagID + " / " + origName);
								}
							}
						}
						rsTags.close();
						String sqlUpdatePublication = "UPDATE publications SET couID = '" + countryID + "' WHERE pubID = " + prevID + ";";						
						stmtCreatePublicaiton.addBatch(sqlUpdatePublication);							
						rowcount++;
					} else {
						/*System.out.print("Qualitycheck failed - ");
						if (!attributes.contains("pubAbstract")) {
							System.out.println("No Abstract for publication: " + itemID );
						} else if (timeFilter == true){
							System.out.println("Not in time scope:" + itemID );
						} else if (pubTypeFilter == true){
							System.out.println("Publication type not allowed: " + itemID );
						}*/
					}
					attributes = "";
					values = "";
					timeFilter = false;
					pubTypeFilter = true;
				} else {
					attributes += ", ";
					values += ", ";
				}
				String attribute = rs.getString(2);
				String val = rs.getString(3);
				String defaultVal = "'" + val.replace("'", "''") + "'";
				switch  (attribute) {
					case "date" :
						int year =  Integer.parseInt(val.substring(0, 4));
						values += val.substring(0, 4);
						attributes += "pubYear";
						if (year > maxYear || year < minYear) {
							timeFilter = true;
							System.out.print(year  + " : ");
						}
						break;
					case "abstractNote":
						values += defaultVal;
						attributes += "pubAbstract";
						break;
					case "title":
						values += defaultVal;
						attributes += "pubTitle";
						break;
					case "publicationTitle":
						values += "'journalArticle', " + defaultVal;
						attributes += "pubType, pubSource";
						pubTypeFilter = false;
						break;
					case "conferenceName":
						// Check of Source exits, if not write to logfile
						
						if (sources.containsKey(val)) {
							values += "'conferencePaper', '" + sources.get(val) + "'";
							attributes += "pubType, pubSource";
							pubTypeFilter = false;
						} else {
							// Wirte to Logfile
							if (!missingSources.contains(val)) {
								missingSources.add(val);
							}
							System.out.println("No Source for: " + val);
						}
						break;
				}
				
				prevID = itemID;
				System.out.flush();
				
			}
			rs.close();
			stmtCreatePublicaiton.executeBatch();
			stmtCreatePublicaiton.close();
			stmtPublications.close();
			stmtCountry.close();
		    PrintWriter keywordLog = new PrintWriter(missingKeywordsFile, "UTF-8");
		    System.out.println("Number of missing keywords :" + missingKeywords.size());
		    for (String keyword: missingKeywords) {
		    	keywordLog.write(keyword + "\n");
		    }
			keywordLog.close();
		    PrintWriter sourcesLog = new PrintWriter(missingSourcesFile, "UTF-8");
		    for (String source: missingSources) {
		    	sourcesLog.write(source + "\n");
		    }
		    sourcesLog.close();

			System.out.println("# Publications: "+ rowcount);
			System.out.println("# Relations: "+ tagRelCount);
			
	    } catch ( Exception e ) {
	    	System.err.println( e.getClass().getName() + ": " + e.getMessage() );
	    	e.printStackTrace();
	    	System.exit(0);
	    }
	}
	
	private static void writeNormalizedKeywords (Connection cTarget, NormalizationMap normKeywords, AcronymsMap acronyms) {
		try {
			int i = 0;
			Statement stmtCreateTag = cTarget.createStatement();
			for (NormElement keyword : normKeywords.values()) {
				if (!keyword.isGeneric()) {
					i++;
					if (i==61) {
						int h = 1;
					}
					String sqlInsert = "INSERT OR REPLACE INTO tags (tagID, tagName, tagShortName, tagType) VALUES (" + keyword.id + ",\"" + keyword.key + "\", '" + "NO SHORT NAME" + "', 1);";
					stmtCreateTag.addBatch(sqlInsert);
				}
			}
			stmtCreateTag.executeBatch();
			stmtCreateTag.close();
			System.out.println("# Inserted Keywords");
		} catch ( Exception e ) {
	    	System.err.println( e.getClass().getName() + ": " + e.getMessage() );
	    	System.exit(0);
	    }
	}
	
	private static void createTargetDatabase (Connection cTarget) {
		try {
			Statement stmtCreate = cTarget.createStatement();
			
			String dropPublicationTags = "DROP TABLE IF EXISTS publicationTags;";
			String dropExperimentTags = "DROP TABLE IF EXISTS experimentTags;";
			String dropExperimentLinks  = "DROP TABLE IF EXISTS experimentLinks;";
			String dropPublications= "DROP TABLE IF EXISTS publications;";
			String dropTags = "DROP TABLE IF EXISTS tags;";
			//String dropCountries = "DROP TABLE IF EXISTS countries;";
			String dropExperiments = "DROP TABLE IF EXISTS experiments;";
			
			//String createCountries = "CREATE TABLE countries (couID INTEGER NOT NULL, couName TEXT, couZoteroName TEXT, couLongitude REAL, couLatitude REAL, PRIMARY KEY(couID))";
			String createPublications = "CREATE TABLE publications (pubID INTEGER, pubTitle TEXT, pubYear INTEGER, pubType TEXT, pubSource TEXT, pubOrigin TEXT, pubAbstract TEXT, couID INTEGER, PRIMARY KEY(pubID), FOREIGN KEY (couID) REFERENCES countries(couID));";
			String createTags = "CREATE TABLE tags (tagID INTEGER, tagName TEXT NOT NULL, tagShortName TEXT, tagType INT NOT NULL, PRIMARY KEY(tagID));";
			String createExperiments = "CREATE TABLE experiments (expID INTEGER NOT NULL, expName TEXT, expType INTEGER, expObjectives TEXT, PRIMARY KEY(expID))";
			String createPublicationTags = "CREATE TABLE publicationTags (pubID INT, tagID INT, PRIMARY KEY (pubID, tagID), FOREIGN KEY (pubID) REFERENCES publicaitons(pubID), FOREIGN KEY (tagID) REFERENCES tags(tagID));";
			String createExperimentTags = "CREATE TABLE experimentTags (expID INTEGER NOT NULL, tagID INTEGER NOT NULL, tagWeight INTEGER, tagLevel INTEGER, PRIMARY KEY(expID, tagID), FOREIGN KEY (tagID) REFERENCES tags(tagID), FOREIGN KEY (expID) REFERENCES experiments(expID));";
			String createExperimentLinks = "CREATE TABLE experimentLinks (parentTagID INTEGER NOT NULL, childTagID INTEGER NOT NULL, expID INTEGER NOT NULL, linkWeight INTEGER, PRIMARY KEY(parentTagID, childTagID, expID), FOREIGN KEY (parentTagID) REFERENCES tags(tagID), FOREIGN KEY (childTagID) REFERENCES tags(tagID), FOREIGN KEY (expID) REFERENCES experiments(expID));";
			
			stmtCreate.execute(dropPublicationTags);
			stmtCreate.execute(dropExperimentTags);
			stmtCreate.execute(dropExperimentLinks);
			stmtCreate.execute(dropPublications);
			stmtCreate.execute(dropTags);
			//stmtCreate.execute(dropCountries);
			stmtCreate.execute(dropExperiments);
			
			//stmtCreate.execute(createCountries);
			stmtCreate.execute(createPublications);
			stmtCreate.execute(createTags);
			stmtCreate.execute(createExperiments);
			stmtCreate.execute(createPublicationTags);
			stmtCreate.execute(createExperimentTags);
			stmtCreate.execute(createExperimentLinks);
			
			stmtCreate.close();
			System.out.println("# Database Cretated Successfully");
		} catch ( Exception e ) {
	    	System.err.println( e.getClass().getName() + ": " + e.getMessage() );
	    	System.exit(0);
	    }
	}

}
