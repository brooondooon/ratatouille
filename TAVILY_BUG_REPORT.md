# Tavily Extract API Bug Report

## Issue Summary
While building Ratatouille, I discovered that the Tavily Extract API is missing critical structured content (ingredient lists) when extracting from recipe websites, specifically Food Network.

## Reproduction Steps

1. Call Tavily Extract API on this URL:
   ```
   https://www.foodnetwork.com/recipes/food-network-kitchen/steak-with-red-wine-shallot-sauce-recipe-1972846
   ```

2. Use either `extract_depth="basic"` or `extract_depth="advanced"`

3. Examine the extracted content between the `## Ingredients` and `## Directions` headers

## Expected Behavior

The extracted content should include the ingredient list that appears on the webpage:
- 1 1-pound New York strip steak (about 1-inch thick)
- Kosher salt and freshly ground pepper
- 1 large shallot, minced
- 3/4 cup boxed red wine
- 2 to 3 tablespoons cold unsalted butter, cubed

## Actual Behavior

The Extract API returns:
```markdown
## Ingredients

[View Shopping List](...)   [Ingredient Substitutions](...)

NEW: You can now switch to Cook Mode to keep your screen awake.

## Directions

1. Remove the steak from the refrigerator...
```

**The ingredient bullet list is completely missing** from the extracted content. The API jumps directly from the `## Ingredients` header to the `## Directions` section, skipping all 5 ingredients.

## Impact on My Application

This caused my LLM-based cooking guide feature to generate incorrect ingredients. When the LLM receives content with an "## Ingredients" header followed immediately by directions, it has no ingredient data to work with.

In my case, the extracted content included navigation menu items earlier in the page (Chicken, Turkey, Beef, Pork, Fish, etc.), which the LLM mistakenly interpreted as the recipe ingredients since they appeared under a different "## Ingredients" heading (from the site navigation).

## Verification

I saved the full extracted content and verified:
- ✗ "strip steak" - NOT FOUND in 16,113 characters of extracted content
- ✗ "shallot, minced" - NOT FOUND
- ✗ "boxed red wine" - NOT FOUND
- ✗ "unsalted butter" - NOT FOUND

The directions ARE properly extracted, confirming that the Extract API can see this part of the page, but somehow the structured list between the headers is being skipped.

## Hypothesis

It appears the Extract API may have issues extracting certain types of structured HTML lists or dynamic content that appears between semantic headers on recipe sites. This might be related to how the HTML is structured on Food Network's pages.

## Workaround I'm Using

For now, I've updated my LLM prompts to be more resilient when ingredient data is missing, and I'm working on detecting when extractions are incomplete so I can show a helpful error message to users.

## Additional Context

- This is a critical issue for recipe-based applications
- Tested with both `basic` and `advanced` extract depths - same result
- The Extract API works fine for other parts of the page (navigation, directions, etc.)
- I'm using this for a cooking assistant app that relies on accurate recipe extraction

Happy to provide more details or test additional URLs if helpful!
