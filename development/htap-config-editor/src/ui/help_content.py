"""
Help content for HTAP Configuration Editor

Provides contextual help text for all major features and concepts.
"""

import streamlit as st


# ============================================================================
# HELP TEXT DICTIONARY
# ============================================================================

HELP_TEXT = {
    "archetypes": """
    ### 🏠 What are Archetypes?

    **Archetypes** are baseline building models in HOT2000 format (.h2k files) that represent typical housing configurations.

    **Key Points:**
    - Each archetype defines a complete building: geometry, envelope, HVAC, location, etc.
    - HTAP modifies archetypes by applying option choices to create variations
    - Multiple archetypes allow comparing different building types (e.g., detached vs. townhouse)

    **Location:**
    - Default archetype directory: `C:/HTAP/archetypes/`
    - Common archetypes: `AB-base.h2k`, `BC-base.h2k`, `ON-base.h2k`

    **Tips:**
    - Start with one archetype to keep run times manageable
    - Use region-specific archetypes (AB, BC, ON) for better accuracy
    - Archetype files must be copied to `C:/H2K-CLI-Min/User/` before running simulations
    """,

    "location": """
    ### 📍 What is Location?

    **Location** determines the weather data used for energy simulations.

    **Key Points:**
    - HOT2000 includes weather files for 100+ Canadian locations
    - Weather affects heating/cooling loads, solar gains, and energy consumption
    - Different locations have different temperature profiles, solar radiation, and wind patterns

    **Common Locations:**
    - **Vancouver-BC**: Mild, wet climate (heating dominated)
    - **Toronto-ON**: Cold winters, hot summers (heating & cooling)
    - **Calgary-AB**: Cold, dry climate (high heating loads)

    **Tips:**
    - Choose location that matches your project region
    - Location affects cost-effectiveness of efficiency measures
    - For parametric studies, you can test multiple locations to see regional differences
    """,

    "ruleset": """
    ### 📏 What is a Ruleset?

    **Rulesets** define building code compliance requirements and reference configurations.

    **Common Rulesets:**
    - **as-found**: No code requirements, analyze building as-is
    - **NBC-9.36**: National Building Code of Canada Section 9.36 (energy efficiency)
    - **BC-Step-3**: BC Step Code Step 3 requirements

    **How Rulesets Work:**
    - Rulesets can constrain options (e.g., minimum insulation levels)
    - HTAP applies ruleset requirements when processing options
    - Some rulesets define baseline configurations for comparison

    **Tips:**
    - Use `as-found` for analyzing existing buildings or custom configurations
    - Use `NBC-9.36` for new construction compliance studies
    - BC Step Code rulesets are specific to British Columbia projects
    """,

    "cost_source": """
    ### 💰 What is Cost Source?

    **Cost sources** are regional cost databases containing material and labour costs for building components.

    **Key Points:**
    - Different regions have different material and labour costs
    - Cost sources include costs for insulation, windows, HVAC equipment, etc.
    - Some cost sources inherit from others (e.g., regional sources extend national defaults)

    **Common Sources:**
    - **LEEP-ON-Ottawa**: Ontario/Ottawa region costs
    - **LEEP-AB-Calgary**: Alberta/Calgary region costs
    - **LEEP-BC-Vancouver**: BC/Vancouver region costs

    **Cost Components:**
    - Material costs (e.g., $/m² for insulation)
    - Labour costs (installation)
    - Equipment costs (HVAC, DHW systems)

    **Tips:**
    - Choose cost source that matches your project region for accurate cost estimates
    - Cost estimates are incremental (cost difference vs. baseline)
    - Review cost summary to understand cost breakdown by component
    """,

    "multi_select": """
    ### 🔀 Multi-Select Options (Parametric Runs)

    **Multi-select** allows choosing multiple options for a single attribute, creating parametric studies.

    **How It Works:**
    - Select multiple options for any attribute (e.g., 3 wall types, 2 window types)
    - HTAP generates all combinations automatically
    - Each combination runs as a separate simulation

    **Example:**
    - 3 wall types × 2 window types = **6 simulations**
    - 3 walls × 2 windows × 2 heating systems = **12 simulations**

    **Combination Calculation:**
    ```
    Total runs = archetypes × locations × (option1 × option2 × ... × optionN)
    ```

    **Tips:**
    - Start small: A few options create manageable run sets
    - Watch total combinations: 100+ runs take significant time
    - Use multi-select to compare options (e.g., which wall insulation is most cost-effective?)

    **Warnings:**
    - ⚠️ >100 combinations: May take hours to complete
    - ⚠️ >500 combinations: May be impractical, consider sampling
    """,

    "export_validation": """
    ### ✅ Export Validation

    **Export validation** checks your configuration before generating the .run file.

    **Validation Levels:**
    - **🔴 Errors**: Must be fixed before export (e.g., missing required fields)
    - **🟡 Warnings**: Can export with caution (e.g., large number of runs)
    - **🔵 Info**: Helpful information (e.g., configuration summary)

    **Common Errors:**
    - No archetypes selected
    - No location selected
    - No options selected
    - Invalid option combinations

    **Common Warnings:**
    - Large number of combinations (>100 runs)
    - Missing cost database (costs won't be calculated)
    - Unusual option combinations

    **Tips:**
    - Review validation details before exporting
    - Fix all errors before attempting export
    - Consider warnings carefully - they may indicate configuration issues
    - Export is disabled until all errors are resolved
    """,

    "run_modes": """
    ### ⚙️ Run Modes

    **Run modes** determine how HTAP processes your configuration.

    **Available Modes:**
    - **mesh**: Generate all combinations of options (full factorial)
    - **parametric**: Systematic variation (one-at-a-time)
    - **sample**: Random sampling of combination space

    **Mesh Mode (Default):**
    - Tests every combination of selected options
    - Most comprehensive, but can generate many runs
    - Best for thorough analysis and optimization

    **Parametric Mode:**
    - Varies options systematically
    - Fewer runs than mesh mode
    - Good for understanding individual option impacts

    **Sample Mode:**
    - Randomly samples the combination space
    - Useful for very large combination spaces
    - Provides statistical overview with fewer runs

    **Tips:**
    - Use **mesh** for small to medium studies (<100 combinations)
    - Use **parametric** for sensitivity analysis
    - Use **sample** for large combination spaces (>500 combinations)
    """,

    "advanced_parameters": """
    ### ⚙️ Advanced Parameters

    **Advanced parameters** customize the run environment and output settings.

    **Key Parameters:**
    - **Archetype Directory**: Where to find .h2k archetype files
    - **Options File**: HTAP options definition file
    - **Unit Costs Database**: Cost data for options
    - **Output Folder**: Where to save simulation results

    **Default Values:**
    - Archetype Directory: `C:/HTAP/archetypes`
    - Options File: `C:/HTAP/HTAP-options.json`
    - Unit Costs Database: `C:/HTAP/HTAPUnitCosts.json`
    - Output Folder: `./output`

    **Tips:**
    - Use default values unless you have a specific reason to change them
    - Custom archetype directories allow organizing projects separately
    - Custom options files enable project-specific option sets
    """,

    "cost_summary": """
    ### 💰 Cost Summary

    **Cost summary** shows estimated costs for selected options compared to baseline.

    **What It Shows:**
    - Total estimated cost for all selected options
    - Cost breakdown by option category
    - Component-level costs (materials, labour, equipment)

    **Cost Calculation:**
    - Costs are **incremental** (vs. baseline/reference option)
    - Based on regional cost database (material + labour)
    - Includes applicable cost components for each option

    **Understanding Costs:**
    - **Positive costs**: Option is more expensive than baseline
    - **Negative costs**: Option is less expensive (or cost savings)
    - **$0 costs**: Same cost as baseline, or no cost data available

    **Tips:**
    - Cost summary helps prioritize cost-effective options
    - Review component breakdown to understand where costs come from
    - Costs are estimates - actual costs may vary
    - Some options may not have cost data (shown as "Cost data not available")
    """,
}


# ============================================================================
# HELP DISPLAY FUNCTION
# ============================================================================

def show_help_button(key: str, label: str = "❓ Help") -> None:
    """
    Display help text in an expandable section

    Args:
        key: Key to look up in HELP_TEXT dictionary
        label: Label for the help button/expander (default: "❓ Help")

    Usage:
        show_help_button("archetypes")
        show_help_button("cost_source", label="💡 What's this?")
    """
    if key not in HELP_TEXT:
        st.warning(f"No help text available for: {key}")
        return

    with st.expander(label):
        st.markdown(HELP_TEXT[key])


def show_inline_help(key: str) -> None:
    """
    Display help text inline (without expander)

    Args:
        key: Key to look up in HELP_TEXT dictionary

    Usage:
        show_inline_help("archetypes")
    """
    if key not in HELP_TEXT:
        st.warning(f"No help text available for: {key}")
        return

    st.markdown(HELP_TEXT[key])


def get_help_text(key: str) -> str:
    """
    Get help text for a given key

    Args:
        key: Key to look up in HELP_TEXT dictionary

    Returns:
        Help text string, or empty string if key not found
    """
    return HELP_TEXT.get(key, "")
