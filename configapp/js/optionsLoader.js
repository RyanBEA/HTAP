/**
 * OptionsLoader - Loads and parses HTAP-options.json
 */
class OptionsLoader {
    constructor() {
        this.optionsData = null;
        this.categories = [];
    }

    /**
     * Load HTAP-options.json from the data directory
     */
    async load() {
        try {
            const response = await fetch('data/HTAP-options.json');
            if (!response.ok) {
                throw new Error(`Failed to load options file: ${response.statusText}`);
            }

            this.optionsData = await response.json();
            this.parseCategories();
            return true;
        } catch (error) {
            console.error('Error loading HTAP options:', error);
            throw error;
        }
    }

    /**
     * Parse categories from loaded options data
     */
    parseCategories() {
        this.categories = [];

        for (const [key, value] of Object.entries(this.optionsData)) {
            if (key.startsWith('Opt-')) {
                this.categories.push({
                    id: key,
                    name: key,
                    displayName: this.formatDisplayName(key),
                    structure: value.structure || 'flat',
                    costed: value.costed || false,
                    default: value.default || 'NA',
                    options: value.options || {}
                });
            }
        }

        // Sort categories alphabetically by display name
        this.categories.sort((a, b) => a.displayName.localeCompare(b.displayName));
    }

    /**
     * Format category name for display
     * e.g., "Opt-AboveGradeWall" -> "Above Grade Wall"
     */
    formatDisplayName(optName) {
        // Remove "Opt-" prefix
        let name = optName.replace('Opt-', '');

        // Split on capital letters and hyphens
        name = name.replace(/([A-Z])/g, ' $1').trim();
        name = name.replace(/-/g, ' ');

        return name;
    }

    /**
     * Get all categories
     */
    getCategories() {
        return this.categories;
    }

    /**
     * Get options for a specific category
     */
    getOptionsForCategory(categoryId) {
        const category = this.categories.find(cat => cat.id === categoryId);
        if (!category) {
            return [];
        }

        const options = [];
        for (const [optionName, optionData] of Object.entries(category.options)) {
            options.push({
                name: optionName,
                data: optionData,
                characteristics: optionData.characteristics || {},
                displayName: this.formatOptionDisplayName(optionName, optionData)
            });
        }

        return options;
    }

    /**
     * Format option name for display with characteristics
     */
    formatOptionDisplayName(optionName, optionData) {
        if (optionName === 'NA') {
            return 'NA (No modification)';
        }

        let display = optionName;

        // Add characteristics if available
        if (optionData.characteristics) {
            const chars = optionData.characteristics;
            const details = [];

            if (chars['u-value']) {
                details.push(`U=${chars['u-value']}`);
            }
            if (chars.panes) {
                details.push(`${chars.panes} panes`);
            }
            if (chars.fill) {
                details.push(`Fill: ${chars.fill}`);
            }
            if (chars.coat) {
                details.push(`Coat: ${chars.coat}`);
            }

            if (details.length > 0) {
                display += ` (${details.join(', ')})`;
            }
        }

        return display;
    }

    /**
     * Get locations from Opt-Location category
     */
    getLocations() {
        const locationCategory = this.categories.find(cat => cat.id === 'Opt-Location');
        if (!locationCategory) {
            return [];
        }

        const locations = [];
        for (const locationName of Object.keys(locationCategory.options)) {
            if (locationName !== 'NA') {
                locations.push(locationName);
            }
        }

        return locations.sort();
    }

    /**
     * Search options by keyword
     */
    searchOptions(categoryId, searchTerm) {
        const options = this.getOptionsForCategory(categoryId);

        if (!searchTerm || searchTerm.trim() === '') {
            return options;
        }

        const term = searchTerm.toLowerCase();
        return options.filter(option => {
            return option.name.toLowerCase().includes(term) ||
                   option.displayName.toLowerCase().includes(term);
        });
    }
}
