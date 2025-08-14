#!/usr/bin/env python3
"""
AO3 Terminal Reader - Read Archive of Our Own fanfiction from the command line
With pager support, customizable columns, and proper paragraph formatting
"""

import requests
from bs4 import BeautifulSoup
import time
import sys
import argparse
from urllib.parse import urljoin, quote
import textwrap
import os
import subprocess
import tempfile
import re

class AO3Reader:
    def __init__(self, columns=None):
        self.base_url = "https://archiveofourown.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        # Handle adult content by default
        self.session.cookies.set('view_adult', 'true', domain='archiveofourown.org')
        
        # Set terminal width
        if columns:
            self.terminal_width = columns
        else:
            try:
                self.terminal_width = os.get_terminal_size().columns
            except:
                self.terminal_width = 80
    
    def verify_adult_content(self, url):
        """Handle age verification if needed"""
        try:
            response = self.session.get(url)
            
            # Check if we hit age verification page
            if "This work could have adult content" in response.text:
                # Find the form and submit it
                soup = BeautifulSoup(response.text, 'html.parser')
                form = soup.find('form')
                if form:
                    form_url = urljoin(url, form.get('action', ''))
                    # Submit age verification
                    verify_data = {'view_adult': 'true'}
                    response = self.session.post(form_url, data=verify_data)
                    
                    # Try the original URL again
                    response = self.session.get(url)
            
            return response
        except requests.RequestException as e:
            print(f"Error accessing content: {e}")
            return None
    
    def search_fics(self, query, sort="kudos", page=1, rating=None):
        """Search for fanfiction on AO3 with better filtering"""
        search_url = f"{self.base_url}/works/search"
        params = {
            'work_search[query]': query,
            'work_search[sort_column]': sort,
            'work_search[complete]': '',  # Both complete and incomplete
            'page': page
        }
        
        # Add rating filter if specified
        if rating:
            params['work_search[rating_ids][]'] = rating
        
        try:
            response = self.session.get(search_url, params=params)
            response.raise_for_status()
            return self.parse_search_results(response.text)
        except requests.RequestException as e:
            print(f"Error fetching search results: {e}")
            return []
    
    def parse_search_results(self, html):
        """Parse search results from AO3 HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        works = []
        
        work_items = soup.find_all('li', class_='work')
        
        for item in work_items:
            try:
                # Extract work information
                heading = item.find('h4', class_='heading')
                if not heading:
                    continue
                
                title_link = heading.find('a')
                title = title_link.get_text().strip() if title_link else "Unknown Title"
                work_url = urljoin(self.base_url, title_link['href']) if title_link else ""
                
                # Author
                author_links = heading.find_all('a', rel='author')
                authors = [a.get_text().strip() for a in author_links] if author_links else ["Unknown Author"]
                
                # Fandoms
                fandom_tags = item.find('h5', class_='fandoms')
                fandoms = [a.get_text().strip() for a in fandom_tags.find_all('a')] if fandom_tags else []
                
                # Rating and warnings
                required_tags = item.find('ul', class_='required-tags')
                rating = "Not Rated"
                warnings = []
                if required_tags:
                    rating_span = required_tags.find('span', class_='rating')
                    if rating_span:
                        rating = rating_span.get('title', 'Not Rated')
                    
                    warning_spans = required_tags.find_all('span', class_='warnings')
                    warnings = [w.get('title', '') for w in warning_spans if w.get('title')]
                
                # Stats
                stats = item.find('dl', class_='stats')
                kudos = words = chapters = hits = "N/A"
                if stats:
                    kudos_dd = stats.find('dd', class_='kudos')
                    kudos = kudos_dd.get_text().strip() if kudos_dd else "N/A"
                    
                    words_dd = stats.find('dd', class_='words')
                    words = words_dd.get_text().strip() if words_dd else "N/A"
                    
                    chapters_dd = stats.find('dd', class_='chapters')
                    chapters = chapters_dd.get_text().strip() if chapters_dd else "N/A"
                    
                    hits_dd = stats.find('dd', class_='hits')
                    hits = hits_dd.get_text().strip() if hits_dd else "N/A"
                
                # Summary
                summary_block = item.find('blockquote', class_='userstuff')
                summary = summary_block.get_text().strip()[:150] + "..." if summary_block else ""
                
                # Tags
                tag_list = item.find('ul', class_='tags')
                tags = []
                if tag_list:
                    tag_links = tag_list.find_all('a', class_='tag')
                    tags = [tag.get_text().strip() for tag in tag_links[:5]]  # Limit to 5 tags
                
                works.append({
                    'title': title,
                    'authors': authors,
                    'fandoms': fandoms,
                    'rating': rating,
                    'warnings': warnings,
                    'kudos': kudos,
                    'words': words,
                    'chapters': chapters,
                    'hits': hits,
                    'summary': summary,
                    'tags': tags,
                    'url': work_url
                })
            except Exception as e:
                continue
        
        return works
    
    def display_works(self, works):
        """Display works in a clean, readable format"""
        if not works:
            print("No works found.")
            return
        
        separator = "=" * self.terminal_width
        
        print(f"\n{separator}")
        print(f"Found {len(works)} works:")
        print(f"{separator}")
        
        for i, work in enumerate(works, 1):
            print(f"\n{i}. {work['title']}")
            print(f"   By: {', '.join(work['authors'])}")
            
            if work['fandoms']:
                fandoms_text = ', '.join(work['fandoms'][:2])  # Limit fandoms display
                if len(work['fandoms']) > 2:
                    fandoms_text += f" (+{len(work['fandoms'])-2} more)"
                print(f"   Fandom: {fandoms_text}")
            
            print(f"   Rating: {work['rating']}")
            if work['warnings']:
                print(f"   Warnings: {', '.join(work['warnings'])}")
            
            stats_line = f"   📊 {work['kudos']} kudos | {work['words']} words | {work['chapters']} chapters | {work['hits']} hits"
            print(stats_line)
            
            if work['tags']:
                tags_text = ', '.join(work['tags'])
                print(f"   Tags: {tags_text}")
            
            if work['summary']:
                # Wrap summary text nicely using full terminal width
                summary_wrapped = textwrap.fill(work['summary'], width=self.terminal_width-6, 
                                              initial_indent='   📖 ', subsequent_indent='      ')
                print(summary_wrapped)
            
            print(f"   🔗 {work['url']}")
            print(f"   {'-'*self.terminal_width}")
    
    def format_content_for_pager(self, title, author, chapter_text, chapter=1, total_chapters=1):
        """Format content with proper paragraph handling and line breaks"""
        separator = "=" * self.terminal_width
        
        # Header
        formatted_text = f"{separator}\n"
        formatted_text += f"📚 {title}\n"
        formatted_text += f"✍️  By {author}\n"
        if total_chapters > 1:
            formatted_text += f"📖 Chapter {chapter} of {total_chapters}\n"
        formatted_text += f"{separator}\n\n"
        
        # Process content with proper paragraph breaks
        if chapter_text:
            # Split by multiple line breaks to preserve paragraph structure
            paragraphs = re.split(r'\n\s*\n', chapter_text.strip())
            
            for paragraph in paragraphs:
                if paragraph.strip():
                    # Clean up individual lines within paragraph
                    lines = [line.strip() for line in paragraph.split('\n') if line.strip()]
                    paragraph_text = ' '.join(lines)
                    
                    # Wrap the paragraph using full terminal width with some padding
                    wrapped = textwrap.fill(paragraph_text, width=self.terminal_width-4)
                    formatted_text += wrapped + "\n\n"
        
        # Footer with navigation info
        if total_chapters > 1:
            formatted_text += f"\n{separator}\n"
            if chapter < total_chapters:
                formatted_text += f"📄 Use --chapter {chapter + 1} to read next chapter\n"
            if chapter > 1:
                formatted_text += f"📄 Use --chapter {chapter - 1} to read previous chapter\n"
            formatted_text += f"{separator}\n"
        
        return formatted_text
    
    def use_pager(self, text):
        """Display text using system pager (like less) with arrow key navigation"""
        try:
            # Try to use less first (best experience)
            pager_cmd = None
            
            # Check for less
            if subprocess.run(['which', 'less'], capture_output=True).returncode == 0:
                pager_cmd = ['less', '-R', '-S', '-F', '-X']
            # Check for more
            elif subprocess.run(['which', 'more'], capture_output=True).returncode == 0:
                pager_cmd = ['more']
            # Check for cat with paging (fallback)
            else:
                # Fallback: just print with manual paging
                self.manual_pager(text)
                return
            
            # Use system pager
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
                tmp_file.write(text)
                tmp_file_path = tmp_file.name
            
            try:
                subprocess.run(pager_cmd + [tmp_file_path])
            finally:
                os.unlink(tmp_file_path)
                
        except Exception as e:
            print(f"Error using pager: {e}")
            self.manual_pager(text)
    
    def manual_pager(self, text):
        """Manual pager implementation as fallback"""
        lines = text.split('\n')
        terminal_height = 25  # Conservative default
        
        try:
            terminal_height = os.get_terminal_size().lines - 2
        except:
            pass
        
        current_line = 0
        
        while current_line < len(lines):
            # Display current page
            end_line = min(current_line + terminal_height, len(lines))
            for i in range(current_line, end_line):
                print(lines[i])
            
            if end_line >= len(lines):
                print("\n[End of content - Press 'q' to quit]")
                input()
                break
            
            # Show pager prompt
            try:
                response = input(f"\n[Line {current_line+1}-{end_line} of {len(lines)} - Press ENTER for next page, 'b' for back, 'q' to quit]: ")
                if response.lower() == 'q':
                    break
                elif response.lower() == 'b':
                    current_line = max(0, current_line - terminal_height)
                else:
                    current_line = end_line
            except KeyboardInterrupt:
                break
    
    def read_work(self, work_url, chapter=1, use_pager=True):
        """Read a work with full adult content support and pager"""
        try:
            # Handle potential age verification
            response = self.verify_adult_content(work_url)
            if not response:
                return
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Work metadata
            title_elem = soup.find('h2', class_='title')
            title = title_elem.get_text().strip() if title_elem else "Unknown Title"
            
            author_elem = soup.find('a', rel='author')
            author = author_elem.get_text().strip() if author_elem else "Unknown Author"
            
            # Chapter navigation
            chapter_nav = soup.find('ol', class_='chapter')
            total_chapters = 1
            if chapter_nav:
                chapters = chapter_nav.find_all('li')
                total_chapters = len(chapters)
            
            # Chapter content
            chapter_content = soup.find('div', class_='userstuff')
            chapter_text = ""
            
            if chapter_content:
                # Clean up the content but preserve structure
                for elem in chapter_content(['script', 'style']):
                    elem.decompose()
                
                # Get text with better formatting
                # Replace <p> tags with double newlines to preserve paragraphs
                for p in chapter_content.find_all('p'):
                    p.insert_after('\n\n')
                
                # Replace <br> tags with newlines
                for br in chapter_content.find_all('br'):
                    br.replace_with('\n')
                
                # Replace <hr> tags with separator
                for hr in chapter_content.find_all('hr'):
                    hr.replace_with('\n' + '-' * 40 + '\n')
                
                chapter_text = chapter_content.get_text()
            
            # Format content for display
            formatted_content = self.format_content_for_pager(
                title, author, chapter_text, chapter, total_chapters
            )
            
            if use_pager:
                self.use_pager(formatted_content)
            else:
                print(formatted_content)
                
        except Exception as e:
            print(f"Error reading work: {e}")

def main():
    parser = argparse.ArgumentParser(description='Read AO3 fanfiction from terminal with pager support')
    parser.add_argument('query', nargs='?', help='Search query for fanfiction')
    parser.add_argument('--sort', choices=['kudos', 'hits', 'bookmarks', 'comments', 'word_count', 'created_at', 'revised_at'], 
                       default='kudos', help='Sort results by (default: kudos)')
    parser.add_argument('--page', type=int, default=1, help='Page number (default: 1)')
    parser.add_argument('--read', type=int, help='Read work number from search results')
    parser.add_argument('--url', help='Read work directly from URL')
    parser.add_argument('--chapter', type=int, default=1, help='Chapter number to read (default: 1)')
    parser.add_argument('--rating', choices=['General Audiences', 'Teen And Up Audiences', 'Mature', 'Explicit'], 
                       help='Filter by rating')
    parser.add_argument('--columns', type=int, help='Set terminal width in columns (default: auto-detect)')
    parser.add_argument('--no-pager', action='store_true', help='Disable pager and print directly')
    
    args = parser.parse_args()
    
    reader = AO3Reader(columns=args.columns)
    
    # Direct URL reading
    if args.url:
        print(f"Reading work from URL...")
        reader.read_work(args.url, args.chapter, use_pager=not args.no_pager)
        return
    
    # Search mode
    if not args.query:
        print("Please provide a search query or use --url to read directly")
        print("\nUsage examples:")
        print("  python ao3_reader.py 'coffee shop au' --columns 100")
        print("  python ao3_reader.py 'sherlock holmes' --read 1 --no-pager")
        print("  python ao3_reader.py --url 'https://archiveofourown.org/works/12345' --chapter 2")
        return
    
    print(f"🔍 Searching AO3 for: '{args.query}'")
    if args.rating:
        print(f"📊 Filtering by rating: {args.rating}")
    if args.columns:
        print(f"📐 Using {args.columns} columns")
    print("Please wait...")
    
    works = reader.search_fics(args.query, args.sort, args.page, args.rating)
    reader.display_works(works)
    
    # Direct read from search results
    if args.read and 1 <= args.read <= len(works):
        work = works[args.read - 1]
        print(f"\n📖 Reading: {work['title']}")
        reader.read_work(work['url'], args.chapter, use_pager=not args.no_pager)
        return
    
    # Interactive mode
    if works:
        print(f"\n📚 Commands:")
        print(f"  1-{len(works)}: Read work")
        print(f"  n: Next page")
        print(f"  q: Quit")
        
        while True:
            try:
                choice = input("> ").strip().lower()
                if choice == 'q':
                    break
                elif choice == 'n':
                    # Next page
                    works = reader.search_fics(args.query, args.sort, args.page + 1, args.rating)
                    args.page += 1
                    reader.display_works(works)
                    print(f"\nPage {args.page} - Commands: 1-{len(works)} (read), n (next page), q (quit):")
                else:
                    num = int(choice)
                    if 1 <= num <= len(works):
                        work = works[num - 1]
                        print(f"\n📖 Reading: {work['title']}")
                        reader.read_work(work['url'], args.chapter, use_pager=not args.no_pager)
                        print(f"\nCommands: 1-{len(works)} (read), n (next page), q (quit):")
                    else:
                        print(f"Please enter a number between 1 and {len(works)}, 'n' for next page, or 'q' to quit.")
                        
            except (ValueError, KeyboardInterrupt):
                break

if __name__ == "__main__":
    main()
