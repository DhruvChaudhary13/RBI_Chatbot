"""
Add standard RBI definitions to the vector database
"""

from vector_store import VectorStoreManager
from langchain.schema import Document

def add_standard_definitions():
    """Add standard RBI definitions and FAQs to the vector database"""
    print("📝 Adding standard RBI definitions to FAISS database...")
    
    vector_mgr = VectorStoreManager()
    
    # Standard RBI definitions and FAQs
    standard_definitions = [
        {
            "content": """What is a Non-Banking Financial Company (NBFC)?
A Non-Banking Financial Company (NBFC) is a company registered under the Companies Act, 1956 or Companies Act, 2013, and engaged in the business of loans and advances, acquisition of shares/stocks/bonds/debentures/securities issued by Government or local authority or other marketable securities of a like nature, leasing, hire-purchase, etc., as their principal business, but does not include any institution whose principal business is that of agriculture activity, industrial activity, purchase or sale of any goods (other than securities) or providing any services and sale/purchase/construction of immovable property. A non-banking institution which is a company and has principal business of receiving deposits under any scheme or arrangement in one lump sum or in installments by way of contributions or in any other manner, is also a non-banking financial company (Residuary non-banking company).""",
            "metadata": {"source": "RBI FAQ", "type": "definition"}
        },
        {
            "content": """What does conducting financial activity as "principal business" mean?
Financial activity as principal business is when a company's financial assets constitute more than 50 per cent of the total assets (netted off by intangible assets) and income from financial assets constitute more than 50 per cent of the gross income. A company which fulfils both these criteria needs to get registered as NBFC with the Reserve Bank. The term 'principal business' has not been defined in the Reserve Bank of India Act, 1934. Hence, the Reserve Bank has defined it vide Press Release 1998-99/1269 dated April 08, 1999 so as to ensure that only companies predominantly engaged in financial activity get registered with it and are regulated and supervised by it. Hence, if there are companies engaged in agricultural operations, industrial activity, purchase and sale of goods, providing services or purchase, sale or construction of immovable property as their principal business and are doing some financial business in a small way, they will not be regulated by the Reserve Bank. Interestingly, this test is popularly known as 50-50 test and is applied to determine whether or not a company is into financial business.""",
            "metadata": {"source": "RBI FAQ", "type": "definition"}
        },
        {
            "content": """What are the different types of NBFCs?
NBFCs are categorized as:
1. Asset Finance Company (AFC)
2. Investment Company (IC)
3. Loan Company (LC)
4. Infrastructure Finance Company (IFC)
5. Systemically Important Core Investment Company (CIC-ND-SI)
6. NBFC-Micro Finance Institution (NBFC-MFI)
7. NBFC-Factors
8. Mortgage Guarantee Companies (MGC)
9. NBFC-Infrastructure Debt Fund (NBFC-IDF)
10. Non-Banking Financial Company - Account Aggregator (NBFC-AA)""",
            "metadata": {"source": "RBI FAQ", "type": "classification"}
        },
        {
            "content": """What is the minimum net owned fund requirement for NBFCs?
The minimum Net Owned Fund (NOF) requirement for NBFCs is:
- Rs. 10 crore for most NBFCs
- Rs. 5 crore for NBFC-Micro Finance Institutions (NBFC-MFIs)
- Rs. 5 crore for NBFC-Factors
- Rs. 2 crore for NBFC-P2P, NBFC-AA, and NBFC not availing public funds
- Rs. 300 crore for NBFC-IFC and IDF-NBFC""",
            "metadata": {"source": "RBI FAQ", "type": "regulatory"}
        },
        {
            "content": """Is it mandatory for every NBFC to be registered with RBI?
Yes, it is mandatory for every NBFC to be registered with the Reserve Bank of India. No non-banking financial institution can commence or carry on the business of a non-banking financial institution without obtaining a Certificate of Registration from the Bank. However, to avoid duplication of regulation, certain entities are exempted from the requirement of registration with RBI.""",
            "metadata": {"source": "RBI FAQ", "type": "registration"}
        },
        {
            "content": """What is Scale Based Regulatory Framework for NBFCs?
The Scale Based Regulatory Framework (SBR Framework) for NBFCs was implemented by RBI effective October 01, 2022. It classifies NBFCs into four layers based on size, activity, complexity and interconnectedness:
1. Base Layer (NBFC-BL): Lowest regulatory requirements
2. Middle Layer (NBFC-ML): Medium regulatory requirements  
3. Upper Layer (NBFC-UL): Highest regulatory requirements (systemically significant)
4. Top Layer (NBFC-TL): Ideally empty, for extreme risk cases
The framework follows the principle of proportionality - regulations increase as you move from lower to higher layers.""",
            "metadata": {"source": "RBI FAQ", "type": "regulatory_framework"}
        }
    ]
    
    try:
        # Convert to Document objects
        documents = []
        for definition in standard_definitions:
            doc = Document(
                page_content=definition["content"],
                metadata=definition["metadata"]
            )
            documents.append(doc)
        
        # Add documents to vector store
        success = vector_mgr.add_documents(documents)
        
        if success:
            print(f"✅ Added {len(documents)} standard RBI definitions to FAISS database")
            return True
        else:
            print("❌ Failed to add definitions to vector store")
            return False
            
    except Exception as e:
        print(f"❌ Error adding definitions: {e}")
        return False

def check_definition_exists(vector_mgr, question):
    """Check if a definition already exists in the vector store"""
    try:
        # Use regular similarity_search instead of similarity_search_with_scores
        results = vector_mgr.similarity_search(question, k=1)
        return len(results) > 0
    except Exception as e:
        print(f"❌ Error checking definition: {e}")
        return False

if __name__ == "__main__":
    add_standard_definitions()