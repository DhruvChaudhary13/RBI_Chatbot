import os
import PyPDF2
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import re

class DataProcessor:
    def __init__(self, chunk_size=600, chunk_overlap=80):  # INCREASED for better context
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""],  # Added ; and ,
            length_function=len,
        )
    
    def clean_text(self, text):
        """Clean and preprocess the extracted text more intelligently"""
        if not text:
            return ""
            
        # Remove excessive whitespace but preserve meaningful paragraph breaks
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Preserve real paragraph breaks
        
        # Remove page numbers and headers more intelligently
        text = re.sub(r'\bPage\s*\d+\s*\b', '', text)
        text = re.sub(r'\b\d+\s*of\s*\d+\b', '', text)
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Remove common PDF artifacts but keep important content
        text = re.sub(r'RBI/DoR/\d{4}-\d{2}/\s*\d+', '', text)
        text = re.sub(r'DoR\.\s*FIN\.\s*REC\.\s*No\.\s*\d+/\d+\.\s*\d+\.\s*\d+/\d{4}-\d{2}', '', text)
        
        # Fix hyphenated words across lines
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s*\.\s*', '. ', text)
        text = re.sub(r'\s*,\s*', ', ', text)
        text = re.sub(r'\s*;\s*', '; ', text)
        text = re.sub(r'\s*:\s*', ': ', text)
        
        return text.strip()
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text with better content preservation"""
        print(f"Reading PDF from: {pdf_path}")
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                total_pages = len(pdf_reader.pages)
                pages_with_content = 0
                
                for page_num in range(total_pages):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    
                    if page_text and page_text.strip():
                        # Clean but preserve more content
                        cleaned_text = self.clean_text(page_text)
                        if len(cleaned_text) > 50:  # Increased threshold for better quality
                            text += cleaned_text + "\n\n"
                            pages_with_content += 1
                    
                    if (page_num + 1) % 50 == 0 or (page_num + 1) == total_pages:
                        print(f"   Processed {page_num + 1}/{total_pages} pages")
                
                print(f"Extracted text from {pages_with_content}/{total_pages} pages with content")
                print(f"Total characters extracted: {len(text):,}")
                return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return None
    
    def create_high_quality_chunks(self, text):
        """Create high-quality chunks optimized for regulatory documents"""
        if not text or len(text.strip()) == 0:
            print("No text to chunk")
            return []
            
        print("Creating HIGH-QUALITY chunks for optimal retrieval...")
        
        # Step 1: Split by major sections first
        sections = re.split(r'\n\s*\n', text)
        print(f"   Found {len(sections)} major sections")
        
        all_chunks = []
        
        for i, section in enumerate(sections):
            section = section.strip()
            if len(section) < 80:  # Increased minimum section size
                continue
                
            # Step 2: Use the text splitter on each substantial section
            docs = self.text_splitter.split_documents([Document(page_content=section)])
            
            # Step 3: Filter for high-quality chunks
            for doc in docs:
                content = doc.page_content.strip()
                
                # Quality checks - MORE SELECTIVE
                if len(content) < 50:  # Increased minimum
                    continue
                    
                # Check if chunk has meaningful text (not just numbers/special chars)
                alpha_chars = len(re.findall(r'[a-zA-Z]', content))
                if alpha_chars < 25:  # Increased threshold
                    continue
                    
                # Check if chunk has reasonable sentence structure
                sentences = len(re.findall(r'[.!?]', content))
                words = len(content.split())
                
                # Reject chunks that are mostly numbers/formatting
                if words > 0 and (alpha_chars / len(content)) < 0.4:
                    continue
                    
                # Prefer chunks with complete sentences
                if sentences == 0 and words > 15:
                    # If no sentence endings but has substantial content, it might be a list or definition
                    pass
                    
                all_chunks.append(doc)
        
        print(f"Created {len(all_chunks)} high-quality chunks")
        return all_chunks
    
    def analyze_chunk_quality_enhanced(self, chunks):
        """Enhanced analysis of chunk quality"""
        if not chunks:
            print("No chunks to analyze")
            return
        
        print("\nENHANCED CHUNK QUALITY ANALYSIS:")
        print(f"Total chunks generated: {len(chunks)}")
        
        # Size distribution
        sizes = [len(chunk.page_content) for chunk in chunks]
        print(f"Size Analysis:")
        print(f"   Average: {sum(sizes)/len(sizes):.0f} chars")
        print(f"   Min: {min(sizes)} chars")
        print(f"   Max: {max(sizes)} chars")
        
        # Size distribution buckets (optimized ranges)
        tiny = len([s for s in sizes if s < 80])
        small = len([s for s in sizes if 80 <= s < 200])
        medium = len([s for s in sizes if 200 <= s < 400])
        large = len([s for s in sizes if s >= 400])
        print(f"   Distribution: {tiny} tiny (<80), {small} small (80-200), {medium} medium (200-400), {large} large (400+)")
        
        # Content quality analysis
        print(f"\nContent Quality Analysis:")
        high_quality = 0
        medium_quality = 0
        low_quality = 0
        
        for chunk in chunks:
            content = chunk.page_content
            sentences = len(re.findall(r'[.!?]', content))
            words = len(content.split())
            alpha_ratio = len(re.findall(r'[a-zA-Z]', content)) / len(content) if content else 0
            
            if sentences >= 2 and words >= 20 and alpha_ratio > 0.6:
                high_quality += 1
            elif sentences >= 1 and words >= 12 and alpha_ratio > 0.4:
                medium_quality += 1
            else:
                low_quality += 1
                
        print(f"   High quality: {high_quality} ({high_quality/len(chunks)*100:.1f}%)")
        print(f"   Medium quality: {medium_quality} ({medium_quality/len(chunks)*100:.1f}%)")
        print(f"   Low quality: {low_quality} ({low_quality/len(chunks)*100:.1f}%)")
        
        # Key terms analysis - EXPANDED for RBI content
        print(f"\nKEY RBI TERMS COVERAGE:")
        key_terms = {
            'nbfc': 'NBFC',
            'deposit': 'Deposit', 
            'capital': 'Capital',
            'reserve bank': 'RBI',
            'regulation': 'Regulation',
            'layer': 'SBR Layers',
            'registration': 'Registration',
            'public funds': 'Public Funds',
            'sebi': 'SEBI',
            'credit rating': 'Credit Rating',
            'money circulation': 'Money Circulation',
            'prize chits': 'Prize Chits',
            'slcc': 'SLCC',
            'state level': 'State Level',
            'rbi act': 'RBI Act'
        }
        
        for term, display_name in key_terms.items():
            count = sum(1 for chunk in chunks if term in chunk.page_content.lower())
            percentage = (count / len(chunks)) * 100
            print(f"   {display_name}: {count} chunks ({percentage:.1f}%)")
    
    def show_sample_chunks(self, chunks, num_samples=5):
        """Show sample chunks with quality assessment"""
        print(f"\nSAMPLE CHUNKS (First {num_samples}):")
        print("-" * 80)
        
        for i in range(min(num_samples, len(chunks))):
            chunk = chunks[i]
            content = chunk.page_content
            words = len(content.split())
            sentences = len(re.findall(r'[.!?]', content))
            
            print(f"Sample {i+1} ({len(content)} chars, {words} words, {sentences} sentences):")
            print(f"{content[:200]}..." if len(content) > 200 else content)
            print("-" * 60)
    
    def process_pdf(self, pdf_path):
        """Complete PDF processing pipeline with enhanced chunking"""
        print(f"PROCESSING PDF: {pdf_path}")
        print("=" * 60)
        
        # Check if file exists
        if not os.path.exists(pdf_path):
            print(f"PDF file not found: {pdf_path}")
            return None
        
        # Check file size
        file_size = os.path.getsize(pdf_path) / (1024 * 1024)  # MB
        print(f"File size: {file_size:.1f} MB")
        
        # Extract and clean text
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            print("Failed to extract text from PDF")
            return None
        
        print(f"Text extraction: {len(text):,} characters")
        
        # Create high-quality chunks
        chunks = self.create_high_quality_chunks(text)
        
        if chunks:
            # Enhanced analysis
            self.analyze_chunk_quality_enhanced(chunks)
            self.show_sample_chunks(chunks)
            
            print(f"\nPDF PROCESSING COMPLETED!")
            print(f"   Created {len(chunks)} high-quality chunks from 330-page PDF")
            
            # Quality assessment
            if len(chunks) >= 2000 and len(chunks) <= 4000:
                print(f"   OPTIMAL RANGE! {len(chunks)} chunks - Perfect balance for accuracy")
            elif len(chunks) < 1500:
                print(f"   TOO FEW: {len(chunks)} chunks - May miss important context")
            else:
                print(f"   GOOD: {len(chunks)} chunks - Should work well")
                
        else:
            print("Failed to create chunks")
            
        return chunks

# Test with different chunk sizes
def test_optimized_processing():
    """Test the optimized processing"""
    from config import Config
    
    print("TESTING OPTIMIZED PDF PROCESSING")
    print("=" * 60)
    
    # Test with optimal chunk size
    processor = DataProcessor(chunk_size=600, chunk_overlap=80)
    chunks = processor.process_pdf(Config.PDF_PATH)
    
    return chunks

if __name__ == "__main__":
    test_optimized_processing()
