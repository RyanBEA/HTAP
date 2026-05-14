"""
Simple search for HTAP options using pandas
Optimized for 769 option choices - fast enough without complex indexing
"""

import pandas as pd
from typing import List, Optional

from src.models.option import OptionsDatabase


class OptionsSearch:
    """
    Simple search using pandas DataFrame
    Fast enough for 769 items (<10ms queries)
    """

    def __init__(self, options_db: OptionsDatabase):
        """
        Initialize search with options database

        Args:
            options_db: OptionsDatabase to search
        """
        self.options_db = options_db

        # Flatten to DataFrame for fast filtering
        rows = []
        for cat_name, category in options_db.categories.items():
            for choice_name, choice in category.options.items():
                rows.append({
                    'category': cat_name,
                    'choice': choice_name,
                    'structure': category.structure,
                    'costed': category.costed,
                    'tags': '|'.join(choice.tags) if choice.tags else '',
                    'has_costs': bool(choice.costs and choice.costs.components),
                    'has_custom_costs': bool(choice.costs and choice.costs.custom_costs),
                    'description': choice.description or '',
                    'choice_obj': choice,
                    'category_obj': category
                })

        self.df = pd.DataFrame(rows)

    def search(
        self,
        query: str = "",
        categories: Optional[List[str]] = None,
        require_costs: Optional[bool] = None,
        structure: Optional[str] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Search options with filters

        Args:
            query: Search term (searches in choice name, tags, description)
            categories: Filter by category names (e.g., ["Opt-Windows"])
            require_costs: Filter by cost presence (True/False/None)
            structure: Filter by structure type ("flat"/"tree"/None)
            limit: Maximum results to return

        Returns:
            DataFrame with matching options
        """
        df = self.df.copy()

        # Text search across name, tags, description
        if query:
            query_lower = query.lower()
            mask = (
                df['choice'].str.lower().str.contains(query_lower, na=False) |
                df['tags'].str.lower().str.contains(query_lower, na=False) |
                df['description'].str.lower().str.contains(query_lower, na=False)
            )
            df = df[mask]

        # Category filter
        if categories:
            df = df[df['category'].isin(categories)]

        # Cost filter
        if require_costs is not None:
            df = df[df['has_costs'] == require_costs]

        # Structure filter
        if structure:
            df = df[df['structure'] == structure]

        # Limit results
        return df.head(limit)

    def get_all_categories(self) -> List[str]:
        """Get list of all category names"""
        return sorted(self.df['category'].unique().tolist())

    def get_all_tags(self) -> List[str]:
        """Get list of all unique tags"""
        all_tags = set()
        for tags_str in self.df['tags']:
            if tags_str:
                all_tags.update(tags_str.split('|'))
        return sorted(all_tags)

    def get_category_stats(self) -> pd.DataFrame:
        """
        Get statistics per category

        Returns:
            DataFrame with columns: category, total_choices, choices_with_costs,
                                    structure, costed
        """
        return self.df.groupby('category').agg({
            'choice': 'count',
            'has_costs': 'sum',
            'structure': 'first',
            'costed': 'first'
        }).rename(columns={
            'choice': 'total_choices',
            'has_costs': 'choices_with_costs'
        }).reset_index()

    def count(self, **kwargs) -> int:
        """
        Count matching results without returning data

        Args:
            **kwargs: Same as search() method

        Returns:
            Number of matching options
        """
        return len(self.search(**kwargs))
