#Import pacckages
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import random
import requests
import os
import random
import requests
from googleapiclient.discovery import build
import markdown
from bs4 import BeautifulSoup
import PyPDF2
load_dotenv()


## Read necessary keys, paths
YOUR_LINKEDIN_ID = 'YtWllkhxbm'
GEMINI_API_KEY = os.environ['GEMINI_API_KEY']
L_ACCESS_TOKEN = os.environ['L_ACCESS_TOKEN']
file_path = 'CGST-Act-Updated-30092020.pdf'

# Create util funtions

def markdown_to_plain_text(markdown_text):
    """Convert Markdown text to plain text."""
    # Convert Markdown to HTML
    html = markdown.markdown(markdown_text)
    
    # Parse HTML and extract plain text
    soup = BeautifulSoup(html, 'html.parser')
    plain_text = soup.get_text()
    
    return plain_text.strip() 

def read_pdf(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {str(e)}")
    return text

pdf_text = read_pdf(file_path)

# Create a topic list and select one at random

gst_topics = [
    "Introduction to GST: Overview and Importance",
    "GST Registration Process: A Step-by-Step Guide",
    "Types of GST: CGST, SGST, and IGST Explained",
    "Filing GST Returns: A Comprehensive Guide",
    "Input Tax Credit (ITC): How to Claim and Its Importance",
    "Key Compliance Requirements for GST",
    "Recent Amendments in GST Laws: What You Need to Know",
    "GST and E-commerce: Implications for Online Businesses",
    "GST Benefits and Challenges for Small Businesses",
    "Common Challenges in GST Implementation",
    "Understanding GST Invoices: Requirements and Types",
    "Reverse Charge Mechanism in GST: A Detailed Explanation",
    "GST's Impact on Cross-Border Trade",
    "GST Implications in Real Estate Transactions",
    "The Importance of Accurate Billing Under GST",
    "GST Compliance for International Trade",
    "GST Audits: What to Expect and Why They're Important",
    "Impact of GST on Inflation Rates in India",
    "Sector-Specific GST Issues: Agriculture, Manufacturing, and Services",
    "Filing Appeals Against GST Orders: A Guide",
    "Common GST Mistakes: How to Avoid Them",
    "The Role of GST Training and Workshops in Compliance",
    "Technology and GST Compliance: Tools and Software",
    "Impact of GST on Supply Chain Management",
    "Consumer Rights Under GST: What You Should Know",
    "GST Implications for Charitable Organizations and NGOs",
    "Future Predictions for GST in India",
    "Understanding GST Penalties and How to Mitigate Them",
    "Real-Life Case Studies of GST Challenges and Solutions",
    "FAQs on GST: Answering Common Queries",
    "GST Compliance and Audits: Key Takeaways",
    "GST on Services: How It Differs from Goods",
    "State-Specific GST Issues: Understanding Local Regulations",
    "GST and the Informal Sector: Challenges and Opportunities",
    "GST and Its Effect on Business Cash Flow",
    "Navigating GST in a Digital Economy",
    "Understanding Zero-Rated Supplies Under GST",
    "The Role of Technology in GST Compliance and Reporting",
    "GST and Export of Goods and Services: Key Considerations",
    "The Impact of GST on Consumer Pricing",
    "GST as a Tool for Economic Growth: Analyzing its Impact",
    "The Concept of Composition Scheme Under GST",
    "How to Prepare for a GST Audit",
    "GST and Foreign Direct Investment (FDI)",
    "GST and Tax Administration Reforms",
    "Understanding the GST Council and Its Functions",
    "GST and Agricultural Products: Exemptions and Compliance",
    "The Role of GST in Atmanirbhar Bharat (Self-Reliant India)",
    "Public Awareness on GST: The Need for Education",
    "Analyzing the Effect of GST on State Revenues",
    "GST and the Impact on the Real Estate Market",
    "Understanding Transitional Provisions in GST",
    "Comparing GST with the Previous Tax Regime",
    "The Role of Professionals in GST Compliance",
    "Key Takeaways from the GST Act: A Summary",
]

selected = random.choice(gst_topics)

# Define a prompt to send to LLM

prompt_text = f"""

## Start of Prompt Instruction 
Pls use "{selected}" as an interest topic and collate material on the same. Then perform the following

Create a professional yet engaging LinkedIn post that:

Starts with an attention-grabbing hook
Extracts the most valuable insight for financial professionals
Breaks down complex information into 3-4 clear bullet points
Do not use any Emojis
Includes 1-2 relevant examples or applications
Ends with an engaging question or clear call-to-action
Adds 3-4 relevant hashtags

The post should:

Be 500-1000 characters
Use line breaks & para breaks for readability
Sound authoritative but conversational
Highlight practical implications for business owners/finance professionals
Focus on actionable takeaways

The output has to be in normal text format - NOT Markdown format
Do not leave out any blanks/variables to be filled. Please format the response as a ready-to-post LinkedIn update. 

** Here is the context **
{pdf_text}

"""


#### Creating a post using Gemini APIs
genai.configure(api_key=GEMINI_API_KEY)

# model = genai.GenerativeModel(model_name="gemini-1.5-pro")
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,      
    }

