#!/usr/bin/env python3

import argparse
import os
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import logging
from bs4 import BeautifulSoup

def optimize_html_for_ats(html_content):
    """
    Optimize the HTML content for better ATS compatibility.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Ensure all text is properly represented and not hidden
    # Remove elements that might cause issues with ATS systems
    for element in soup.select('[style*="display:none"], [style*="display: none"], [hidden]'):
        element.extract()
    
    # Ensure proper heading hierarchy
    for i, heading in enumerate(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])):
        heading['data-ats-heading'] = 'true'
    
    # Add appropriate attributes to enhance accessibility and ATS parsing
    for a in soup.find_all('a'):
        if a.get('href') and not a.get('aria-label'):
            a['aria-label'] = a.text.strip()
    
    # Add a special class to important content sections
    for section in soup.find_all('section'):
        section['data-ats-section'] = 'true'
        if 'id' in section.attrs:
            if 'summary' in section['id']:
                section['role'] = 'region'
                section['aria-label'] = 'Professional Summary'
            elif 'experience' in section['id']:
                section['role'] = 'region'
                section['aria-label'] = 'Work Experience'
            elif 'education' in section['id']:
                section['role'] = 'region'
                section['aria-label'] = 'Education'
            elif 'skills' in section['id']:
                section['role'] = 'region'
                section['aria-label'] = 'Skills'
            elif 'achievements' in section['id']:	
                section['role'] = 'region'
                section['aria-label'] = 'Achievements'
            elif 'references' in section['id']:
                section['role'] = 'region'
                section['aria-label'] = "References"
    
    # Ensure lists are properly formatted
    for ul in soup.find_all('ul'):
        ul['data-ats-list'] = 'true'
        for li in ul.find_all('li'):
            li['data-ats-item'] = 'true'
    
    # Add additional hidden metadata that can help ATS systems
    # Add the content as both visible and in metadata
    meta_keywords = ""
    for skill in soup.select('.skills-list li'):
        meta_keywords += skill.text.strip() + ", "
    
    # Add meta tags if they don't exist
    if not soup.find('meta', {'name': 'keywords'}):
        meta_tag = soup.new_tag('meta')
        meta_tag['name'] = 'keywords'
        meta_tag['content'] = meta_keywords.strip(', ')
        if soup.head:
            soup.head.append(meta_tag)

    return str(soup)

def convert_html_to_pdf(html_file, output_pdf=None, optimize_for_ats=True):
    """
    Convert HTML file to PDF with ATS optimization
    
    Args:
        html_file (str): Path to the HTML file or HTML content string
        output_pdf (str, optional): Path to save the PDF file. Defaults to None.
        optimize_for_ats (bool, optional): Whether to optimize the HTML for ATS systems. Defaults to True.
    
    Returns:
        str: Path to the generated PDF file
    """
    try:
        # Check if input is a file path or HTML content
        if os.path.isfile(html_file):
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # If output_pdf is not specified, use the same name as the input file
            if not output_pdf:
                file_name = os.path.splitext(os.path.basename(html_file))[0]
                output_pdf = f"{file_name}.pdf"
        else:
            # Assume html_file is actually HTML content
            html_content = html_file
            output_pdf = output_pdf or "output.pdf"
        
        # Optimize HTML for ATS if requested
        if optimize_for_ats:
            html_content = optimize_html_for_ats(html_content)
        
        # Create HTML object
        html = HTML(string=html_content)
        
        # Configure font
        font_config = FontConfiguration()
        
        # Define custom CSS for better PDF rendering
        custom_css = CSS(string='''
            @page {
                margin: 1.2cm 1cm;
                size: letter;
                @top-center {
                    content: "";
                }
                @bottom-center {
                    content: "";
                }
            }
            /* Rest of your CSS */
        ''', font_config=font_config)
        # Add PDF metadata
        meta_keywords = ""
        
        metadata = {
            'Title': 'Mohamed Amine SAYAGH - Software Developer Resume',
            'Author': 'Mohamed Amine SAYAGH',
            'Subject': 'Professional Resume',
            'Creator': 'ATS-Optimized Resume Generator'
        }

        
        # Render PDF with custom CSS
        html.write_pdf(output_pdf, stylesheets=[custom_css], metadata=metadata)
        
        print(f"PDF successfully created at: {output_pdf}")
        return output_pdf
    
    except Exception as e:
        logging.error(f"Error converting HTML to PDF: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Convert HTML file to ATS-friendly PDF')
    parser.add_argument('html_file', help='Path to the HTML file', default='resume.html')
    parser.add_argument('-o', '--output', help='Path to save the PDF file', default='resume.pdf')
    parser.add_argument('--no-optimize', action='store_true', help='Disable ATS optimization', default=True)
    
    args = parser.parse_args()
    
    try:
        convert_html_to_pdf(
            args.html_file, 
            args.output, 
            optimize_for_ats=True
        )
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
    