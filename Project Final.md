# Wrangle OpenStreetMap Data Project

## Map Area

### Portland, OR

>https://www.openstreetmap.org/relation/186579

I chose Portland as the OSM Extract as it is close to home, which might make it easier to understand.

## Wrangling the map data and sampling

First I will use the 'Sample-code.py' script given for beginning the project in order to create a sample of the OSM Data.
I will use this sample to acquire a smaller extract of the data that I can check for problems and fix a few of them programmatically. Using the data.py code from the exercises for the course, I will check street names, tags, and audit the data for small needed changes.

The nodes and ways in the osm xml file will then be parsed out to csv files, which I will then import to SQLite in order to query within the database and analyze the data.

I will not be using the full XML extract as it is 1.5gb and creates a 2.5gb database. 

### Initial issues

On beginning the Audit, the main issues I found were the street names having inconsistencies in their form and abbreviations, states being mislabeled, and postal codes being inconsistent in their form. 
I decided to change the street names and states, as the postal codes would need to be adjusted based on if the street names and states are correct.

### Street names and States

I updated the street names and states to better reflect the mapping and to for sure be Oregon and not Washington, as a few errors output.\
By using the mapping:
>"St": "Street",\
 "ST": "Street",\
 "St.": "Street",\
 "St,": "Street",\
 "Street.": "Street",\
 "street": "Street",\
 "Sq": "Square",\
 "Rd.": "Road",\
 "Rd": "Road",\
 "Ave": "Avenue",\
 "DR.": "Drive",\
 "Blvd": "Boulevard"
 
 The majority of street abbreviations were corrected.
 
 The states were updated similarly but just by using 'OR' is the correct form and changing those that didn't match.

The data was then parsed to CSV files and entered into a Microsoft Access Database to explore the data via SQL. 

## Data Overview

This section will explore the SQL queries used to find information from the database

### Size of the files

| File      | Size |
| ----------- | ----------- |
| Portland_oregonosm.xml      | 1.46 gb       |
| Sample.osm   |   10.2 mb      |
| Portland.accdb  |  14 mb  |
| nodes.csv  |  3.9 mb  |
| nodes_tags.csv  |  65 kb  |
| ways.csv   |  388 kb  |
| ways_tags.csv  |  1 mb  |
| ways_nodes.csv  |  1.1 mb  |


### The number of nodes

>SELECT COUNT(*) FROM nodes;

43852

### The number of ways

>SELECT COUNT(*) FROM ways;

5733

### Unique Users

It may be noticeable that the SQL is not regular sqlite SQL but the syntax necessary for Microsoft Access.

>SELECT COUNT(*)  
>FROM (SELECT DISTINCT uid FROM nodes UNION ALL SELECT DISTINCT uid FROM ways) e;

461

### Top 10 users

SELECT TOP 10 user, COUNT(\*) FROM  
(SELECT user FROM nodes UNION ALL SELECT user FROM ways)  
GROUP BY user  
ORDER BY COUNT(\*) DESC;  

| user	| Count  |
| ----------- | ----------- |
|  Peter Dobratz_pdxbuildings  |  13033  |
|  lyzidiamond_imports  |  12689  |
|  Mele Sax-Barnett  |  3843 |
| baradam  |  	3343  |
| Darrell_pdxbuildings  | 	2863  |
| cowdog  |  	2182  |
| Peter Dobratz  |  	2008  |
| Grant Humphries  |  	1937  | 
| justin_pdxbuildings  |  	776  |
| amillar-osm-import  |  	725  |

### Amenity with most entries

SELECT TOP 1 value, COUNT(\*)  
FROM nodes_tags  
WHERE key="amenity"  
GROUP BY value  
ORDER BY COUNT(\*) DESC;  

|  Value  |  Count  |
| -------- | ------- | 
|  bicycle_parking  |  13   |

Let's do a silly one. This is the Pacific Northwest, so lets see how many Starbucks there are in the entries.

### Number of Starbucks

SELECT count (*)  
FROM nodes_tags  
WHERE value ='STARBUCKS';  

1

That's a surprisingly low amount, but that's just because the sample file is small. The full OSM extract would likely show hundreds of Starbucks!

## Problems in the Data and Suggestions

Auditing the sample size of Portland map, a few problems came up that could be fixed and cleaned early on, before adding to the database. Abbreviated street names and incorrect state listings were the most common.
This was fixed programmatically above using a few functions.

Now that the data is in the database, it is clear there are a few other problems in the data, which interferes with making deeper query assertations. Across the three 'nodes' tables, there are a significant amount of missing 'id' entries, which shrinks the amount of outputs for joined queries considerably. This could bring the numbers/COUNT outputs into question, as some rows may get excepted when querying nodes JOIN nodes_tags queries.

One of the key problems with datasets this large, even for just a relatively small sample of a single city, is the amount of unique points being logged. A unique id for each node tag quickly scales into the billions. Rather than an overall unique id for each tag, it would be helpful to subset the id for tags to each user and type, reducing the overall numeric scale for each tag. Even would simply require more specificty in querying as the unique user would need to be a query element as well as the id's, to differentiate if any numbers duplicated (which they would).

### Additional exploration

Below is an extra query to explore some aspects of the map, like the starbucks exploration above.

Number of religious locations:

SELECT value, COUNT(\*)  
FROM nodes_tags WHERE key="religion"  
GROUP BY value  
ORDER BY COUNT(\*) DESC;  

|  Value  |  Count  |
| ------- | ---------- |
| christian  |  2 |


# Conclusion

It's apparent even from my sample that the Portland extract of data is positively massive, and it would have been much easier to parse through with a smaller city scale. 
The most distorting factor in the data appears to be the inclusion of quite a bit of Vancouver, WA data as well, with streets and places holding WA tags. 
The data is clearly bot-submitted on many users accounts, with tag designations by the highest contributors scaling into the billions range. It would be helpful to make these designations more specific for each element, which would allow for more clean parsing when identifying problems. 

Many of these problems and solutions are beyond my ability to tackle, but I think it makes sense to try to fix them from an engineering perspective, to have cleaner data going into the map initially. This way there is less cleaning necessary on the back end.

# References

Street names code confirmation:
https://github.com/belgarion42/c750/blob/master/Udacity%20OSM%20Project%20-%20Irvine%2C%20CA%20-%20Randy%20Crane.ipynb
https://github.com/wblakecannon/udacity-dand/blob/master/4-Data-Wrangling/L12-Case-Study-OpenStreetMap-Data/11-Quiz-Preparing-for-Database-SQL.py




```python

```