response = model.generate_content(prompt_text,
    safety_settings = safety_settings)

final_post = response.candidates[0].content.parts[0].text
final_post_simple_text = markdown_to_plain_text(final_post)

# Post to Linkedin

def post_to_linkedin(post_content):
    """Post content to LinkedIn with private visibility"""
    url = 'https://api.linkedin.com/v2/ugcPosts'
    
    headers = {
        'Authorization': f'Bearer {L_ACCESS_TOKEN}',
        # 'Content-Type': 'application/json'
    }
    
    post_data = {
        "author": "urn:li:person:YtWllkhxbm",  # Replace with your LinkedIn ID
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": post_content
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    response = requests.post(url, headers=headers, json=post_data)
    return response.status_code == 201

post_to_linkedin(final_post_simple_text)



# import pandas as pd
# import numpy as np
# from openpyxl import load_workbook
# from openpyxl.utils.dataframe import dataframe_to_rows

# def process_excel(input_file, output_file=None):
#     """
#     Process Excel file by dividing all numeric values by 100000 and
#     adding ' (in Lakhs)' suffix to columns with numeric values.
    
#     Args:
#         input_file: Path to input Excel file
#         output_file: Path to output Excel file, if None, will use 'processed_' + input_file
    
#     Returns:
#         Path to the output file
#     """
#     if output_file is None:
#         output_file = f"processed_{input_file}"
    
#     # Load the Excel file
#     xls = pd.ExcelFile(input_file)
#     sheet_names = xls.sheet_names
    
#     # Create a writer object
#     writer = pd.ExcelWriter(output_file, engine='openpyxl')
    
#     # Process each sheet
#     for sheet_name in sheet_names:
#         # Read the sheet
#         df = pd.read_excel(input_file, sheet_name=sheet_name)
        
#         # Keep track of which columns have numeric values
#         numeric_columns = []
        
#         # Process each column
#         for col in df.columns:
#             # Check if column has numeric values
#             numeric_values = df[col].apply(lambda x: isinstance(x, (int, float)) and not np.isnan(x))
#             if numeric_values.any():
#                 # Only convert numeric values in the column
#                 df[col] = df[col].apply(lambda x: x/100000 if isinstance(x, (int, float)) and not np.isnan(x) else x)
#                 numeric_columns.append(col)
        
#         # Rename columns by adding suffix
#         column_mapping = {}
#         for col in numeric_columns:
#             if not ' (in Lakhs)' in col:  # Avoid adding suffix twice
#                 column_mapping[col] = f"{col} (in Lakhs)"
        
#         # Apply column renaming
#         df.rename(columns=column_mapping, inplace=True)
        
#         # Write to Excel
#         df.to_excel(writer, sheet_name=sheet_name, index=False)
    
#     # Save the Excel file
#     writer.close()
    
#     return output_file

# if __name__ == "__main__":
#     # Test with the provided file
#     output_file = process_excel('annual_report.xlsx')
#     print(f"Processed file saved as: {output_file}") 
