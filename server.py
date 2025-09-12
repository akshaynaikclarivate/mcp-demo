from fastmcp import FastMCP
import asyncio
import logging
import xml.etree.ElementTree as ET
import requests
from requests.auth import HTTPDigestAuth
from dotenv import load_dotenv
import os
import json
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("AddressServer", "Returns dummy addresses")

# @mcp.tool()
# def get_address(name: str) -> str:
#     """Get the address for a person by name"""
#     logger.info(f"Looking up address for: {name}")
#     return f"{name} lives at 123 Main Street, Springfield"

# @mcp.tool(description="Returns biomarker validity categories with counts for a given biomarker")
# def get_biomarker_validity(biomarker: str) -> str:
#     """
#     Retrieves the biomarker validity categories and their counts from the API response.

#     This tool lists the possible validity stages (e.g., Experimental, Early Studies in Humans,
#     Late Studies in Humans, Emerging, Recommended / Approved) along with how many
#     biomarkers fall into each category. It is useful for understanding the distribution
#     of biomarkers across different validation stages.
#     """
#     # Replace these with actual values or environment variables
#     load_dotenv()
#     username = os.getenv("USERNAME")
#     password = os.getenv("PASSWORD")

#     # Example API endpoint
#     url = f"https://api.cortellis.com/api-ws/ws/rs/biomarkers-v3/biomarkerUse/search?query={biomarker}"

#     # Make the request
#     response = requests.get(url, auth=HTTPDigestAuth(username, password))
#     logger.info(f"username: {username}")
#     logger.info(f"password: {password}")
#     # logger.info(f"API Response Status Code: {response.status_code}")
#     if response.status_code == 200:
#         xml_data = response.text

#         # Parse XML
#         root = ET.fromstring(xml_data)
#         validity_filter = root.find(".//Filter[@label='Validity']")
#         if validity_filter is not None:
#             return ET.tostring(validity_filter, encoding='unicode')
#         else:
#             print("No Validity filter found.")

#     logger.info(f"Checking validity for: {biomarker}")
#     return str(biomarker.isalpha())


# Kimons code base 
def _runRESTcall(url,user,key,fileFormat):  
    """ 
    execute a REST call and return XML 
    @param url: 
    @return: XML and text message 
    """  
    response = None
    if fileFormat=="json":
        headers = {'Accept': 'application/json'}  
    if fileFormat=="xml":
        headers = {'Accept': 'application/xml'}
     
    try:  
        r = requests.get(url, auth=HTTPDigestAuth(user,key), headers=headers)  
    except Exception:  
        return response, Exception.message  
  
    try:  
        response = r.text
        message = "success"  
    except:  
        if r.status_code != 200:  
            message = str(r.status_code) + " Error " + r.text  
        else:  
            message = r.text  
    return response, message  

@mcp.tool()    
async def getCompanyRecords(idList):
    """Get the company record for a company id. Do not use this tool to analyze drug details, use getDrugRecord instead.

    Args:
        idList: Comma-separated list of company IDs use getCompanyResults to get the IDs for a company name
    """
    fileFormat="json"
    url = 'https://api.cortellis.com/api-ws/ws/rs/company-v2/companies?idList='+idList
    load_dotenv()
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    recordResponse, message = _runRESTcall(url,username,password,fileFormat)
    companyRecords=json.loads(recordResponse)
    return companyRecords
    
@mcp.tool()
async def getCompanyResults (companyName):
    """Get the company ID for a company name. Use this function to get a company ID for a name.

    Args:
        companyName: User-provided string of company name
    """
    fileFormat="json"
    offset="0"
    hits="25"
    load_dotenv()
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    url = 'https://api.cortellis.com/api-ws/ws/rs/company-v2/company/search/?query=companyNameDisplay:'+companyName+'&offset='+offset+'&hits='+hits+'&filtersEnabled=0&returnFilterCount=10&sortBy=+companyNameDisplay'
    recordResponse, message = _runRESTcall(url,username,password,fileFormat)
    idlist=[]
    companies=json.loads(recordResponse)
    for company in companies['companyResultsOutput']['SearchResults']['Company']:
        idlist.append(company['@id'])
    return ','.join(idlist)
    
@mcp.tool()
async def getDrugsForCompany(companyIDs):
    """Use this function to get the drug IDs for a given company
        Get all drugs that the company has at different stages of development.

    Args:
        companyIDs: a comma-separated list of company IDs that you can get from the getCompanyResults function.
    """
    fileFormat="json"
    offset="0"
    hits="999"
    load_dotenv()
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    url = 'https://api.cortellis.com/api-ws/ws/rs/drugs-v2/drug/search?query=companiesPrimary::OR('+companyIDs+') OR companiesSecondary::OR('+companyIDs+')&hits='+hits+'&sortBy=-phaseHighest'
    recordResponse, message = _runRESTcall(url,username,password,fileFormat)
    drugRecords=json.loads(recordResponse)
    idlist=[]
    for drug in drugRecords['drugResultsOutput']['SearchResults']['Drug']:
        idlist.append(drug['@id'])
    return ','.join(idlist)


