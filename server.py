from fastmcp import FastMCP
import asyncio
import logging
import xml.etree.ElementTree as ET
import requests
from requests.auth import HTTPDigestAuth
from dotenv import load_dotenv
import os


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("AddressServer", "Returns dummy addresses")

@mcp.tool()
def get_address(name: str) -> str:
    """Get the address for a person by name"""
    logger.info(f"Looking up address for: {name}")
    return f"{name} lives at 123 Main Street, Springfield"

@mcp.tool(description="Returns biomarker validity categories with counts for a given biomarker")
def get_biomarker_validity(biomarker: str) -> str:
    """
    Retrieves the biomarker validity categories and their counts from the API response.

    This tool lists the possible validity stages (e.g., Experimental, Early Studies in Humans,
    Late Studies in Humans, Emerging, Recommended / Approved) along with how many
    biomarkers fall into each category. It is useful for understanding the distribution
    of biomarkers across different validation stages.
    """
    # Replace these with actual values or environment variables
    load_dotenv()
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    # Example API endpoint
    url = f"https://api.cortellis.com/api-ws/ws/rs/biomarkers-v3/biomarkerUse/search?query={biomarker}"

    # Make the request
    response = requests.get(url, auth=HTTPDigestAuth(username, password))
    logger.info(f"username: {username}")
    logger.info(f"password: {password}")
    # logger.info(f"API Response Status Code: {response.status_code}")
    if response.status_code == 200:
        xml_data = response.text

        # Parse XML
        root = ET.fromstring(xml_data)
        validity_filter = root.find(".//Filter[@label='Validity']")
        if validity_filter is not None:
            return ET.tostring(validity_filter, encoding='unicode')
        else:
            print("No Validity filter found.")

    logger.info(f"Checking validity for: {biomarker}")
    return str(biomarker.isalpha())


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