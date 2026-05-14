/**
 * FormBuilder - Generate dynamic forms for options
 */
class FormBuilder {
    /**
     * Escape HTML to prevent XSS attacks
     */
    static escapeHTML(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    /**
     * Create form for new option based on template
     * @param {Object} templateOption - Full option object {name, data, ...}
     * @param {Array} allOptions - All available options in category
     * @param {String} categoryId - Category identifier
     * @returns {String} HTML string for form
     */
    static createOptionForm(templateOption, allOptions, categoryId) {
        // Extract the actual data from the template option
        const templateData = templateOption.data || templateOption;
        const fields = this.extractFields(templateData);

        let html = '<form id="new-option-form" class="option-form">';

        // Template selector dropdown
        html += `
            <div class="form-group">
                <label for="template-selector">Template Option</label>
                <select id="template-selector" class="form-control">
        `;

        // Populate dropdown with all options
        allOptions.forEach(opt => {
            const selected = opt.name === templateOption.name ? 'selected' : '';
            html += `<option value="${this.escapeHTML(opt.name)}" ${selected}>${this.escapeHTML(opt.name)}</option>`;
        });

        html += `
                </select>
                <small class="form-hint">Select an existing option to use as a starting template</small>
            </div>
        `;

        // Option name (required)
        html += `
            <div class="form-group">
                <label for="opt-name">Option Name <span class="required">*</span></label>
                <input type="text" id="opt-name" class="form-control" required
                       aria-required="true"
                       pattern="[a-zA-Z0-9._-]+"
                       placeholder="e.g., NC-3g-HG-u1.00">
                <small class="form-hint">Unique identifier for this option (alphanumeric, dots, dashes, underscores only)</small>
            </div>
        `;

        // Characteristics (optional, common fields)
        if (fields.characteristics && Object.keys(fields.characteristics).length > 0) {
            html += '<h4>Characteristics (Optional)</h4>';
            html += '<small class="form-hint">Technical specifications for this option. Leave blank to keep template values.</small>';

            for (const [key, value] of Object.entries(fields.characteristics)) {
                const inputType = typeof value === 'number' ? 'number' : 'text';
                const step = typeof value === 'number' ? 'step="0.01"' : '';
                const escapedKey = this.escapeHTML(key);
                const escapedValue = this.escapeHTML(String(value));
                const escapedLabel = this.escapeHTML(this.formatLabel(key));
                html += `
                    <div class="form-group">
                        <label for="char-${escapedKey}">${escapedLabel}</label>
                        <input type="${inputType}" id="char-${escapedKey}" class="form-control"
                               value="${escapedValue}" ${step} placeholder="${escapedValue}">
                    </div>
                `;
            }
        }

        // h2kMap (show simplified editor)
        if (fields.h2kMap) {
            html += '<h4>HOT2000 Mappings (Optional)</h4>';
            html += '<small class="form-hint">HOT2000 XML tag mappings. Edit JSON below to customize or leave as-is.</small>';
            const escapedJSON = this.escapeHTML(JSON.stringify(fields.h2kMap, null, 2));
            html += `
                <div class="form-group">
                    <label for="h2k-map">H2K Map (JSON)</label>
                    <textarea id="h2k-map" class="form-control code-input" rows="8">${escapedJSON}</textarea>
                </div>
            `;
        }

        // Costs (optional)
        if (fields.costs) {
            html += '<h4>Costs (Optional)</h4>';
            html += '<small class="form-hint">Cost components for this option. Edit JSON below or leave as-is.</small>';
            const escapedJSON = this.escapeHTML(JSON.stringify(fields.costs, null, 2));
            html += `
                <div class="form-group">
                    <label for="costs-data">Cost Components (JSON)</label>
                    <textarea id="costs-data" class="form-control code-input" rows="6">${escapedJSON}</textarea>
                </div>
            `;
        }

        html += '</form>';
        return html;
    }

    /**
     * Extract field structure from template option
     */
    static extractFields(templateOption) {
        const fields = {};

        if (templateOption.characteristics) {
            fields.characteristics = { ...templateOption.characteristics };
        }

        if (templateOption.h2kMap) {
            fields.h2kMap = JSON.parse(JSON.stringify(templateOption.h2kMap));
        }

        if (templateOption.costs) {
            fields.costs = JSON.parse(JSON.stringify(templateOption.costs));
        }

        return fields;
    }

    /**
     * Validate and extract form data
     */
    static extractFormData(formElement) {
        const data = {
            name: document.getElementById('opt-name').value.trim(),
            characteristics: {},
            h2kMap: null,
            costs: null
        };

        if (!data.name) {
            throw new Error('Option name is required');
        }

        // Validate option name pattern
        const pattern = /^[a-zA-Z0-9._-]+$/;
        if (!pattern.test(data.name)) {
            throw new Error('Option name can only contain letters, numbers, dots, dashes, and underscores');
        }

        // Extract characteristics
        const charInputs = formElement.querySelectorAll('[id^="char-"]');
        charInputs.forEach(input => {
            const key = input.id.replace('char-', '');
            let value = input.value.trim();

            if (value !== '') {
                // Auto-detect number
                if (input.type === 'number') {
                    value = parseFloat(value);
                }
                data.characteristics[key] = value;
            }
        });

        // Extract h2kMap (JSON)
        const h2kMapEl = document.getElementById('h2k-map');
        if (h2kMapEl && h2kMapEl.value.trim() !== '') {
            try {
                data.h2kMap = JSON.parse(h2kMapEl.value);
            } catch (e) {
                const errorMsg = this.formatJSONError(e, h2kMapEl.value);
                throw new Error('Invalid JSON in H2K Map:\n' + errorMsg);
            }
        }

        // Extract costs (JSON)
        const costsEl = document.getElementById('costs-data');
        if (costsEl && costsEl.value.trim() !== '') {
            try {
                data.costs = JSON.parse(costsEl.value);
            } catch (e) {
                const errorMsg = this.formatJSONError(e, costsEl.value);
                throw new Error('Invalid JSON in Costs:\n' + errorMsg);
            }
        }

        return data;
    }

    /**
     * Format label from key (convert camelCase and snake_case to Title Case)
     */
    static formatLabel(key) {
        return key
            .replace(/-/g, ' ')
            .replace(/_/g, ' ')
            .replace(/([A-Z])/g, ' $1')
            .replace(/^./, str => str.toUpperCase())
            .trim();
    }

    /**
     * Format JSON error with helpful context
     */
    static formatJSONError(error, jsonString) {
        const msg = error.message;

        // Try to extract position if available
        const posMatch = msg.match(/position (\d+)/);
        if (posMatch) {
            const pos = parseInt(posMatch[1]);
            const lines = jsonString.substring(0, pos).split('\n');
            const lineNum = lines.length;
            const colNum = lines[lines.length - 1].length + 1;
            return `${msg} (near line ${lineNum}, column ${colNum})`;
        }

        return msg;
    }
}