@mcp.tool()
def getDrugRecordDevelopmentStatus (drugIDs):
    """Use this function to get the current development status of up to 50 drugs
        
    Args:
        drugIDs: a comma-separated list of up to 50 drug IDs that you can get from the getDrugsForCompany function.
    """
    fileFormat="json"
    offset="0"
    hits="999"
    load_dotenv()
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    
    url = 'https://api.cortellis.com/api-ws/ws/rs/drugs-v2/drugs?idList='+drugIDs
    recordResponse, message = _runRESTcall(url,username,password,fileFormat)
    drugs=json.loads(recordResponse)

    drugDevStatusList={}
    for drug in drugs['drugRecordsOutput']['Drug']:
        drugDevStatusList[drug['DrugName']]=[]
        if type(drug['IDdbDevelopmentStatus']['DevelopmentStatusCurrent']) is list:
            for currentStatus in drug['IDdbDevelopmentStatus']['DevelopmentStatusCurrent']:
                devStatus={}
                devStatus['Company']=currentStatus['Company']['$']
                devStatus['Country']=currentStatus['Country']['$']
                devStatus['DevelopmentStatus']=currentStatus['DevelopmentStatus']['$']
                devStatus['Indication']=currentStatus['Indication']['$']
                drugDevStatusList[drug['DrugName']].append(devStatus)
            
        else:
            devStatus={}
            currentStatus=drug['IDdbDevelopmentStatus']['DevelopmentStatusCurrent']
            devStatus['Company']=currentStatus['Company']['$']
            devStatus['Country']=currentStatus['Country']['$']
            devStatus['DevelopmentStatus']=currentStatus['DevelopmentStatus']['$']
            devStatus['Indication']=currentStatus['Indication']['$']
            drugDevStatusList[drug['DrugName']].append(devStatus)
        return drugDevStatusList


@mcp.tool()
def getActiveTrials (companyIDs):
    """Use this function to get the currently active clinical trials for a company or a list of companies. The function will only return trials that are
        either not yet recruiting, currently recruiting or no longer recruiting but which have not been completed, terminated or suspended
        
    Args:
        companyIDs: a comma-separated list of up to 50 Company IDs that you can get from the getCompanyResults function.
    """

    fileFormat="json"
    offset="0"
    hits="999"
    load_dotenv()
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    url = 'https://api.cortellis.com/api-ws/ws/rs/trials-v2/trial/search/?query=(trialCompaniesSponsor::OR('+companyIDs+') OR trialCompaniesCollaborator::OR('+companyIDs+')) AND trialRecruitmentStatus::OR(1,2,3)&filtersEnabled=false&hits='+hits
    recordResponse, message = _runRESTcall(url,username,password,fileFormat)

    activeTrials=json.loads(recordResponse)
    # activeTrials=recordResponse
    print (activeTrials, file=sys.stderr)
    
    activeTrialsList=[]
    for trial in activeTrials['trialResultsOutput']['SearchResults']['Trial']:
        activeTrial={}
        activeTrial['Trial Name']=trial['TitleDisplay']
        activeTrial['Phase']=trial['Phase']
        
        if 'Countries' in trial:
            if type(trial['Countries']['Country']) is list:
                activeTrial['Countries']=','.join(trial['Countries']['Country'])
            else:
                activeTrial['Countries']=trial['Countries']['Country']
        
        if type(trial['InterventionsPrimaryDisplay']['Intervention']) is list:
            activeTrial['Primary Interventions']=','.join(trial['InterventionsPrimaryDisplay']['Intervention'])
        else:
            activeTrial['Primary Interventions']=trial['InterventionsPrimaryDisplay']['Intervention']
        
        if 'Indications' in trial:
            if type(trial['Indications']['Indication']) is list:
                activeTrial['Indications']=','.join(trial['Indications']['Indication'])
            else:
                activeTrial['Indications']=trial['Indications']['Indication']

        if type(trial['CompaniesSponsor']['Company']) is list:
            activeTrial['Trial Sponsor Companies']=','.join(trial['CompaniesSponsor']['Company'])
        else:
            activeTrial['Trial Sponsor Companies']=trial['CompaniesSponsor']['Company']
        
        if 'TrialCategories' in trial:
            if type(trial['TrialCategories']['Category']) is list:
                activeTrial['Trial Categories']=','.join(trial['TrialCategories']['Category'])
            else:
                activeTrial['Trial Categories']=trial['TrialCategories']['Category']
        
        if 'TermsPatientSelection' in trial:
            if type(trial['TermsPatientSelection']['Term']) is list:
                activeTrial['Pateint Demographics']=','.join(trial['TermsPatientSelection']['Term'])
            else:
                activeTrial['Patient Demographics']=trial['TermsPatientSelection']['Term']
        activeTrialsList.append(activeTrial)
    return (activeTrialsList)

@mcp.tool()    
async def getRegDocumentMetadata(idrac):
    """Get the regulatory document metadata to understand if there are previous versions of this document

    Args:
        idrac: document id
    """
    fileFormat="json"
    url = "https://api.cortellis.com/api-ws/ws/rs/regulatory-v2/regulatory/"+idrac
    load_dotenv()
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    recordResponse, message = _runRESTcall(url,username,password,fileFormat)
    regDocumentMetadata=json.loads(recordResponse)
    return regDocumentMetadata

@mcp.tool()    
async def getRegDocumentPDF(idrac):
    """Get the regulatory document source PDF document to analyze and provide insights
    Args:
        idrac: document id
    """
    fileFormat="json"
    url = "https://api.cortellis.com/api-ws/ws/rs/regulatory-v2/regulatory/"+idrac+"?fmt=pdf"
    load_dotenv()
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    recordResponse, message = _runRESTcall(url,username,password,fileFormat)
    return recordResponse




if __name__ == "__main__":
    try:
        logger.info("Starting AddressServer...")
        # Run in Streamable HTTP mode with proper configuration
        mcp.run(
            transport="http", 
            host="0.0.0.0", 
            port=8000,
            # Add some FastMCP specific options if available
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise
