#!/usr/bin/env python3
"""
Unit Tests for Trakt Agent Core Functions

Tests basic functionality without requiring API access.
"""
import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import modules under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import BASE_DIR, DATA_DIR


class TestConfig:
    """Test configuration module."""
    
    def test_base_dir_exists(self):
        """BASE_DIR should point to the project root."""
        assert BASE_DIR.exists()
        assert (BASE_DIR / "config.py").exists()
    
    def test_data_dir_exists(self):
        """DATA_DIR should exist or be creatable."""
        assert DATA_DIR.exists()


class TestRecommendFiltering:
    """Test candidate filtering logic."""
    
    def test_get_title_year_movie(self):
        """Test extracting title/year from movie item."""
        from core.recommend import get_title_year
        
        item = {"movie": {"title": "Test Movie", "year": 2025}}
        assert get_title_year(item) == "Test Movie (2025)"
    
    def test_get_title_year_show(self):
        """Test extracting title/year from show item."""
        from core.recommend import get_title_year
        
        item = {"show": {"title": "Test Show", "year": 2024}}
        assert get_title_year(item) == "Test Show (2024)"
    
    def test_get_trakt_id_movie(self):
        """Test extracting Trakt ID from movie."""
        from core.recommend import get_trakt_id
        
        item = {"movie": {"ids": {"trakt": 12345}}}
        assert get_trakt_id(item) == 12345
    
    def test_get_trakt_id_show(self):
        """Test extracting Trakt ID from show."""
        from core.recommend import get_trakt_id
        
        item = {"show": {"ids": {"trakt": 67890}}}
        assert get_trakt_id(item) == 67890
    
    def test_get_genres_movie(self):
        """Test extracting genres from movie."""
        from core.recommend import get_genres
        
        item = {"movie": {"genres": ["action", "sci-fi"]}}
        assert get_genres(item) == ["action", "sci-fi"]
    
    def test_get_genres_show(self):
        """Test extracting genres from show."""
        from core.recommend import get_genres
        
        item = {"show": {"genres": ["drama", "thriller"]}}
        assert get_genres(item) == ["drama", "thriller"]
    
    def test_filter_candidates_removes_watched(self):
        """Test that watched items are filtered out."""
        from core.recommend import filter_candidates
        
        candidates = [
            {"movie": {"title": "Watched", "year": 2025, "ids": {"trakt": 1}, "genres": []}},
            {"movie": {"title": "Not Watched", "year": 2025, "ids": {"trakt": 2}, "genres": []}}
        ]
        watched_ids = {1}
        
        result = filter_candidates(candidates, watched_ids)
        assert len(result) == 1
        assert "Not Watched" in result[0]
    
    def test_filter_candidates_removes_excluded_genres(self):
        """Test that excluded genres are filtered out."""
        from core.recommend import filter_candidates
        
        candidates = [
            {"movie": {"title": "Horror Movie", "year": 2025, "ids": {"trakt": 1}, "genres": ["horror"]}},
            {"movie": {"title": "Action Movie", "year": 2025, "ids": {"trakt": 2}, "genres": ["action"]}}
        ]
        watched_ids = set()
        exclusions = ["horror"]
        
        result = filter_candidates(candidates, watched_ids, exclusions)
        assert len(result) == 1
        assert "Action Movie" in result[0]
    
    def test_filter_candidates_removes_blocklisted_titles(self):
        """Test that blocklisted titles are filtered out."""
        from core.recommend import filter_candidates
        
        candidates = [
            {"movie": {"title": "Wicked", "year": 2025, "ids": {"trakt": 1}, "genres": ["fantasy"]}},
            {"movie": {"title": "Good Movie", "year": 2025, "ids": {"trakt": 2}, "genres": ["fantasy"]}}
        ]
        watched_ids = set()
        exclusions = []
        blocklist = ["Wicked"]
        
        result = filter_candidates(candidates, watched_ids, exclusions, blocklist)
        assert len(result) == 1
        assert "Good Movie" in result[0]


class TestProfileStatistics:
    """Test taste profile statistics calculation."""
    
    def test_calculate_statistics_basic(self):
        """Test basic statistics calculation."""
        from core.profile_taste import calculate_statistics
        
        history = [
            {"movie": {"title": "Movie 1", "year": 2020, "ids": {"trakt": 1}}},
            {"movie": {"title": "Movie 2", "year": 2021, "ids": {"trakt": 2}}},
            {"show": {"title": "Show 1", "year": 2022, "ids": {"trakt": 3}}, "episode": {"season": 1, "number": 1}}
        ]
        
        stats = calculate_statistics(history)
        
        assert stats["total_items"] == 3
        assert stats["movies"] == 2
        assert stats["tv_episodes"] == 1
        assert stats["unique_shows"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
