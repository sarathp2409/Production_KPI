# Auto-Collated Books Plan

## Goal
Allow users to define 0..N groups of auto-collated books in the pagination create form. Each group is a multi-select of book names chosen in the form, captured as JSON for backend parsing.

## Execution Plan
1. Review current pagination create flow
   - Open `pagination_dash/templates/pagination_dash/pagination_form.html`.
   - Inspect any linked JS to understand book selection UI, section ordering, and submit mechanics.
2. Locate backend entrypoint
   - Find the view/form/model that handles form submission.
   - Identify where to add a new field for auto-collated groups.
3. Define data contract
   - Hidden input containing JSON array of arrays, e.g. `[["TOI B-2","TIMS B-1"],["TIMS B-2","TOI Supp-1"]]`.
   - Constraints: only books selected in the form; allow empty overall; ignore empty groups.
4. Design UI section
   - Insert between Extra Miles and Competitor Data.
   - Header + helper text; Add Group button.
   - Each group row: multi-select of book names + Remove Group control.
5. Implement frontend behavior
   - Sync group options with the selected books list.
   - Serialize groups to hidden input on change/submit.
   - Prevent empty groups; optionally dedupe within a group.
6. Update backend parsing/storage
   - Parse JSON safely.
   - Validate membership against selected books.
   - Persist to model/JSONField or related table; support edit/view if needed.
7. Add validation/tests
   - 0 groups works.
   - 1+ groups works.
   - Malformed JSON handled gracefully.
   - Document assumptions where appropriate.
