class PromptTemplate:
    MAPPING_INFO_TEMPLATE = """
Extract text from the image using OCR (Pytesseract), adjusting for any flipped or skewed orientation if needed.
Generate a Pydantic Object based on the structure provided below. There are some notes:
    - The general information in MainInformation can be founded from top rows / first table. The tables follow contain information of entities.
    - If there are lines with HEADING "Tier 1" / "Tier 2": Table above HEADING "Tier 1" contains all entities: Main information, entities list. The first row of this table is the information of Main information.
    - EntityType (can be a code number or string, prefer to get the code): 
        + its not value from columns like "Benificial Owner" / "Intermediary" / "FlowThrough" / "US Branch" / "ForeignStatusType" / "Chapter 4 Status"
        + if we have a column with column name has "Entity Type" in it, get corresponding value from that column. 
        + if not have this column, get it from column that has "ch.3" / "chap 3" / "chapter 3" / "type of recipient" in its lower name.
      If have multiple values like string or code, please return the code. 
    - City, State, Country and ZipCode can be extracted from address. Please be careful not to misclassify between City / State / Country / ZipCode
    - EIN: if not have this column, get it from USTIN or TIN column
    - Chapter4Status (can be a code number or string, prefer to get the code): Column with lower name has "chap 4" / "chapter 4" / "fatca status" in it . please get the first one you see
    - ForeignTaxpayerId: if not have this column, get it from FTIN or ForeignTIN column
    - Name is the same with InvestorName
    - Number is the same with AccountNumber
    - FormType is the same with DocumentType / Type of Document
    - AllocationPercentage: have "allocation %" / "allocation percentage" / "allocation" in lower column name. If EntitiesList only have 1 entity, then its value would be 100.00%
    - TierOwnershipPercentage: we can get from column that has "ownership percentage" / "ownership %" in its lower name

If column's name has multiple components mentioned above, please get each value of each component (Example: if column's name is "Entity Type, Resident Country, Type of Document" -> it has 3 components: EntityType, Country, FormType). Based on the order in the column's name, you can know which value belongs to which component. 

class Entity(BaseModel):
    AccountNumber: Optional[str] = None
    Name: Optional[str] = None
    AddressLine1: Optional[str] = None
    AddressLine2: Optional[str] = None
    AddressLine3: Optional[str] = None
    City_Town: Optional[str] = None
    State: Optional[str] = None
    Country: Optional[str] = None
    ZipCode: Optional[str] = None
    FormType: Optional[str] = None
    EIN: Optional[str] = None
    GIIN: Optional[str] = None
    EntityType: Optional[str] = None
    Chapter4Status: Optional[str] = None
    ForeignTaxpayerId: Optional[str] = None
    AllocationPercentage: Optional[str] = None
    TierOwnershipPercentage:  Optional[str] = None

class MainInformation(BaseModel):
    Date: Optional[str] = None
    Name: Optional[str] = None
    AddressLine1: Optional[str] = None
    AddressLine2: Optional[str] = None
    AddressLine3: Optional[str] = None
    City_Town: Optional[str] = None
    State: Optional[str] = None
    Country: Optional[str] = None
    ZipCode: Optional[str] = None
    FormType: Optional[str] = None
    EIN: Optional[str] = None
    EntityType: Optional[str] = None
    Chapter4Status: Optional[str] = None
    GIIN: Optional[str] = None
    Number: Optional[str] = None
    EntityList: Optional[List[Entity]] = None
   
The output should follow the example format, containing only the structured Pydantic data. Avoid including Python class definitions, import statements, FieldInfo, or FieldInfoList.
Use only English/alphabetic characters for the output, and refer to any comments in the Pydantic Object for additional context. If a field's value is not present in the image, set that field as "None" without making inferences from other fields.
Please keep the response in the specified Pydantic Object format with all fields, not JSON format. Please response as much as possible, not show "# Additional entities would be listed here following the same pattern"
"""

    MULTI_TIER_CLASSIFICATION = '''
Extract text from the image using OCR (Pytesseract), adjusting for any flipped or skewed orientation if needed.
In the document, we can have multi-tier entities and the order is tier 1 > tier 2 > tier 3 > tier 4 ... There are some cases for multi-tier detection:
	- tier-by-location
        1. In the Name / InvestorName / Requester Name column, values with the same indentation level will have the same tier, otherwise they have different tier. If the values that have a deeper indentation from the left (like 1 tab / many tabs / center align) than the previous value -> their tier will be lower.
	    2. In the Name / InvestorName / Requester Name column, it consists of many smaller columns (mark it as 1st, 2nd, 3rd, 4th, ... column). The tier order is determined by which column (1st, 2nd, 3rd, 4th, ...) the Name value belongs to from left to right. The value in the 1st column is tier 1, from 2nd column is tier 2, from 3rd column is 3, from 4th column is 4, ...
        3. If there is a Tier 1 / Tier 2 / Tier 3 / ... column in the input: we can get the tier of the entity by look at which column its name belongs to. 
    
    - tier-not-by-location
        4. If there are lines with HEADING "Tier 1" / "Tier 2" / "Tier 3" / ...: Table above HEADING "Tier 1" contains all entities: Main information and list of entities. The first row of this table is the information of Main information. With the next rows in that table:
		    a. which row that has name appear in the table between HEADING "Tier 1" and HEADING "Tier 2" belongs to Tier1
		    b. which row that has name appear in the table between HEADING "Tier 2" and HEADING "Tier 3" belongs to Tier2
	        c. The table between HEADING "Tier 1" and HEADING "Tier 2" show the all Tier1 entities. The table between HEADING "Tier 2" and HEADING "Tier 3" show all Tier2 entities...
            We can check the same for the other tier

        Especially, for all 4 cases above, in case there are subset of consecutive entities that their allocation percentage sum up to 100 or 100%, their tier would be lower than the closest previous entity
        If one of 4 cases above is satisfied, please separate all entities by their tier. Entity with higher tier can have multiple child entities link with it.


Generate a Pydantic Object based on the structure provided below:

class EntityTier(BaseModel):
    Name: Optional[str] = None
    Tier: Optional[int] = None

class TierInformation(BaseModel):
    Name: Optional[str] = None
    EntityList: Optional[List[EntityTier]] = None

   
The general information in TierInformation can be founded from top rows / first table.
The tables follow contain information of entities. some entities are taken from "()" in other entity name, we don't need to take these entities.
Use only English/alphabetic characters for the output, and refer to any comments in the Pydantic Object for additional context. If a field's value is not present in the image, set that field as "None" without making inferences from other fields.

Especially, in the content, if we have words like "with <number> tier(s)" with <number> is greater than 1, its obviously "Multi tier".
If there is any entity in the EntityList that has Tier > 1, return "Multi tier" else return "One tier".
If all data in table format and not have lines with HEADING "Tier 1" / "Tier 2" / "Tier 3" / ... -> method is "tier-by-location". Otherwise, method is "tier-not-by-location".
The output would be a Pydantic Object based on the structure provided below:

class TierClassification(BaseModel):
    EntityClass: Optional[str] = None
    Method: Optional[str] = None

with:
    + EntityClass: "Multi tier" or "One tier"
    + Method: "tier-not-by-location" or "tier-by-location"

The output should follow the example format, containing only the structured Pydantic data. Avoid including Python class definitions, import statements, FieldInfo, or FieldInfoList.
Please keep the response in the specified Pydantic Object TierClassification format with all fields, not JSON format.
'''

    TIER_DETECTION_TEMPLATE = '''
Extract text from the image using OCR (Pytesseract), adjusting for any flipped or skewed orientation if needed.
In the document, we can have multi-tier entities and the order is tier 1 > tier 2 > tier 3 > tier 4 ... There are some cases for multi-tier detection:
	    1. In the Name / InvestorName / Requester Name column, values with the same indentation level will have the same tier, otherwise they have different tier. If the values that have a deeper indentation from the left (like 1 tab / many tabs / center align) than the previous value -> their tier will be lower.
	    2. In the Name / InvestorName / Requester Name column, it consists of many smaller columns (mark it as 1st, 2nd, 3rd, 4th, ... column). The tier order is determined by which column (1st, 2nd, 3rd, 4th, ...) the Name value belongs to from left to right. The value in the 1st column is tier 1, from 2nd column is tier 2, from 3rd column is 3, from 4th column is 4, ...
        3. If there is a Tier 1 / Tier 2 / Tier 3 / ... column in the input: we can get the tier of the entity by look at which column its name belongs to. 
        4. If there are lines with HEADING "Tier 1" / "Tier 2" / "Tier 3" / ...: Table above HEADING "Tier 1" contains all entities: Main information and list of entities. The first row of this table is the information of Main information. With the next rows in that table:
		    a. which row that has name appear in the table between HEADING "Tier 1" and HEADING "Tier 2" belongs to Tier1
		    b. which row that has name appear in the table between HEADING "Tier 2" and HEADING "Tier 3" belongs to Tier2
	        c. The table between HEADING "Tier 1" and HEADING "Tier 2" show the all Tier1 entities. The table between HEADING "Tier 2" and HEADING "Tier 3" show all Tier2 entities...
            We can check the same for the other tier

        Especially, for all 4 cases above, in case there are subset of consecutive entities that their allocation percentage sum up to 100 or 100%, their tier would be lower than the closest previous entity
        If one of 4 cases above is satisfied, please separate all entities by their tier. Entity with higher tier can have multiple child entities link with it.


Generate a Pydantic Object based on the structure provided below:

class EntityTier(BaseModel):
    Name: Optional[str] = None
    Tier: Optional[int] = None

class TierInformation(BaseModel):
    Name: Optional[str] = None
    EntityList: Optional[List[EntityTier]] = None

   
The general information in TierInformation can be founded from top rows / first table.
The tables follow contain information of entities. some entities are taken from "()" in other entity name, we don't need to take these entities.
The output should follow the structure format of TierInformation above, containing only the structured Pydantic data. Avoid including Python class definitions, import statements, FieldInfo, or FieldInfoList.
Use only English/alphabetic characters for the output, and refer to any comments in the Pydantic Object for additional context. If a field's value is not present in the image, set that field as "None" without making inferences from other fields.
IMPORTANT THING: Please keep the response in the specified TierInformation format with all fields, not JSON format.
'''

    FALLBACK_CASE_OTHER_TYPE = '''
Extract text from the image using OCR (Pytesseract), adjusting for any flipped or skewed orientation if needed.
Generate a Pydantic Object based on the structure provided below. There are some notes:
    - ParentName: for this field, please do it carefully cuz this is the most important, we will set them based on their tier (the order is tier 1 > tier 2 > tier 3 > ...). there are some cases to follow:
	    1. In the Name / InvestorName / Requester Name column, values with the same indentation level will have the same tier, otherwise they have different tier. If the values that have a deeper indentation from the left (like 1 tab or center align) than the previous value -> their tier will be lower and the closest previous value with a higher tier is their Parent. ParentName of tier 1 entities would be Name in MainInformation
	    2. In the Name / InvestorName / Requester Name column, it consists of many smaller columns (mark it as 1st, 2nd, 3rd, ... column). The tier order is determined by which column (1st, 2nd, 3rd, ...) the Name value belongs to from left to right. The value in the 1st column is tier 1, from 2nd column is tier 2, from 3rd column is 3, ...
            3. If there is a Tier 1 / Tier 2 / Tier 3 / ... column in the input: The structure of each entity in Tier 1 / Tier 2 / Tier 3 / ... will include Name, Address, EIN. Normally, the ParentName of the values in each Tier will be the Name value in the closest entity with higher tier(example: Parent of Tier 2 will be Tier 1, Parent of Tier 3 will be Tier 2, ...). Tier 1 ParentName would be Name in MainInformation. Please get entity in all tiers. 
            4. If there are lines with HEADING "Tier 1" / "Tier 2" / "Tier 3" / ...: Table above HEADING "Tier 1" contains all entities: Main information and list of entities. The first row of this table is the information of Main information. With the next rows in that table:
		a. which row that has name appear in the table between HEADING "Tier 1" and HEADING "Tier 2" belongs to Tier1 and their ParentName would be Name in MainInformation
		b. which row that has name appear in the table between HEADING "Tier 2" and HEADING "Tier 3" belongs to Tier2L and their ParentName would be the closest tier1 entity. You can see that the ParentName of them exists next to HEADING "Tier 2:"
		* We can check the same for the other tier
	     The table between HEADING "Tier 1" and HEADING "Tier 2" show the allocation percentage of each Tier1 entities. The table between HEADING "Tier 2" and HEADING "Tier 3" show the allocation percentage of each Tier2 entities. We can check the same for the other tier
	 Especially, for all 4 cases above, in case there are subset of entities that their allocation percentage sum up to 100 or 100%, their ParentName will be the closest previous entity with higher tier
	 If one of 4 cases above is satisfied, please separate all entities by their tier. Entity with higher tier can have multiple child entities link with it.
	 If none of 4 cases above occur, ParentName would be Name in MainInformation
    - If we have columns like Tier 1 / Tier 2 / Tier 3 / ..., you can look at the AllocationPercentage of each Tier for each entity. Please try to get all of the entities with their corresponding AllocationPercentage in each Tier (Tier 1 entity have Tier 1 AllocationPercentage, Tier 2 entity have Tier 2 AllocationPercentage, ...)
    - EntityType (can be a code number or string, prefer to get the code): 
        + its not value from columns like "Benificial Owner" / "Intermediary" / "FlowThrough" / "US Branch" / "ForeignStatusType" / "Chapter 4 Status"
        + if we have a column with column name has "Entity Type" in it, get corresponding value from that column. 
        + if not have this column, get it from column that has "chapter 3" / "type of recipient" in its lower name.
      If have multiple values like string or code, please return the code. 
    - City, State, Country and ZipCode can be extracted from address. Please be careful not to misclassify between City / State / Country / ZipCode
    - EIN: if not have this column, get it from USTIN or TIN column
    - Chapter4Status (can be a code number or string, prefer to get the code): Column with lower name has "chapter 4" or "fatca status" in it . please get the first one you see
    - ForeignTaxpayerId: if not have this column, get it from FTIN or ForeignTIN column
    - Name is the same with InvestorName
    - Number is the same with AccountNumber
    - FormType is the same with DocumentType / Type of Document
    - AllocationPercentage: have "allocation %" / "allocation percentage" / "allocation" in lower column name. If EntitiesList only have 1 entity, then its value would be 100.00%
    - TierOwnershipPercentage: ownership percentage of tier

If column's name has multiple components mentioned above, please get each value of each component (Example: if column's name is "Entity Type, Resident Country, Type of Document" -> it has 3 components: EntityType, Country, FormType). Based on the order in the column's name, you can know which value belongs to which component. 

class Entity(BaseModel):
    AccountNumber: Optional[str] = None
    Name: Optional[str] = None
    ParentName: Optional[str] = None
    AddressLine1: Optional[str] = None
    AddressLine2: Optional[str] = None
    AddressLine3: Optional[str] = None
    City_Town: Optional[str] = None
    State: Optional[str] = None
    Country: Optional[str] = None
    ZipCode: Optional[str] = None
    FormType: Optional[str] = None
    EIN: Optional[str] = None
    GIIN: Optional[str] = None
    EntityType: Optional[str] = None
    Chapter4Status: Optional[str] = None
    ForeignTaxpayerId: Optional[str] = None
    AllocationPercentage: Optional[str] = None
    TierOwnershipPercentage:  Optional[str] = None

class MainInformation(BaseModel):
    Date: Optional[str] = None
    Name: Optional[str] = None
    AddressLine1: Optional[str] = None
    AddressLine2: Optional[str] = None
    AddressLine3: Optional[str] = None
    City_Town: Optional[str] = None
    State: Optional[str] = None
    Country: Optional[str] = None
    ZipCode: Optional[str] = None
    FormType: Optional[str] = None
    EIN: Optional[str] = None
    EntityType: Optional[str] = None
    Chapter4Status: Optional[str] = None
    GIIN: Optional[str] = None
    Number: Optional[str] = None
    EntityList: Optional[List[Entity]] = None
   
The general information in MainInformation can be founded from top rows / first table.
The tables follow contain information of entities.
The output should follow the example format, containing only the structured Pydantic data. Avoid including Python class definitions, import statements, FieldInfo, or FieldInfoList.
Use only English/alphabetic characters for the output, and refer to any comments in the Pydantic Object for additional context. If a field's value is not present in the image, set that field as "None" without making inferences from other fields.
Please keep the response in the specified Pydantic Object format with all fields, not JSON format.
'''