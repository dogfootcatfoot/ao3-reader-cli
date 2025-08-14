# 📚 Terminal Fiction Readers

> pure-vibe-coding-with-claude. just read ao3, in your work place or somewhere else. it could be seem like hacker, maybe?

Look like you're doing important terminal work while secretly reading fanfiction and web novels. Because sometimes you need a good enemies-to-lovers fic but your boss is walking around. 👀

## What This Is

Two Python scripts that let you browse and read stories from:
- **AO3 (Archive of Our Own)** - All your favorite fanfiction

Everything runs in your terminal, so it looks like you're doing serious coding stuff. Perfect stealth mode for workplace fiction consumption.

## Features That Make You Look Professional™

✨ **Pager Support** - Navigate with arrow keys like you're reading man pages  
✨ **Custom Width** - Set your terminal to any width (make it look even more technical)  
✨ **Adult Content Handling** - Automatically handles age verification (you're welcome)  
✨ **Clean Text Formatting** - Proper paragraph breaks, no weird HTML artifacts  
✨ **Interactive Browsing** - Page through results seamlessly  
✨ **Search & Filter** - Find exactly what you want to read  

## Quick Start

### Install Dependencies
```bash
pip install requests beautifulsoup4
```

### Basic Usage

#### AO3 Reader
```bash
# Search and browse
python ao3_reader.py "coffee shop au"

# Read specific result
python ao3_reader.py "hurt comfort" --read 1

# Custom terminal width (for that extra professional look)
python ao3_reader.py "enemies to lovers" --columns 120

# Read directly from URL
python ao3_reader.py --url "https://archiveofourown.org/works/12345"
```

## Advanced Stealth Mode

### Make It Look Extra Technical
```bash
# Wide terminal = more professional
python ao3_reader.py "your search" --columns 150

# Disable pager for quick reading
python ao3_reader.py "your search" --no-pager --read 1

# Filter by rating (keep it workplace appropriate)
python ao3_reader.py "fluff" --rating "General Audiences"
```

### Pro Tips for Workplace Reading
- Use `--columns 120` or higher - makes it look like you're reading documentation
- The pager controls work like `less` command - very programmer-y
- Search results look like API responses or log files
- Use specific searches to find exactly what you want quickly

## Commands You'll Actually Use

### AO3 Reader Options
```
--sort          Sort by kudos, hits, bookmarks, etc.
--rating        Filter by content rating
--columns       Set terminal width (default: auto)
--no-pager      Print directly instead of using pager
--read N        Jump straight to reading result #N
--chapter N     Read specific chapter
```

## Pager Controls (When Reading)

Once you're reading a story, you get full navigation:
- **Arrow keys** - Scroll up/down
- **Space** - Next page
- **b** - Previous page
- **/** - Search within text
- **q** - Quit reading

Just like reading actual documentation. Very convincing.

## Examples for Different Moods

### When You Need Fluff
```bash
python ao3_reader.py "domestic fluff" --rating "General Audiences" --read 1
```

### When You Want Drama
```bash
python ao3_reader.py "angst with a happy ending" --sort kudos
```

### When Boss Is Nearby
```bash
python ao3_reader.py "your search" --columns 150 --no-pager
# Looks like you're debugging something important
```

## Troubleshooting

**"Width not working"** - Make sure you're using `--columns` with a number

## The Vibe

This is for when you want to read good stories but need to maintain your professional developer aesthetic. Terminal-based reading hits different - it's focused, distraction-free, and looks important.

Perfect for:
- Long lunch breaks
- Slow work days  
- When you finish your tasks early
- Weekend coding sessions (but make it fiction)

## Legal Stuff

These scripts just fetch publicly available content. Don't abuse the servers, be respectful, and maybe actually do some work too. 😉

---

### Note
* English is not my mother tongue, please excuse about grammar mistakes or awkward expressions.
* If you like this project, mail to me and recommend your favorite fics. XOXO 💌
