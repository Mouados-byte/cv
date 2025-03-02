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
    
    # Add a special style for ATS optimization
    style_tag = soup.new_tag('style')
    style_tag.string = """
        /* ATS Optimization Styles */
        [data-ats-section] {
            margin-bottom: 1em;
        }
        [data-ats-heading] {
            font-weight: bold;
            margin-bottom: 0.5em;
        }
        [data-ats-item] {
            margin-bottom: 0.2em;
        }
    """
    if soup.head:
        soup.head.append(style_tag)
    
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
        
        # Configure fonts
        font_config = FontConfiguration()
        
        # Define custom CSS for better PDF rendering
        custom_css = CSS(string='''
            @page {
                margin: 1cm;
                size: letter;
                @top-center {
                    content: "";
                }
                @bottom-center {
                    content: counter(page);
                }
            }
            body {
                font-size: 11pt;
                line-height: 1.4;
                font-family: "Helvetica", "Arial", sans-serif;
            }
            h1, h2, h3, h4, h5, h6 {
                margin-top: 0.5em;
                margin-bottom: 0.3em;
                page-break-after: avoid;
            }
            section {
                margin-bottom: 1em;
                page-break-inside: avoid;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                page-break-inside: auto;
            }
            tr {
                page-break-inside: avoid;
                page-break-after: auto;
            }
            /* Ensure print compatibility */
            @media print {
                a {
                    color: black !important;
                    text-decoration: none;
                }
                img, svg {
                    max-width: 100% !important;
                }
            }
        ''', font_config=font_config)
        
        # Create HTML object
        html = HTML(string=html_content)
        
        # Render PDF with custom CSS
        html.write_pdf(output_pdf)
        
        print(f"PDF successfully created at: {output_pdf}")
        return output_pdf
    
    except Exception as e:
        logging.error(f"Error converting HTML to PDF: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Convert HTML file to ATS-friendly PDF')
    parser.add_argument('html_file', help='Path to the HTML file')
    parser.add_argument('-o', '--output', help='Path to save the PDF file')
    parser.add_argument('--no-optimize', action='store_true', help='Disable ATS optimization')
    
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
    