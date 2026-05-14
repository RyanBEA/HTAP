/**
 * SimCalculator - Calculate total simulation count for parametric runs
 */
class SimCalculator {
    constructor() {
        // Calculator instance
    }

    /**
     * Calculate total number of simulations
     * Formula: archetypes × locations × rulesets × (product of multi-select options)
     */
    calculate(config) {
        // Base combinations
        const archetypesCount = Math.max(config.runScope.archetypes.length, 1);
        const locationsCount = Math.max(config.runScope.locations.length, 1);
        const rulesetsCount = Math.max(config.runScope.rulesets.length, 1);

        let baseCount = archetypesCount * locationsCount * rulesetsCount;

        // Upgrades multiplier
        let upgradesMultiplier = 1;
        const upgradeFactors = [];

        for (const [category, options] of Object.entries(config.upgrades)) {
            if (options && options.length > 1) {
                // Only count if more than one option selected (parametric variation)
                upgradesMultiplier *= options.length;
                upgradeFactors.push({
                    category: category,
                    count: options.length
                });
            }
        }

        const totalCount = baseCount * upgradesMultiplier;

        return {
            total: totalCount,
            base: baseCount,
            archetypes: archetypesCount,
            locations: locationsCount,
            rulesets: rulesetsCount,
            upgradesMultiplier: upgradesMultiplier,
            upgradeFactors: upgradeFactors
        };
    }

    /**
     * Get human-readable breakdown formula
     */
    getFormula(calcResult) {
        const parts = [];

        // Base factors
        if (calcResult.archetypes > 1) {
            parts.push(`${calcResult.archetypes} archetypes`);
        }
        if (calcResult.locations > 1) {
            parts.push(`${calcResult.locations} locations`);
        }
        if (calcResult.rulesets > 1) {
            parts.push(`${calcResult.rulesets} rulesets`);
        }

        // Upgrade factors
        for (const factor of calcResult.upgradeFactors) {
            const shortName = factor.category.replace('Opt-', '');
            parts.push(`${factor.count} ${shortName}`);
        }

        if (parts.length === 0) {
            return '1 simulation';
        }

        // Build formula
        const numbers = [];

        if (calcResult.archetypes > 1) numbers.push(calcResult.archetypes);
        if (calcResult.locations > 1) numbers.push(calcResult.locations);
        if (calcResult.rulesets > 1) numbers.push(calcResult.rulesets);

        for (const factor of calcResult.upgradeFactors) {
            numbers.push(factor.count);
        }

        const formula = numbers.join(' × ');

        return formula;
    }

    /**
     * Get warning message if simulation count is large
     */
    getWarning(calcResult) {
        if (calcResult.total > 5000) {
            return 'Very large run! This will take significant time to complete.';
        } else if (calcResult.total > 1000) {
            return 'Large run. Consider reducing the number of options.';
        }
        return null;
    }

    /**
     * Estimate runtime
     * Assumes ~60 seconds per simulation, divided by thread count
     */
    estimateRuntime(totalSimulations, threadCount = 7, secondsPerSim = 60) {
        const totalSeconds = (totalSimulations * secondsPerSim) / threadCount;

        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);

        if (hours > 0) {
            return `~${hours}h ${minutes}m`;
        } else {
            return `~${minutes}m`;
        }
    }
}
