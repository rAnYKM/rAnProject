# rAnProject Development Notes - Database Design

## Minimal Database Design

- Node Table

|Column Name | Description|
|------------|------------|
|id|Node ID, identity|

- Attribute Table

- Relation Table

## Critical Thinking

- Our original model uses a relational database management system (MySQL) to store the social network. It might be better if we use a graph database management system (e.g. Neo4j).

- We can adopt the basic idea of the Social Attribute Network, which is to treat each attribute as a node in the social network. The attribute put in the attribute table should be formatted.
	- Pros: easier to build up a network
	- Cons: more entities in the table, efficiency?

- For our DEMO, the emphasis is laid on protection scheme. The database is just used for data storage and when we use the data, we put the whole network into the networkx data structure. However, it is not practical when the database is very large (Memory is limited). It is also one of the challenges. 

## Database Related Operations/Class

- **snapdb.py**: Generate a sample SNAP database 


- **randb.py** 

