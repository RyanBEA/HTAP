/**
 * Main Application Controller
 */
class HTAPConfigApp {
    constructor() {
        this.optionsLoader = new OptionsLoader();
        this.runFileParser = new RunFileParser();
        this.simCalculator = new SimCalculator();

        this.currentPanel = null;
        this.currentCategory = null;
        this.optionsModified = false;  // Track if options have been modified

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', () => this.init());
    }

    /**
     * Initialize the application
     */
    async init() {
        try {
            // Load HTAP options
            await this.optionsLoader.load();

            // Setup UI
            this.setupNavigation();
            this.setupEventListeners();
            this.populateLocations();

            // Show default panel
            this.showPanel('run-parameters');

            // Update status
            this.setStatus('Ready');

            // Load from localStorage if exists
            this.loadFromLocalStorage();

            // Update summary
            this.updateSummary();

        } catch (error) {
            this.setStatus(`Error: ${error.message}`, true);
            alert('Failed to load HTAP options. Please check that data/HTAP-options.json exists.');
        }
    }

    /**
     * Setup navigation items for Opt-* categories
     */
    setupNavigation() {
        const upgradesNav = document.getElementById('upgrades-nav');
        const categories = this.optionsLoader.getCategories();

        categories.forEach(category => {
            const navItem = document.createElement('div');
            navItem.className = 'nav-item';
            navItem.dataset.section = category.id;

            navItem.innerHTML = `
                <span class="nav-icon">○</span>
                <span class="nav-label">${category.displayName}</span>
                <span class="nav-badge" id="nav-badge-${category.id}"></span>
            `;

            navItem.addEventListener('click', () => this.showUpgradePanel(category.id));
            upgradesNav.appendChild(navItem);
        });
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Navigation items
        document.querySelectorAll('.nav-item').forEach(item => {
            if (!item.dataset.section) return;

            item.addEventListener('click', () => {
                const section = item.dataset.section;

                if (this.optionsLoader.getCategories().find(cat => cat.id === section)) {
                    this.showUpgradePanel(section);
                } else {
                    this.showPanel(section);
                }
            });
        });

        // Header buttons
        document.getElementById('btn-new').addEventListener('click', () => this.newConfig());
        document.getElementById('btn-open').addEventListener('click', () => this.openFile());
        document.getElementById('btn-save').addEventListener('click', () => this.exportRunFile());
        document.getElementById('btn-export-bottom').addEventListener('click', () => this.exportRunFile());

        // Run parameters
        document.getElementById('run-mode').addEventListener('change', (e) => {
            this.runFileParser.config.runParameters.runMode = e.target.value;
            this.updateSummary();
            this.saveToLocalStorage();
        });

        document.getElementById('archetype-dir').addEventListener('input', (e) => {
            this.runFileParser.config.runParameters.archetypeDir = e.target.value;
            this.saveToLocalStorage();
        });

        document.getElementById('unit-costs-db').addEventListener('input', (e) => {
            this.runFileParser.config.runParameters.unitCostsDb = e.target.value;
            this.saveToLocalStorage();
        });

        document.getElementById('options-file').addEventListener('input', (e) => {
            this.runFileParser.config.runParameters.optionsFile = e.target.value;
            this.saveToLocalStorage();
        });

        // Archetypes
        document.getElementById('archetypes-input').addEventListener('input', (e) => {
            const text = e.target.value;
            const archetypes = text.split('\n').map(line => line.trim()).filter(line => line !== '');
            this.runFileParser.config.runScope.archetypes = archetypes;
            this.updateSummary();
            this.saveToLocalStorage();
        });

        // Rulesets
        document.getElementById('rulesets-input').addEventListener('input', (e) => {
            const value = e.target.value.trim();
            this.runFileParser.config.runScope.rulesets = value ? [value] : ['as-found'];
            this.updateSummary();
            this.saveToLocalStorage();
        });

        // File input
        document.getElementById('file-input').addEventListener('change', (e) => this.handleFileSelect(e));

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                this.exportRunFile();
            } else if (e.ctrlKey && e.key === 'o') {
                e.preventDefault();
                this.openFile();
            } else if (e.ctrlKey && e.key === 'n') {
                e.preventDefault();
                this.newConfig();
            }
        });
    }

    /**
     * Populate locations list
     */
    populateLocations() {
        const locations = this.optionsLoader.getLocations();
        const listContainer = document.getElementById('locations-list');
        const searchInput = document.getElementById('locations-search');

        const renderLocations = (filteredLocations) => {
            listContainer.innerHTML = '';

            filteredLocations.forEach(location => {
                const optionItem = document.createElement('div');
                optionItem.className = 'option-item';

                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.value = location;
                checkbox.id = `loc-${location}`;

                const selectedLocations = this.runFileParser.config.runScope.locations || [];
                checkbox.checked = selectedLocations.includes(location);

                checkbox.addEventListener('change', (e) => {
                    this.toggleLocation(location, e.target.checked);
                });

                const label = document.createElement('label');
                label.className = 'option-label';
                label.htmlFor = `loc-${location}`;
                label.innerHTML = `<div class="option-name">${location}</div>`;

                optionItem.appendChild(checkbox);
                optionItem.appendChild(label);
                listContainer.appendChild(optionItem);
            });
        };

        // Initial render
        renderLocations(locations);

        // Search functionality
        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            const filtered = locations.filter(loc => loc.toLowerCase().includes(searchTerm));
            renderLocations(filtered);
        });
    }

    /**
     * Toggle location selection
     */
    toggleLocation(location, checked) {
        let locations = this.runFileParser.config.runScope.locations || [];

        if (checked) {
            if (!locations.includes(location)) {
                locations.push(location);
            }
        } else {
            locations = locations.filter(loc => loc !== location);
        }

        this.runFileParser.config.runScope.locations = locations;
        this.updateSummary();
        this.saveToLocalStorage();
    }

    /**
     * Show a panel
     */
    showPanel(panelId) {
        // Hide all panels
        document.querySelectorAll('.panel-content').forEach(panel => {
            panel.style.display = 'none';
        });

        // Show selected panel
        const panel = document.getElementById(`panel-${panelId}`);
        if (panel) {
            panel.style.display = 'block';
            this.currentPanel = panelId;
        }

        // Update navigation active state
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.section === panelId) {
                item.classList.add('active');
            }
        });
    }

    /**
     * Show upgrade options panel for a category
     */
    showUpgradePanel(categoryId) {
        this.currentCategory = categoryId;

        const category = this.optionsLoader.getCategories().find(cat => cat.id === categoryId);
        if (!category) return;

        const options = this.optionsLoader.getOptionsForCategory(categoryId);
        const selectedOptions = this.runFileParser.getUpgradeOptions(categoryId);

        // Clone the template or use existing panel
        let panel = document.getElementById(`panel-${categoryId}`);

        if (!panel) {
            // Create panel from template
            panel = this.createUpgradePanel(categoryId, category, options);
        } else {
            // Re-render options for existing panel
            this.renderUpgradeOptions(panel, categoryId, options);
        }

        this.showPanel(categoryId);
    }

    /**
     * Create upgrade panel
     */
    createUpgradePanel(categoryId, category, options) {
        const centerPanel = document.querySelector('.center-panel');
        const panel = document.createElement('div');
        panel.id = `panel-${categoryId}`;
        panel.className = 'panel-content';
        panel.style.display = 'none';

        // Check if category should have "Add New Option" button
        const excludedCategories = [
            'Opt-Ruleset', 'Opt-DBFiles', 'Opt-ResultHouseCode',
            'Opt-Archetype', 'Opt-Location'
        ];
        const showAddButton = category.structure === 'tree' &&
                              !excludedCategories.includes(categoryId);

        panel.innerHTML = `
            <h2>${category.displayName}</h2>
            <div class="panel-actions">
                <button class="btn btn-sm btn-secondary btn-select-all">Select All</button>
                <button class="btn btn-sm btn-secondary btn-clear-all">Clear All</button>
                ${showAddButton ? '<button class="btn btn-sm btn-primary btn-add-option">+ Add New Option</button>' : ''}
            </div>
            <div class="search-box">
                <input type="text" class="form-control upgrade-search" placeholder="Search options...">
            </div>
            <div class="options-list upgrade-options-list"></div>
            <div class="selection-summary">
                <span class="upgrade-count">0 options selected</span>
            </div>
        `;

        centerPanel.appendChild(panel);

        // Setup event listeners for this panel
        this.setupUpgradePanelListeners(panel, categoryId, options);

        // Add "Add New Option" listener if button exists
        if (showAddButton) {
            panel.querySelector('.btn-add-option').addEventListener('click', () => {
                this.handleAddNewOption(categoryId);
            });
        }

        // Render options
        this.renderUpgradeOptions(panel, categoryId, options);

        return panel;
    }

    /**
     * Setup event listeners for upgrade panel
     */
    setupUpgradePanelListeners(panel, categoryId, allOptions) {
        // Select All button
        panel.querySelector('.btn-select-all').addEventListener('click', () => {
            const checkboxes = panel.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(cb => cb.checked = true);
            this.updateUpgradeSelection(categoryId, panel);
        });

        // Clear All button
        panel.querySelector('.btn-clear-all').addEventListener('click', () => {
            const checkboxes = panel.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(cb => cb.checked = false);
            this.updateUpgradeSelection(categoryId, panel);
        });

        // Search functionality
        panel.querySelector('.upgrade-search').addEventListener('input', (e) => {
            const searchTerm = e.target.value;
            const filteredOptions = this.optionsLoader.searchOptions(categoryId, searchTerm);
            this.renderUpgradeOptions(panel, categoryId, filteredOptions);
        });
    }

    /**
     * Render upgrade options
     */
    renderUpgradeOptions(panel, categoryId, options) {
        const listContainer = panel.querySelector('.upgrade-options-list');
        const selectedOptions = this.runFileParser.getUpgradeOptions(categoryId);

        listContainer.innerHTML = '';

        options.forEach(option => {
            const optionItem = document.createElement('div');
            optionItem.className = 'option-item';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = option.name;
            checkbox.id = `${categoryId}-${option.name}`;
            checkbox.checked = selectedOptions.includes(option.name);

            checkbox.addEventListener('change', () => {
                this.updateUpgradeSelection(categoryId, panel);
            });

            const label = document.createElement('label');
            label.className = 'option-label';
            label.htmlFor = `${categoryId}-${option.name}`;

            label.innerHTML = `
                <div class="option-name">${this.escapeHTML(option.name)}</div>
                <div class="option-details">${this.getOptionDetails(option)}</div>
            `;

            optionItem.appendChild(checkbox);
            optionItem.appendChild(label);
            listContainer.appendChild(optionItem);
        });

        // Update selection count
        this.updateSelectionCount(panel, selectedOptions.length);
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHTML(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    /**
     * Get option details string
     */
    getOptionDetails(option) {
        if (!option || !option.characteristics) {
            return 'No details available';
        }

        const chars = option.characteristics;
        const details = [];

        if (chars['u-value']) details.push(`U=${this.escapeHTML(String(chars['u-value']))}`);
        if (chars.panes) details.push(`${this.escapeHTML(String(chars.panes))} panes`);
        if (chars.fill) details.push(`Fill: ${this.escapeHTML(chars.fill)}`);
        if (chars.coat) details.push(`Coat: ${this.escapeHTML(chars.coat)}`);

        return details.join(', ') || 'No details available';
    }

    /**
     * Update upgrade selection
     */
    updateUpgradeSelection(categoryId, panel) {
        const checkboxes = panel.querySelectorAll('input[type="checkbox"]:checked');
        const selected = Array.from(checkboxes).map(cb => cb.value);

        this.runFileParser.setUpgradeOption(categoryId, selected);

        this.updateSelectionCount(panel, selected.length);
        this.updateNavigationBadge(categoryId, selected.length);
        this.updateSummary();
        this.saveToLocalStorage();
    }

    /**
     * Update selection count in panel
     */
    updateSelectionCount(panel, count) {
        const countSpan = panel.querySelector('.upgrade-count');
        if (countSpan) {
            countSpan.textContent = `${count} option${count !== 1 ? 's' : ''} selected`;
        }
    }

    /**
     * Update navigation badge
     */
    updateNavigationBadge(categoryId, count) {
        const badge = document.getElementById(`nav-badge-${categoryId}`);
        if (badge) {
            if (count > 0) {
                badge.textContent = count;
                badge.style.display = 'inline-block';
            } else {
                badge.style.display = 'none';
            }
        }

        // Update nav icon
        const navItem = document.querySelector(`.nav-item[data-section="${categoryId}"]`);
        if (navItem) {
            const icon = navItem.querySelector('.nav-icon');
            if (icon) {
                icon.textContent = count > 0 ? '●' : '○';
            }
        }
    }

    /**
     * Update summary panel
     */
    updateSummary() {
        const config = this.runFileParser.getConfig();

        // Run mode
        document.getElementById('summary-run-mode').textContent = config.runParameters.runMode;

        // Run scope
        document.getElementById('summary-archetypes').textContent = config.runScope.archetypes.length;
        document.getElementById('summary-locations').textContent = config.runScope.locations.length;
        document.getElementById('summary-rulesets').textContent = config.runScope.rulesets.length;

        const baseCount = Math.max(config.runScope.archetypes.length, 1) *
                         Math.max(config.runScope.locations.length, 1) *
                         Math.max(config.runScope.rulesets.length, 1);
        document.getElementById('summary-base-combos').textContent = baseCount;

        // Update navigation badges for scope
        this.updateNavigationBadge('archetypes', config.runScope.archetypes.length);
        this.updateNavigationBadge('locations', config.runScope.locations.length);
        this.updateNavigationBadge('rulesets', config.runScope.rulesets.length);

        // Selected upgrades
        const upgradesDiv = document.getElementById('summary-upgrades');
        upgradesDiv.innerHTML = '';

        let hasSelections = false;
        for (const [category, options] of Object.entries(config.upgrades)) {
            if (options.length > 0 && !(options.length === 1 && options[0] === 'NA')) {
                hasSelections = true;
                const shortName = category.replace('Opt-', '');
                const div = document.createElement('div');
                div.textContent = `${shortName}: ${options.length}`;
                upgradesDiv.appendChild(div);
            }
        }

        if (!hasSelections) {
            upgradesDiv.innerHTML = '<div style="color: #7f8c8d;">No options selected</div>';
        }

        // Calculate simulations
        const calcResult = this.simCalculator.calculate(config);
        document.getElementById('total-sim-count').textContent = calcResult.total.toLocaleString();

        const formula = this.simCalculator.getFormula(calcResult);
        document.getElementById('sim-formula').textContent = formula;
    }

    /**
     * New configuration
     */
    newConfig() {
        if (confirm('Create new configuration? Any unsaved changes will be lost.')) {
            this.runFileParser.setConfig(this.runFileParser.getDefaultConfig());
            this.loadConfigToUI();
            this.updateSummary();
            this.saveToLocalStorage();
            this.setStatus('New configuration created');
        }
    }

    /**
     * Open file dialog
     */
    openFile() {
        document.getElementById('file-input').click();
    }

    /**
     * Handle file selection
     */
    async handleFileSelect(event) {
        const file = event.target.files[0];
        if (!file) return;

        try {
            const content = await file.text();
            const config = this.runFileParser.parse(content);

            this.runFileParser.setConfig(config);
            this.loadConfigToUI();
            this.updateSummary();
            this.saveToLocalStorage();

            this.setStatus(`Loaded: ${file.name}`);
            document.getElementById('status-file').textContent = file.name;

        } catch (error) {
            alert(`Error loading file: ${error.message}`);
        }

        // Reset file input
        event.target.value = '';
    }

    /**
     * Load configuration to UI
     */
    loadConfigToUI() {
        const config = this.runFileParser.getConfig();

        // Run parameters
        document.getElementById('run-mode').value = config.runParameters.runMode;
        document.getElementById('archetype-dir').value = config.runParameters.archetypeDir;
        document.getElementById('unit-costs-db').value = config.runParameters.unitCostsDb;
        document.getElementById('options-file').value = config.runParameters.optionsFile;

        // Archetypes
        document.getElementById('archetypes-input').value = config.runScope.archetypes.join('\n');

        // Locations - repopulate with selections
        this.populateLocations();

        // Rulesets
        document.getElementById('rulesets-input').value = config.runScope.rulesets[0] || 'as-found';

        // Update all navigation badges
        for (const [categoryId, options] of Object.entries(config.upgrades)) {
            this.updateNavigationBadge(categoryId, options.length);
        }
    }

    /**
     * Export .run file (and options if modified)
     */
    exportRunFile() {
        // Check if options have been modified
        if (this.hasModifiedOptions()) {
            this.showExportDialog();
        } else {
            this.doExportRunFile();
        }
    }

    /**
     * Check if options have been modified
     */
    hasModifiedOptions() {
        return this.optionsModified === true;
    }

    /**
     * Show export dialog for options
     */
    showExportDialog() {
        const dialogHTML = `
            <p style="margin-bottom: 20px;">
                You have added new options. How would you like to export the modified HTAP-options.json file?
            </p>
            <div class="export-options">
                <label class="radio-option">
                    <input type="radio" name="export-type" value="update" checked>
                    <span>Update Existing File</span>
                    <small>Download as "HTAP-options.json" (will replace your existing file when moved to data folder)</small>
                </label>
                <label class="radio-option">
                    <input type="radio" name="export-type" value="new">
                    <span>Save as New File</span>
                    <small>Download as "HTAP-options-custom-YYYYMMDD.json" (preserves original file)</small>
                </label>
            </div>
            <p style="margin-top: 20px; font-size: 12px; color: #7f8c8d;">
                Note: The .run file will also be exported after options are saved.
            </p>
        `;

        this.showModal(
            'Export Modified Options',
            dialogHTML,
            () => this.confirmExportOptions(),
            'Export'
        );
    }

    /**
     * Confirm export options choice
     */
    confirmExportOptions() {
        const exportType = document.querySelector('input[name="export-type"]:checked').value;

        if (exportType === 'new') {
            this.exportOptionsAsNew();
        } else {
            this.exportOptionsUpdate();
        }

        // Reset modified flag since we've exported the changes
        this.optionsModified = false;

        // After options are exported, export .run file
        this.doExportRunFile();
    }

    /**
     * Export options as new file with timestamp
     */
    exportOptionsAsNew() {
        const timestamp = new Date().toISOString().split('T')[0].replace(/-/g, '');
        const filename = `HTAP-options-custom-${timestamp}.json`;

        this.exportOptionsFile(filename);
        this.setStatus(`Exported new options file: ${filename}`);
    }

    /**
     * Export options updating existing file name
     */
    exportOptionsUpdate() {
        const filename = 'HTAP-options.json';

        this.exportOptionsFile(filename);
        this.setStatus('Exported updated HTAP-options.json');
    }

    /**
     * Export options file with given filename
     */
    exportOptionsFile(filename) {
        if (!this.optionsLoader || !this.optionsLoader.optionsData) {
            throw new Error('Options data not available for export');
        }

        const optionsData = this.optionsLoader.optionsData;
        const content = JSON.stringify(optionsData, null, 2);

        // Create download
        const blob = new Blob([content], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();

        URL.revokeObjectURL(url);
    }

    /**
     * Export .run file (actual export logic)
     */
    doExportRunFile() {
        const config = this.runFileParser.getConfig();
        const content = this.runFileParser.generate(config);

        // Create download
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = 'htap-config.run';
        a.click();

        URL.revokeObjectURL(url);

        this.setStatus('Run file exported');
    }

    /**
     * Save to localStorage
     */
    saveToLocalStorage() {
        try {
            const config = this.runFileParser.getConfig();
            localStorage.setItem('htap-config', JSON.stringify(config));
        } catch (error) {
            console.error('Failed to save to localStorage:', error);
        }
    }

    /**
     * Load from localStorage
     */
    loadFromLocalStorage() {
        try {
            const saved = localStorage.getItem('htap-config');
            if (saved) {
                const config = JSON.parse(saved);
                this.runFileParser.setConfig(config);
                this.loadConfigToUI();
                this.setStatus('Restored previous session');
            }
        } catch (error) {
            console.error('Failed to load from localStorage:', error);
        }
    }

    /**
     * Set status message
     */
    setStatus(message, isError = false) {
        const statusEl = document.getElementById('status-message');
        statusEl.textContent = message;
        statusEl.style.color = isError ? '#e74c3c' : '#ecf0f1';
    }

    /**
     * Show modal with custom content
     */
    showModal(title, bodyHTML, onConfirm, confirmText = 'Confirm') {
        const overlay = document.getElementById('modal-overlay');
        const modalTitle = document.getElementById('modal-title');
        const modalBody = document.getElementById('modal-body');
        const confirmBtn = document.getElementById('modal-confirm');
        const cancelBtn = document.getElementById('modal-cancel');
        const closeBtn = document.getElementById('modal-close');

        modalTitle.textContent = title;
        modalBody.innerHTML = bodyHTML;
        confirmBtn.textContent = confirmText;
        overlay.style.display = 'flex';

        // Remove old listeners by cloning button
        const newConfirm = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirm, confirmBtn);

        // Set new listener
        newConfirm.addEventListener('click', () => {
            try {
                onConfirm();
                this.hideModal();
            } catch (error) {
                // If onConfirm throws error, don't close modal
                console.error('Modal confirm error:', error);
                alert(`Error: ${error.message}`);
            }
        });

        // Cancel/close listeners
        const closeModal = () => this.hideModal();
        cancelBtn.onclick = closeModal;
        closeBtn.onclick = closeModal;
        overlay.onclick = (e) => {
            if (e.target === overlay) closeModal();
        };

        // ESC key to close modal
        this.modalKeyHandler = (e) => {
            if (e.key === 'Escape') {
                closeModal();
            }
        };
        document.addEventListener('keydown', this.modalKeyHandler);

        // Auto-focus first input field
        setTimeout(() => {
            const firstInput = modalBody.querySelector('input, textarea');
            if (firstInput) firstInput.focus();
        }, 100);
    }

    /**
     * Hide modal
     */
    hideModal() {
        document.getElementById('modal-overlay').style.display = 'none';

        // Remove keyboard event listener
        if (this.modalKeyHandler) {
            document.removeEventListener('keydown', this.modalKeyHandler);
            this.modalKeyHandler = null;
        }
    }

    /**
     * Handle "Add New Option" button click
     */
    handleAddNewOption(categoryId) {
        if (!this.optionsLoader || !this.optionsLoader.categories) {
            alert('Options data not loaded');
            return;
        }

        const category = this.optionsLoader.categories.find(cat => cat.id === categoryId);
        if (!category) {
            alert(`Category "${categoryId}" not found`);
            return;
        }

        // Get existing options, pick one with most fields as template
        const options = this.optionsLoader.getOptionsForCategory(categoryId);
        const templateOption = this.selectBestTemplate(options);

        if (!templateOption || !templateOption.data) {
            alert('No existing options available to use as template');
            return;
        }

        // Generate form with all options for template selector
        const formHTML = FormBuilder.createOptionForm(templateOption, options, categoryId);

        // Show modal
        this.showModal(
            `Add New Option to ${category.displayName}`,
            formHTML,
            () => this.confirmAddOption(categoryId),
            'Add Option'
        );

        // Add event listener for template selector change
        this.setupTemplateSelector(categoryId, options);
    }

    /**
     * Setup template selector event listener
     */
    setupTemplateSelector(categoryId, allOptions) {
        const selector = document.getElementById('template-selector');
        if (!selector) return;

        selector.addEventListener('change', (e) => {
            const selectedOptionName = e.target.value;
            const selectedOption = allOptions.find(opt => opt.name === selectedOptionName);

            if (!selectedOption) return;

            // Save current option name (user might have started typing)
            const currentName = document.getElementById('opt-name')?.value || '';

            // Regenerate form with new template
            const newFormHTML = FormBuilder.createOptionForm(selectedOption, allOptions, categoryId);
            const modalBody = document.getElementById('modal-body');
            modalBody.innerHTML = newFormHTML;

            // Restore option name if user had entered something
            if (currentName) {
                const nameInput = document.getElementById('opt-name');
                if (nameInput) nameInput.value = currentName;
            }

            // Re-attach the template selector listener (since we regenerated the form)
            this.setupTemplateSelector(categoryId, allOptions);
        });
    }

    /**
     * Select option with most fields to use as template
     */
    selectBestTemplate(options) {
        if (options.length === 0) return null;

        // Exclude 'NA' if possible
        const filtered = options.filter(opt => opt.name !== 'NA');
        const candidates = filtered.length > 0 ? filtered : options;

        // Pick one with most characteristics + h2kMap fields
        return candidates.reduce((best, opt) => {
            const charCount = Object.keys(opt.data.characteristics || {}).length;
            const h2kCount = Object.keys(opt.data.h2kMap?.base || {}).length;
            const totalCount = charCount + h2kCount;

            const bestCharCount = Object.keys(best.data.characteristics || {}).length;
            const bestH2kCount = Object.keys(best.data.h2kMap?.base || {}).length;
            const bestTotalCount = bestCharCount + bestH2kCount;

            return totalCount > bestTotalCount ? opt : best;
        }, candidates[0]);
    }

    /**
     * Confirm and add new option
     */
    confirmAddOption(categoryId) {
        const form = document.getElementById('new-option-form');

        if (!form) {
            throw new Error('Form not found');
        }

        const optionData = FormBuilder.extractFormData(form);

        // Check for duplicate name
        const category = this.optionsLoader.categories.find(cat => cat.id === categoryId);
        if (!category) {
            throw new Error(`Category "${categoryId}" not found`);
        }

        if (category.options && category.options[optionData.name]) {
            throw new Error(`Option "${optionData.name}" already exists in ${category.displayName}`);
        }

        // Build option object (only include non-empty sections)
        const newOption = {};

        if (Object.keys(optionData.characteristics).length > 0) {
            newOption.characteristics = optionData.characteristics;
        }

        if (optionData.h2kMap) {
            newOption.h2kMap = optionData.h2kMap;
        }

        if (optionData.costs) {
            newOption.costs = optionData.costs;
        }

        // Add to optionsData (in-memory)
        this.optionsLoader.optionsData[categoryId].options[optionData.name] = newOption;

        // Update category cache
        category.options[optionData.name] = newOption;

        // Re-parse categories to ensure everything is in sync
        this.optionsLoader.parseCategories();

        // Re-render panel with updated options
        const panel = document.getElementById(`panel-${categoryId}`);
        if (panel) {
            const updatedOptions = this.optionsLoader.getOptionsForCategory(categoryId);
            this.renderUpgradeOptions(panel, categoryId, updatedOptions);
        }

        // Set modified flag
        this.optionsModified = true;

        // Show success message
        this.setStatus(`Added new option: ${optionData.name} to ${category.displayName}`);
    }
}

// Initialize the app
const app = new HTAPConfigApp();
