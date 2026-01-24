#!/usr/bin/env python3
"""
Trakt Agent Interactive Setup Script
Guides users through configuration and first-time setup
"""

import json
import os
import sys
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")

def print_step(number, text):
    """Print a step number"""
    print(f"\n📍 Step {number}: {text}")
    print("-" * 60)

def create_directories():
    """Create necessary project directories"""
    print_step(1, "Creating Project Directories")
    
    directories = ["data", "output"]
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ Created: {dir_name}/")
    
    print("\n✓ All directories created successfully")

def configure_trakt_api():
    """Guide user through Trakt API setup"""
    print_step(2, "Trakt API Configuration")
    
    print("\n📝 To use this agent, you need Trakt API credentials.")
    print("   Follow these steps:\n")
    print("   1. Go to: https://trakt.tv/oauth/applications/new")
    print("   2. Create a new application with these settings:")
    print("      - Name: 'Trakt Agent' (or your choice)")
    print("      - Redirect URI: urn:ietf:wg:oauth:2.0:oob")
    print("   3. Copy your Client ID and Client Secret\n")
    
    input("Press Enter when you have your credentials ready...")
    
    client_id = input("\n🔑 Enter your Client ID: ").strip()
    client_secret = input("🔑 Enter your Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("\n❌ Error: Both Client ID and Secret are required")
        sys.exit(1)
    
    # Save to secrets.json
    secrets = {
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    with open("secrets.json", "w") as f:
        json.dump(secrets, f, indent=2)
    
    print("\n✅ Saved credentials to secrets.json")
    print("\n📝 Next, you need to authenticate with Trakt:")
    print("   Run: python scripts/exchange_pin.py")
    print("   This will guide you through OAuth authentication\n")

def configure_preferences():
    """Help user configure preferences.json"""
    print_step(3, "Configure Your Preferences")
    
    print("\n📝 Let's set up your content preferences.\n")
    
    # Check if preferences.json exists
    if Path("preferences.json").exists():
        print("⚠️  preferences.json already exists.")
        overwrite = input("   Do you want to reconfigure? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("✓ Keeping existing preferences")
            return
    
    print("\n🎬 What genres do you enjoy? (comma-separated)")
    print("   Examples: sci-fi, fantasy, thriller, action, comedy")
    preferred = input("   Your preferences: ").strip()
    preferred_genres = [g.strip() for g in preferred.split(",") if g.strip()]
    
    print("\n🚫 What genres do you want to exclude? (comma-separated)")
    print("   Examples: horror, romance, documentary, sports")
    excluded = input("   Exclusions: ").strip()
    excluded_genres = [g.strip() for g in excluded.split(",") if g.strip()]
    
    print("\n📅 Minimum release year for recommendations?")
    min_year = input("   (default: 2005): ").strip()
    min_year = int(min_year) if min_year.isdigit() else 2005
    
    print("\n⭐ Minimum IMDb score for movies?")
    min_movie_score = input("   (default: 7.0): ").strip()
    min_movie_score = float(min_movie_score) if min_movie_score else 7.0
    
    print("\n⭐ Minimum IMDb score for TV shows?")
    min_tv_score = input("   (default: 6.5): ").strip()
    min_tv_score = float(min_tv_score) if min_tv_score else 6.5
    
    # Create preferences
    preferences = {
        "preferred_genres": preferred_genres or[],
        "genre_exclusions": excluded_genres or [],
        "language_exclusions": [],
        "title_blocklist": [],
        "min_year": min_year, 
        "min_imdb_score": {
            "tv_shows": min_tv_score,
            "movies": min_movie_score
        },
        "themes": [],
        "notes": "Edit this file to customize your preferences further (themes, language exclusions, etc.)"
    }
    
    with open("preferences.json", "w") as f:
        json.dump(preferences, f, indent=2)
    
    print("\n✅ Saved preferences to preferences.json")
    print("   You can edit this file anytime to adjust your preferences")

def validate_setup():
    """Validate that all necessary files exist"""
    print_step(4, "Validating Setup")
    
    required_files = {
        "secrets.json": "Trakt API credentials",
        "preferences.json": "Your content preferences",
        "requirements.txt": "Python dependencies"
    }
    
    all_valid = True
    for file, description in required_files.items():
        if Path(file).exists():
            print(f"✅ {file} - {description}")
        else:
            print(f"❌ {file} - Missing!")
            all_valid = False
    
    if not all_valid:
        print("\n⚠️  Some required files are missing.")
        print("   Please complete the setup steps above.")
        return False
    
    print("\n✓ All required files present")
    return True

def show_next_steps():
    """Show user what to do next"""
    print_header("Setup Complete!")
    
    print("🎉 Your Trakt Agent is ready to use!\n")
    print("Next steps:\n")
    print("  1. Authenticate with Trakt (if you haven't already):")
    print("     python scripts/exchange_pin.py\n")
    print("  2. Get your first recommendations:")
    print("     python cli.py recommend\n")
    print("  3. Mark items as watched:")
    print("     python cli.py mark \"Movie Title (Year)\"\n")
    print("  4. View all commands:")
    print("     python cli.py --help\n")
    print("📚 For more help, see README.md\n")

def main():
    """Main setup flow"""
    print_header("🎬 Trakt Agent Setup")
    
    print("This interactive script will help you set up the Trakt Agent.\n")
    print("You'll configure:")
    print("  • Trakt API credentials")
    print("  • Content preferences")
    print("  • Project directories\n")
    
    input("Press Enter to begin...")
    
    try:
        create_directories()
        configure_trakt_api()
        configure_preferences()
        
        if validate_setup():
            show_next_steps()
        else:
            print("\n❌ Setup incomplete. Please address the issues above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
